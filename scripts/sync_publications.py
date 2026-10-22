#!/usr/bin/env python3
"""Sync publications into content/publications/.

Your ORCID record lists your papers by DOI, so no name matching is needed;
Crossref (the official DOI registry) fills in the full date, volume, issue,
pages and abstract for each DOI. Existing files are never overwritten, so
manual edits (featured, equal_contribution, ...) are safe.

Usage (run from the website folder):
  python3 scripts/sync_publications.py              # add new papers from ORCID
  python3 scripts/sync_publications.py --dry-run    # only show what would happen
  python3 scripts/sync_publications.py --doi 10.1126/sciadv.aee5269
                                                    # add one paper by DOI
  python3 scripts/sync_publications.py --fill-missing
                                                    # fill empty doi/volume/issue/pages in existing files
  python3 scripts/sync_publications.py --scholar    # also look on Google Scholar for papers missing from ORCID
"""
import argparse
import difflib
import html as html_lib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# https://orcid.org/0000-0002-2977-2392
ORCID_ID = "0000-0002-2977-2392"
# Target Scholar Citations profile (only used with --scholar)
SCHOLAR_USER_ID = "HhNqllUAAAAJ"
PUBLICATIONS_DIR = "content/publications"

# Only for --scholar / --fill-missing title lookups (ORCID papers are matched by DOI):
# a Crossref match is accepted only if one of its authors' names contains this
# (Crossref may store the family name as "Bhuiyan" or "Ahmad Razin Bhuiyan")
MY_FAMILY_NAME = "Bhuiyan"
# ...and its title is at least this similar to the Scholar title (0-1)
TITLE_MATCH_THRESHOLD = 0.9

# Crossref also registers peer-review reports, figures, etc.; only these count as papers
CROSSREF_TYPES = ['journal-article', 'posted-content', 'proceedings-article', 'book-chapter']

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
CROSSREF_USER_AGENT = 'zarifrazin.github.io publication sync (https://zarifrazin.github.io)'

# Keyword dictionary for auto-tagging
TAG_KEYWORDS = {
    'molecular dynamics': 'Molecular Dynamics',
    'lammps': 'LAMMPS',
    'heat transfer': 'Heat Transfer',
    'thermal': 'Thermal Transport',
    'wettability': 'Wettability',
    'nano-confined': 'Nano-scale',
    'polymer': 'Polymers',
    'simulation': 'Simulation',
    'heat capacity': 'Specific Heat',
    'flame': 'Flame Retardancy',
    'perovskite': 'Perovskites'
}

class ScholarListParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_row = False
        self.in_title = False
        self.in_authors = False
        self.in_source = False
        self.in_year = False

        self.current_paper = {}
        self.papers = []

        self.gs_gray_count = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'tr' and 'gsc_a_tr' in attrs_dict.get('class', ''):
            self.in_row = True
            self.current_paper = {'title': '', 'authors': '', 'source': '', 'year': '', 'citation_id': ''}
            self.gs_gray_count = 0

        elif self.in_row:
            if tag == 'a' and 'gsc_a_at' in attrs_dict.get('class', ''):
                self.in_title = True
                href = attrs_dict.get('href', '')
                m = re.search(r'citation_for_view=([^&]+)', href)
                if m:
                    self.current_paper['citation_id'] = m.group(1)
            elif tag == 'div' and 'gs_gray' in attrs_dict.get('class', ''):
                self.gs_gray_count += 1
                if self.gs_gray_count == 1:
                    self.in_authors = True
                elif self.gs_gray_count == 2:
                    self.in_source = True
            # The year is in <td class="gsc_a_y"><span class="gsc_a_h ...">2024</span></td>
            elif tag == 'span' and 'gsc_a_h' in attrs_dict.get('class', ''):
                self.in_year = True

    def handle_endtag(self, tag):
        if tag == 'tr' and self.in_row:
            self.in_row = False
            self.papers.append(self.current_paper)
        elif self.in_row:
            if tag == 'a' and self.in_title:
                self.in_title = False
            elif tag == 'div':
                if self.in_authors:
                    self.in_authors = False
                elif self.in_source:
                    self.in_source = False
            elif tag == 'span' and self.in_year:
                self.in_year = False

    def handle_data(self, data):
        if self.in_row:
            if self.in_title:
                self.current_paper['title'] += data
            elif self.in_authors:
                self.current_paper['authors'] += data
            elif self.in_source:
                self.current_paper['source'] += data
            elif self.in_year:
                self.current_paper['year'] += data


class ScholarDetailParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_field = False
        self.in_value = False

        self.title = ''
        self.current_field = ''
        self.metadata = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'div' and attrs_dict.get('id') == 'gsc_oci_title':
            self.in_title = True
        elif tag == 'div' and attrs_dict.get('class') == 'gsc_oci_field':
            self.in_field = True
        elif tag == 'div' and attrs_dict.get('class') == 'gsc_oci_value':
            self.in_value = True

    def handle_endtag(self, tag):
        if self.in_title and tag == 'div':
            self.in_title = False
        elif self.in_field and tag == 'div':
            self.in_field = False
        elif self.in_value and tag == 'div':
            self.in_value = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_field:
            self.current_field = data.strip().lower()
        elif self.in_value:
            if self.current_field:
                self.metadata[self.current_field] = self.metadata.get(self.current_field, '') + data


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text


def fetch_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode('utf-8')


def fetch_json(url, retries=4):
    """Crossref rate-limits bursts of requests (HTTP 429); wait and retry."""
    req = urllib.request.Request(url, headers={'User-Agent': CROSSREF_USER_AGENT, 'Accept': 'application/json'})
    for attempt in range(retries):
        time.sleep(1)  # stay well under Crossref's public rate limit
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or attempt == retries - 1:
                raise
            wait = int(e.headers.get('Retry-After') or 5 * (attempt + 1))
            print(f"  Crossref busy (HTTP {e.code}); retrying in {wait}s...")
            time.sleep(wait)


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def strip_tags(text):
    """Crossref titles/abstracts can contain HTML or JATS tags (<i>, <jats:p>, ...)."""
    return clean_text(html_lib.unescape(re.sub(r'<[^>]+>', ' ', text)))


def yaml_str(text):
    return text.replace('\\', '\\\\').replace('"', '\\"')


def format_author_ieee(name):
    name = name.strip()
    if not name:
        return ""
    words = name.split()
    if len(words) == 1:
        return words[0]

    last_name = words[-1]
    initials = []
    for word in words[:-1]:
        # remove punctuation if any
        word = re.sub(r'[.,\/#!$%\^&\*;:{}=\-_`~()]', '', word)
        if not word:
            continue
        if word.isupper() and len(word) > 1:
            for char in word:
                initials.append(f"{char}.")
        else:
            initials.append(f"{word[0].upper()}.")

    if initials:
        return f"{' '.join(initials)} {last_name}"
    else:
        return last_name


def format_authors_list_ieee(authors):
    formatted = [format_author_ieee(a) for a in authors]
    if len(formatted) == 0:
        return ""
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    return ", ".join(formatted[:-1]) + ", and " + formatted[-1]


def normalize_title(title):
    return re.sub(r'[^a-z0-9]+', ' ', title.lower()).strip()


def crossref_record(item):
    """Convert a Crossref work into the fields used in the publication front matter."""
    authors = [clean_text(f"{a.get('given', '')} {a.get('family', '')}") for a in item.get('author', [])]
    parts = (item.get('published') or item.get('issued') or {}).get('date-parts', [[None]])[0]
    date_str = ""
    if parts and parts[0]:
        date_str = f"{parts[0]}-{str(parts[1] if len(parts) > 1 else 1).zfill(2)}-{str(parts[2] if len(parts) > 2 else 1).zfill(2)}"
    journal = (item.get('container-title') or [''])[0]
    is_preprint = item.get('type') == 'posted-content' or 'arxiv' in journal.lower()
    return {
        'title': strip_tags((item.get('title') or [''])[0]),
        'authors': authors,
        'date': date_str,
        'journal': strip_tags(journal),
        'volume': item.get('volume', ''),
        'issue': item.get('issue', ''),
        'pages': item.get('page', '') or item.get('article-number', ''),
        'publisher': item.get('publisher', ''),
        'doi': item.get('DOI', ''),
        'type': 'preprint' if is_preprint else 'journal',
        'abstract': strip_tags(re.sub(r'<jats:title>.*?</jats:title>', '', item.get('abstract', ''))),
    }


def crossref_by_doi(doi):
    doi = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:)', '', doi.strip(), flags=re.I)
    data = fetch_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    return crossref_record(data['message'])


def crossref_by_title(title):
    """Find a paper on Crossref by title. Returns None unless the match is unambiguous."""
    query = urllib.parse.urlencode({
        'query.bibliographic': title,
        'query.author': MY_FAMILY_NAME,
        'filter': ','.join(f'type:{t}' for t in CROSSREF_TYPES),
        'rows': 5,
    })
    try:
        items = fetch_json(f"https://api.crossref.org/works?{query}")['message']['items']
    except Exception as e:
        print(f"  Crossref lookup failed: {e}")
        return None
    best, best_similarity = None, 0
    for item in items:
        candidate = strip_tags((item.get('title') or [''])[0])
        # "Correction: <title>" notices are near-identical to the paper's title
        if re.match(r'(correction|erratum|corrigendum|retraction|expression of concern)\b', candidate, flags=re.I):
            continue
        similarity = difflib.SequenceMatcher(None, normalize_title(title), normalize_title(candidate)).ratio()
        is_mine = any(MY_FAMILY_NAME.lower() in f"{a.get('given', '')} {a.get('family', '')}".lower()
                      for a in item.get('author', []))
        if similarity >= TITLE_MATCH_THRESHOLD and is_mine and similarity > best_similarity:
            best, best_similarity = item, similarity
    return crossref_record(best) if best else None


def orcid_works():
    """All works on the ORCID record as {'title', 'doi', 'type', 'year'}.
    ORCID groups duplicate versions of one paper; any DOI within a group is used."""
    data = fetch_json(f"https://pub.orcid.org/v3.0/{ORCID_ID}/works")
    works = []
    for group in data.get('group', []):
        summary = group['work-summary'][0]
        doi = ''
        for ws in group['work-summary']:
            for ext in (ws.get('external-ids') or {}).get('external-id', []):
                if ext.get('external-id-type') == 'doi' and not doi:
                    doi = ext['external-id-value']
        works.append({
            'title': clean_text(summary['title']['title']['value']),
            'doi': doi.lower(),
            'type': summary.get('type', ''),
            'year': ((summary.get('publication-date') or {}).get('year') or {}).get('value', ''),
        })
    return works


def orcid_doi_for_title(title, works):
    """DOI of the ORCID work whose title matches, or '' (no author check needed: it's your record)."""
    for work in works:
        similarity = difflib.SequenceMatcher(None, normalize_title(title), normalize_title(work['title'])).ratio()
        if work['doi'] and similarity >= TITLE_MATCH_THRESHOLD:
            return work['doi']
    return ''


def auto_tags(title, abstract):
    tags_set = {"Publication"}
    search_blob = (title + " " + abstract).lower()
    for kw, tag_val in TAG_KEYWORDS.items():
        if kw in search_blob:
            tags_set.add(tag_val)
    return sorted(tags_set)


def existing_files():
    return {f for f in os.listdir(PUBLICATIONS_DIR) if f.endswith('.md')}


def existing_dois():
    dois = set()
    for name in existing_files():
        with open(os.path.join(PUBLICATIONS_DIR, name), encoding='utf-8') as f:
            m = re.search(r'^doi:\s*"([^"]+)"', f.read(), flags=re.M)
            if m:
                dois.add(m.group(1).lower())
    return dois


def write_publication(pub, dry_run):
    slug = slugify(pub['title'])
    md_filename = f"{PUBLICATIONS_DIR}/{slug}.md"
    if dry_run:
        print(f"  Would create: {slug}.md")
        print(f"    {pub['journal']} | {pub['date']} | vol {pub['volume'] or '-'} | doi {pub['doi'] or '-'}")
        return

    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(f'title: "{yaml_str(pub["title"])}"\n')
        f.write(f"date: {pub['date']}\n")
        f.write(f'publishDate: "{pub["date"]}"\n')

        f.write("authors:\n")
        for author in pub['authors']:
            f.write(f'  - "{yaml_str(author)}"\n')
        f.write(f'authors_ieee: "{yaml_str(format_authors_list_ieee(pub["authors"]))}"\n')

        f.write(f'journal: "{yaml_str(pub["journal"])}"\n')
        f.write(f'volume: "{pub["volume"]}"\n')
        f.write(f'issue: "{pub["issue"]}"\n')
        f.write(f'pages: "{pub["pages"]}"\n')
        f.write(f'publisher: "{yaml_str(pub["publisher"])}"\n')
        f.write(f'doi: "{pub["doi"]}"\n')
        f.write(f'link: "{pub["link"]}"\n')
        f.write("featured: false\n")  # Can be manually set to true
        # not "type": that is reserved by Hugo and would bypass layouts/publications/
        f.write(f'pub_type: "{pub["type"]}"\n')  # preprint or journal
        f.write('status: "published"\n')  # published, under-review, in-progress

        f.write("tags:\n")
        for tag in auto_tags(pub['title'], pub['abstract']):
            f.write(f'  - "{tag}"\n')
        f.write("---\n\n")

        if pub['abstract']:
            f.write(pub['abstract'] + "\n")

    print(f"  Created: {slug}.md")


def scholar_details(citation_id, paper):
    """Fallback metadata from the Scholar paper page, used when Crossref has no match."""
    detail_url = f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_USER_ID}&citation_for_view={citation_id}"
    detail_html = fetch_html(detail_url)
    detail_parser = ScholarDetailParser()
    detail_parser.feed(detail_html)
    meta = detail_parser.metadata

    journal = clean_text(meta.get('journal', '') or meta.get('conference', '') or meta.get('source', ''))
    abstract = clean_text(meta.get('description', ''))
    if abstract.endswith('…'):
        # Scholar truncates abstracts; drop the cut-off last word
        abstract = abstract.rsplit(' ', 1)[0] + ' …'

    # Standardize date to YYYY-MM-DD
    date_parts = clean_text(meta.get('publication date', '')).split('/')
    year = date_parts[0] if date_parts[0] else clean_text(paper.get('year', ''))
    month = date_parts[1].zfill(2) if len(date_parts) > 1 else "01"
    day = date_parts[2].zfill(2) if len(date_parts) > 2 else "01"

    return {
        'title': clean_text(paper['title']),
        'authors': [a.strip() for a in clean_text(meta.get('authors', '')).split(',') if a.strip()],
        'date': f"{year}-{month}-{day}" if year else "",
        'journal': journal,
        'volume': clean_text(meta.get('volume', '')),
        'issue': clean_text(meta.get('issue', '')),
        'pages': clean_text(meta.get('pages', '')),
        'publisher': clean_text(meta.get('publisher', '')),
        'doi': '',
        'type': 'preprint' if ('arxiv' in journal.lower() or 'preprint' in journal.lower()) else 'journal',
        'abstract': abstract,
        'link': detail_url,
    }


def sync_from_scholar(dry_run):
    print(f"Fetching publications list for user {SCHOLAR_USER_ID}...")
    list_url = f"https://scholar.google.com/citations?hl=en&user={SCHOLAR_USER_ID}&cstart=0&pagesize=100"
    try:
        html = fetch_html(list_url)
    except Exception as e:
        print(f"Error fetching Google Scholar profile list: {e}")
        print("Google Scholar may be blocking automated requests. Add the paper by DOI instead:")
        print("  python3 scripts/sync_publications.py --doi <DOI>")
        sys.exit(1)

    list_parser = ScholarListParser()
    list_parser.feed(html)
    if not list_parser.papers:
        print("Found no papers. Google Scholar probably returned a CAPTCHA page; try again later or use --doi.")
        sys.exit(1)
    print(f"Found {len(list_parser.papers)} papers on profile.")

    files = existing_files()
    dois = existing_dois()
    created = 0
    for idx, paper in enumerate(list_parser.papers):
        title = clean_text(paper['title'])
        citation_id = paper['citation_id']
        prefix = f"[{idx+1}/{len(list_parser.papers)}]"

        if not citation_id:
            print(f"{prefix} Skipping '{title[:40]}...' (no citation ID found)")
            continue

        # Existing files are never overwritten; this also skips Scholar duplicates
        # (e.g. an all-caps conference abstract of the same paper)
        slug = slugify(title)
        if any(f.startswith(slug) for f in files):
            print(f"{prefix} Already on site: {slug}.md")
            continue

        print(f"{prefix} New paper: {title}")
        pub = crossref_by_title(title)
        if pub:
            if pub['doi'].lower() in dois:
                print(f"  Already on site under another title (doi {pub['doi']})")
                continue
            pub['link'] = f"https://doi.org/{pub['doi']}"
            print(f"  Matched on Crossref: doi {pub['doi']}")
        else:
            print("  No confident Crossref match; using Google Scholar details (no DOI)")
            try:
                pub = scholar_details(citation_id, paper)
            except Exception as e:
                print(f"  Error fetching paper details: {e}")
                continue

        write_publication(pub, dry_run)
        files.add(f"{slugify(pub['title'])}.md")
        created += 1

    print(f"\nDone. {created} new publication(s){' would be' if dry_run else ''} added.")


def sync_from_orcid(dry_run):
    print(f"Fetching works from ORCID {ORCID_ID}...")
    try:
        works = orcid_works()
    except Exception as e:
        print(f"Error fetching ORCID record: {e}")
        sys.exit(1)
    print(f"Found {len(works)} works on ORCID.")

    files = existing_files()
    dois = existing_dois()
    created = 0
    for idx, work in enumerate(works):
        prefix = f"[{idx+1}/{len(works)}]"
        if not work['doi']:
            print(f"{prefix} No DOI on ORCID, skipped: {work['title']}")
            print("  Add a DOI to this work on orcid.org, or add the page by hand.")
            continue
        if work['doi'] in dois or any(f.startswith(slugify(work['title'])) for f in files):
            print(f"{prefix} Already on site: {work['title']}")
            continue

        print(f"{prefix} New paper: {work['title']}")
        try:
            pub = crossref_by_doi(work['doi'])
        except Exception as e:
            # e.g. arXiv DOIs are registered with DataCite, not Crossref
            print(f"  Crossref has no record for doi {work['doi']} ({e}); add this one by hand.")
            continue
        pub['link'] = f"https://doi.org/{pub['doi']}"
        write_publication(pub, dry_run)
        files.add(f"{slugify(pub['title'])}.md")
        dois.add(work['doi'])
        created += 1

    print(f"\nDone. {created} new publication(s){' would be' if dry_run else ''} added.")


def add_by_doi(doi, dry_run):
    try:
        pub = crossref_by_doi(doi)
    except Exception as e:
        print(f"Could not find DOI '{doi}' on Crossref: {e}")
        sys.exit(1)
    if pub['doi'].lower() in existing_dois() or any(f.startswith(slugify(pub['title'])) for f in existing_files()):
        print(f"Already on site: {pub['title']}")
        return
    pub['link'] = f"https://doi.org/{pub['doi']}"
    print(f"Found: {pub['title']}")
    write_publication(pub, dry_run)


def fill_missing(dry_run):
    """Fill empty doi/volume/issue/pages (and a Scholar link) in existing files from Crossref.
    Only empty fields are touched; everything else in the file stays as it is."""
    fields = ['doi', 'volume', 'issue', 'pages']
    try:
        works = orcid_works()
    except Exception as e:
        print(f"Could not read ORCID record ({e}); falling back to Crossref title search")
        works = []
    for name in sorted(existing_files()):
        path = os.path.join(PUBLICATIONS_DIR, name)
        with open(path, encoding='utf-8') as f:
            text = f.read()
        empty = [k for k in fields if re.search(rf'^{k}:\s*""\s*$', text, flags=re.M)]
        if not empty:
            continue
        m = re.search(r'^title:\s*"(.*)"\s*$', text, flags=re.M)
        if not m:
            continue
        print(f"{name}: empty {', '.join(empty)}")
        current_doi = re.search(r'^doi:\s*"([^"]*)"', text, flags=re.M)
        doi = (current_doi.group(1) if current_doi else '') or orcid_doi_for_title(m.group(1), works)
        try:
            pub = crossref_by_doi(doi) if doi else crossref_by_title(m.group(1))
        except Exception as e:
            print(f"  Crossref lookup failed: {e}")
            pub = None
        if not pub:
            print("  No confident Crossref match; left unchanged")
            continue
        updates = {k: pub[k] for k in empty if pub[k]}
        if 'doi' in updates and re.search(r'^link:\s*"https://scholar\.google\.com', text, flags=re.M):
            updates['link'] = f"https://doi.org/{pub['doi']}"
        if not updates:
            print("  Crossref has nothing to add")
            continue
        for k, v in updates.items():
            text = re.sub(rf'^{k}:.*$', f'{k}: "{v}"', text, count=1, flags=re.M)
            print(f"  {k}: {v}")
        if not dry_run:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
    if dry_run:
        print("\nDry run: no files were changed.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--doi', help='add one paper by its DOI (from Crossref)')
    parser.add_argument('--fill-missing', action='store_true', help='fill empty doi/volume/issue/pages in existing files')
    parser.add_argument('--scholar', action='store_true', help='also add papers found on Google Scholar but missing from ORCID')
    parser.add_argument('--dry-run', action='store_true', help='show what would change without writing files')
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.makedirs(PUBLICATIONS_DIR, exist_ok=True)
    if args.doi:
        add_by_doi(args.doi, args.dry_run)
    elif args.fill_missing:
        fill_missing(args.dry_run)
    else:
        sync_from_orcid(args.dry_run)
        if args.scholar:
            print()
            sync_from_scholar(args.dry_run)

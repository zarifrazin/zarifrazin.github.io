#!/usr/bin/env python3
import os
import re
import sys
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# Target Scholar Citations profile
SCHOLAR_USER_ID = "HhNqllUAAAAJ"
PUBLICATIONS_DIR = "content/publications"

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
    'flame': 'Flame Retardancy'
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
            elif tag == 'span' and 'gsc_a_y' in attrs_dict.get('class', ''):
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
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


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


def sync():
    os.makedirs(PUBLICATIONS_DIR, exist_ok=True)
    print(f"Fetching publications list for user {SCHOLAR_USER_ID}...")
    
    list_url = f"https://scholar.google.com/citations?hl=en&user={SCHOLAR_USER_ID}&cstart=0&pagesize=100"
    try:
        html = fetch_html(list_url)
    except Exception as e:
        print(f"Error fetching Google Scholar profile list: {e}")
        sys.exit(1)
        
    list_parser = ScholarListParser()
    list_parser.feed(html)
    
    print(f"Found {len(list_parser.papers)} papers on profile.")
    
    for idx, paper in enumerate(list_parser.papers):
        title = clean_text(paper['title'])
        citation_id = paper['citation_id']
        
        if not citation_id:
            print(f"Skipping paper '{title[:40]}...' (No citation ID found)")
            continue
            
        slug = slugify(title)
        md_filename = f"{PUBLICATIONS_DIR}/{slug}.md"
        
        # Check if file exists to prevent overwriting manual configurations (featured status, custom preprints, etc.)
        if os.path.exists(md_filename):
            print(f"[{idx+1}/{len(list_parser.papers)}] Skipping existing file: {slug}.md")
            continue
            
        # Ignore duplicate titles/conference abstracts if they map to the same slug
        # e.g., if there's a lowercase/uppercase duplicate
        similar_files = [f for f in os.listdir(PUBLICATIONS_DIR) if f.startswith(slug)]
        if similar_files:
            print(f"[{idx+1}/{len(list_parser.papers)}] Skipping duplicate/similar file for: {slug}")
            continue

        print(f"[{idx+1}/{len(list_parser.papers)}] Fetching details for citation: {citation_id}...")
        detail_url = f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_USER_ID}&citation_for_view={citation_id}"
        
        try:
            detail_html = fetch_html(detail_url)
        except Exception as e:
            print(f"  Error fetching paper details: {e}")
            continue
            
        detail_parser = ScholarDetailParser()
        detail_parser.feed(detail_html)
        
        meta = detail_parser.metadata
        
        # Parse fields
        authors_raw = clean_text(meta.get('authors', ''))
        authors = [a.strip() for a in authors_raw.split(',') if a.strip()]
        
        journal = clean_text(meta.get('journal', ''))
        volume = clean_text(meta.get('volume', ''))
        issue = clean_text(meta.get('issue', ''))
        pages = clean_text(meta.get('pages', ''))
        publisher = clean_text(meta.get('publisher', ''))
        abstract = clean_text(meta.get('description', ''))
        
        pub_date_raw = clean_text(meta.get('publication date', ''))
        # Standardize date to YYYY-MM-DD
        date_str = ""
        year_str = ""
        if pub_date_raw:
            parts = pub_date_raw.split('/')
            if len(parts) >= 1:
                year_str = parts[0]
                date_str = f"{year_str}-01-01"
            if len(parts) >= 2:
                date_str = f"{year_str}-{parts[1].zfill(2)}-01"
            if len(parts) >= 3:
                date_str = f"{year_str}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
        else:
            year_str = clean_text(paper.get('year', ''))
            if year_str:
                date_str = f"{year_str}-01-01"
            else:
                date_str = "2020-01-01"
                year_str = "2020"
                
        # Keywords check for tagging
        tags_set = {"Publication"}
        search_blob = (title + " " + abstract).lower()
        for kw, tag_val in TAG_KEYWORDS.items():
            if kw in search_blob:
                tags_set.add(tag_val)
        tags_list = sorted(list(tags_set))
        
        # Determine the format based on type (preprint vs journal article)
        is_preprint = "arxiv" in journal.lower() or "preprint" in journal.lower()
        pub_type = "preprint" if is_preprint else "journal"
        
        # Write Markdown file
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(f'title: "{title}"\n')
            f.write(f"date: {date_str}\n")
            f.write(f'publishDate: "{date_str}"\n')
            
            # Format authors array
            f.write("authors:\n")
            for author in authors:
                f.write(f'  - "{author}"\n')
            
            # Format authors_ieee string
            authors_ieee = format_authors_list_ieee(authors)
            f.write(f'authors_ieee: "{authors_ieee}"\n')
                
            f.write(f'journal: "{journal}"\n')
            f.write(f'volume: "{volume}"\n')
            f.write(f'issue: "{issue}"\n')
            f.write(f'pages: "{pages}"\n')
            f.write(f'publisher: "{publisher}"\n')
            f.write(f'doi: ""\n') # Empty DOI by default (can be manually filled)
            f.write(f'link: "{detail_url}"\n')
            f.write(f"featured: false\n") # Can be manually set to true
            f.write(f'type: "{pub_type}"\n') # preprint or journal
            f.write(f'status: "published"\n') # published, under-review, in-progress
            
            # Format tags list
            f.write("tags:\n")
            for tag in tags_list:
                f.write(f'  - "{tag}"\n')
                
            f.write("---\n\n")
            
            if abstract:
                # Truncate clean abstract
                if abstract.endswith('…'):
                    # Strip trailing citation strings like "Scholar articles..."
                    abstract = abstract.rsplit(' ', 1)[0]
                f.write(abstract + "\n")
                
        print(f"  Created: {slug}.md")

    print("\nSync complete! All new Google Scholar publications synced successfully.")

if __name__ == '__main__':
    sync()

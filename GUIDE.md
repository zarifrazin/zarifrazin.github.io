# Website Guide: abzarif.com

How to update this website, and how it works. Written so that **you** can add
content without help, and so that **any AI assistant** starting with no memory
of past conversations can understand the site before changing it.

> This file, `CLAUDE.md`, `AGENTS.md` and the `archetypes/` folder are **not
> published**. Hugo only publishes `content/` and `static/`.

**Contents**
1. [The five rules](#1-the-five-rules)
2. [The everyday workflow](#2-the-everyday-workflow)
3. [Where everything lives](#3-where-everything-lives)
4. [Adding content: the basics](#4-adding-content-the-basics)
5. [Section by section](#5-section-by-section)
6. [Images and files](#6-images-and-files)
7. [Changing the home page text, menu and sections](#7-changing-the-home-page-text-menu-and-sections)
8. [When something goes wrong](#8-when-something-goes-wrong)
9. [Do not do](#9-do-not-do)
10. [For AI assistants: how the site is built](#10-for-ai-assistants-how-the-site-is-built)

---

## 1. The five rules

1. **Preview before you publish.** Run `hugo server` and look at the page.
2. **Pushing publishes.** `git push` makes changes live on abzarif.com about a minute later.
3. **Never rename or delete a published page's file** without a reason: the
   file name is the web address, and Google has it indexed.
4. **Never delete publications to regenerate them.** Run the sync script instead (see [Publications](#publications)).
5. **Keep private and large files out.** No lecture recordings, no full CV with
   phone number or address, no original phone photos (they contain GPS location).

---

## 2. The everyday workflow

All commands are run in a terminal inside the website folder:
`/home/abzarif/websites/personal-website`

**Step 1: add or edit a file** (see sections 4 and 5).

**Step 2: preview it on your computer.**
```bash
hugo server
```
Open http://localhost:1313 in the browser. The page reloads every time you
save a file. Press `Ctrl+C` in the terminal to stop.

**Step 3: publish it.**
```bash
git add -A
git commit -m "Add life event: PhD defense"
git push
```
`git add -A` takes every changed file. To publish only some, name them instead:
`git add content/life-events/phd-defense.md static/images/life-events/phd-defense.jpg`

(You can also do step 3 in VS Code: *Source Control* panel → type a message → *Commit* → *Sync Changes*.)

**Step 4: check the live site** after about a minute. If it hasn't changed,
open the repository on GitHub → **Actions** tab. A red ✗ means the build
failed; click it to read the error (see [section 8](#8-when-something-goes-wrong)).

**No sitemap work needed.** `sitemap.xml` is rebuilt automatically on every
push and lists every page, and Google rechecks it on its own; there's no need
to resubmit it. Optional, for an important new page (e.g. a new paper):
Google Search Console → *URL Inspection* → paste the address → *Request indexing*.

---

## 3. Where everything lives

| What | Where |
|---|---|
| Life events | `content/life-events/` |
| Education | `content/education/` |
| Experience | `content/experience/` |
| Honors & Activities | `content/honors-activities/` |
| Projects (research and engineering) | `content/projects/` |
| Publications | `content/publications/` (filled by the sync script) |
| Resources (scripts, tutorials, skills) | `content/resources/` |
| LAMMPS guide (8 chapters) | `content/resources/md-lammps-guide/` |
| Photo gallery (all photos in one file) | `content/gallery.md` |
| Blog posts (section switched off) | `content/wandering-thoughts/` |
| Hero, About Me, skills, menu, section titles | `hugo.yaml` |
| Templates for new content | `archetypes/` |
| Pictures | `static/images/<section>/` |
| PDFs, scripts, zips | `static/documents/` |
| Videos | `static/videos/` |
| Profile photo | `static/images/profile.jpg` |
| Publication sync script | `scripts/sync_publications.py` |

**Rule of thumb:** a file at `static/images/x.jpg` is used in a page as `/images/x.jpg`
(drop the word `static`).

---

## 4. Adding content: the basics

### Two ways to start a new file

**Way A: copy the template.** Copy `archetypes/<section>.md` into
`content/<section>/<new-name>.md`, then edit it.

**Way B: let Hugo copy it.**
```bash
hugo new content life-events/phd-defense.md
```
Both give the same result: a file full of example values with a comment on
every line explaining it.

**The file name becomes the web address.** `content/life-events/phd-defense.md`
→ `abzarif.com/life-events/phd-defense/`. Use lowercase words joined by dashes,
no spaces.

### How a content file looks

```markdown
---
title: "Passed Qualifying Exam"
date: 2026-05-15
featured: true
---

The text of the page goes here.
```

- The part between the two `---` lines is the **front matter**: settings for the page.
- Everything below is the **body**, written in Markdown:
  `**bold**`, `*italic*`, `[link text](https://...)`, `### Heading`,
  `* bullet`, `1. numbered`, and a blank line between paragraphs.
- Lines starting with `#` inside the front matter are comments, ignored by Hugo.
  You can delete the template's comments or leave them.

### Front matter rules (most build errors come from these)

- **Dates** are `YYYY-MM-DD`, e.g. `2026-05-15`.
- **Put text in double quotes**, especially if it contains `:` or `#`:
  `title: "PhD: The Beginning"`.
- **Indent lists with two spaces**, never tabs:
  ```yaml
  tags:
    - Academic
    - Life Event
  ```
- **Spell field names exactly.** `data:` instead of `date:` is silently ignored.

### Which items appear on the home page

Each home page section shows a few items (set by `count` in `hugo.yaml`:
3 for most, 2 for Education). The rule is the same everywhere:

1. **Every item with `featured: true` is shown**, however many there are.
2. If fewer than `count` are featured, the **newest** other items fill the remaining places.

So leave `featured: false` unless you want an item to stay on the home page
even when newer ones arrive. Everything is always listed on the section's own
"View all" page.

### Why a new page might not appear

- **`draft: true`**: drafts are never published. Set `draft: false`.
- **A date in the future**: Hugo hides pages dated after today until that day.
- **Wrong folder or a typo in a field name.**
- **Resources only:** `category` doesn't exactly match one of the four filter names.

---

## 5. Section by section

### Life Events
Template: `archetypes/life-events.md` → `content/life-events/<name>.md`

1. Put the photo in `static/images/life-events/` (see [section 6](#6-images-and-files) for size).
2. Set `image: /images/life-events/<photo>.jpg`.
3. `tags`: the first tag is the badge shown on the card. Used so far:
   **Academic** or **Personal**, followed by **Life Event**.
4. `description` is the short text on the card. The body is the full story.
   The existing events start the body with a line like `Spring, 2026`.

The photo is also the preview picture when the page is shared on social media.

### Education
Template: `archetypes/education.md` → `content/education/<name>.md`

`dateRange` is shown exactly as you write it ("August 2024 - Present");
`date` is only used for sorting. Use `weight: 1` to force an entry to the top
(the PhD uses this to stay above the M.S.). The body is a short bullet list.

### Experience
Template: `archetypes/experience.md` → `content/experience/<name>.md`

Same idea as Education: `company`, `companyUrl`, `dateRange` (shown) and
`date` (sorting). When a job ends, change "Present" in `dateRange` to the end date.

### Honors & Activities
Template: `archetypes/honors-activities.md` → `content/honors-activities/<name>.md`

These are cards, not pages. `icon` is a Font Awesome icon name; browse more at
https://fontawesome.com/v6/search?o=r&m=free (use the `fas fa-...` form).
Talks, guest lectures and reviewing go here too, as "activities".

### Projects
Template: `archetypes/projects.md` → `content/projects/<name>.md`

- `category`: **Research** or **Engineering**.
- `badges`: short tags on the card (tools, methods).
- `links`: buttons on the project page, each with a `name`, a Font Awesome
  `icon` (`fab fa-github`, `fas fa-link`, `fas fa-external-link-alt`,
  `fab fa-google-drive`) and a `url`. Delete the ones you don't need.
- `image`: the figure on the card and page, in `static/images/projects/`
  (or `static/images/research/`). Also the social share preview.

### Publications

**Papers on your ORCID profile (normal case):**
```bash
python3 scripts/sync_publications.py --dry-run   # see what would be added
python3 scripts/sync_publications.py             # add new papers
```
It reads your ORCID record (0000-0002-2977-2392) and fills in authors, journal,
date and abstract from Crossref. **It never overwrites existing files**, so
hand edits are safe.

After adding a paper, open its new file and:
- put a **topic tag first** in `tags` (the first two show as badges), e.g. `"Carbon Nanotubes"`;
- add `equal_contribution:` if you are a co-first author;
- check the abstract (Elsevier papers often come without one; paste it from the journal page).

**When volume/issue/pages appear later** (papers published "online first"):
```bash
python3 scripts/sync_publications.py --fill-missing
```
This fills only empty fields.

**Papers not on ORCID** (preprints, under review): copy
`archetypes/publications.md` and fill it in by hand. `status` can be
`published`, `under-review`, `in-progress` or `ongoing`; `pub_type` can be
`journal` or `preprint`.

**Never delete the publications folder to start over.** The files contain
hand-added data (co-first authors, abstracts) the script can't recover. If a
file looks wrong, restore it from git: `git checkout -- content/publications/<file>.md`.

### Resources
Template: `archetypes/resources.md` → `content/resources/<name>.md`

- `category` must be **exactly** one of `Simulation Scripts`, `Tutorials & Guides`,
  `Handouts & PDFs`, `Skills Showcase`, or the filter buttons won't find it.
- Add the tag `LAMMPS` to make it appear under the **LAMMPS** filter button.
- Optional buttons: `github`, `download`, `pdf`.

Embedding files in the body:

| Show | Write in the body |
|---|---|
| A PDF or Office file with a preview | `{{< preview src="/documents/folder/file.pdf" title="file.pdf" >}}` |
| A script from `static/`, highlighted, with a download link | `{{< lmpfile src="/documents/folder/in.lammps" title="Full script" >}}` |
| Equations (add `math: true` to the front matter) | `$C_v$` inline, `$$ ... $$` on its own line |

### Photo gallery
All photos are listed in **one file**, `content/gallery.md`. To add a photo:

1. Prepare it ([section 6](#6-images-and-files)) and save it in `static/images/gallery/`.
2. Add a block like this under `galleryImages:` in `content/gallery.md`
   (two-space indent, starting with `- src:`):
   ```yaml
     - src: "/images/gallery/new-photo.jpg"
       title: "Short Title"
       category: "Travel"        # used so far: NC State, Travel, BUET
       caption: "One sentence about the photo."
       date: "2026"
   ```
3. **Order matters:** photos appear in the order listed, and the home page shows
   the **first three**.

### Wandering Thoughts (blog)
Template: `archetypes/wandering-thoughts.md`. The section exists but is
switched off on the home page and menu. To switch it on, set
`wandering_thoughts: enable: true` in `hugo.yaml`. Posts stay hidden while
`draft: true`.

### The LAMMPS guide
`content/resources/md-lammps-guide/`: the landing page is `_index.md` and
each chapter is one file, ordered by `weight`. Scripts shown in chapters are
read from `static/documents/md-lammps-guide/`, so editing a script there
updates both the download and the page. If you change a script, also rebuild
the zip files in that folder (or ask an AI to).

---

## 6. Images and files

**Before adding a photo:**
- **Size:** at most about 2000 pixels on the long side and under ~600 KB.
  Phone photos (4000 px, 3+ MB) slow the site down.
- **Format:** `.jpg` for photos, `.png` for figures. iPhone `.HEIC` doesn't work
  in browsers; convert it to JPG first.
- **Privacy:** phone photos contain the **GPS location** where they were taken.
  Remove it before publishing. In Windows: right-click the file → *Properties*
  → *Details* → *Remove Properties and Personal Information*. The free website
  https://squoosh.app resizes, converts and strips location data in one step.
- **Name:** lowercase with dashes, e.g. `phd-defense-2027.jpg`.

**Other files:**
- PDFs, scripts and zips go in `static/documents/<topic>/`.
- Videos go in `static/videos/`. Keep each under ~5 MB. Compress large videos
  first (ask an AI, or use HandBrake).
- **Never add:** lecture recordings, `.pptx` source files, a CV with your phone
  number or home address, or anything over ~20 MB.

---

## 7. Changing the home page text, menu and sections

All of these are in `hugo.yaml`:

| What | Where in `hugo.yaml` |
|---|---|
| Name, subtitle and intro next to the photo | `params:` → `hero:` → `title`, `subtitle`, `content` |
| Social icons under the intro | `hero:` → `socialLinks:` |
| About Me text | `about:` → `content:` |
| Research expertise list | `about:` → `skills:` → `items:` |
| Menu items and their order | `Menus:` → `main:` (lower `weight` = further left) |
| Section titles, number of items, on/off | each section's block, e.g. `experience:` → `title`, `count`, `enable` |
| Google search description | `params:` → `description:` |
| Browser tab title of the home page | `params:` → `seo:` → `homeTitle` |

The order of the sections on the home page is set in `layouts/index.html`
(one line per section). Moving a section means moving its line, plus its menu
`weight` in `hugo.yaml`.

`hugo.yaml` is strict about indentation. After editing it, always run
`hugo server` and check that it starts without an error.

---

## 8. When something goes wrong

| Symptom | Likely cause and fix |
|---|---|
| `hugo server` prints an error mentioning a file and line | Usually front matter: missing quote, tab instead of spaces, or a colon in unquoted text. Go to that line. |
| "failed to unmarshal YAML" | Same as above: indentation or quotes in front matter or `hugo.yaml`. |
| New page doesn't show | `draft: true`, a future `date`, wrong folder, or (resources) a `category` mismatch. See [section 4](#why-a-new-page-might-not-appear). |
| Image doesn't show | Path must start with `/images/...`, not `static/images/...`; check upper/lower case. |
| Live site unchanged after push | GitHub → repository → **Actions**. Red ✗ = build failed; click it for the error. |
| Shared link shows the wrong picture | Social sites cache previews: refresh with Facebook's *Sharing Debugger* or LinkedIn's *Post Inspector*. |
| Want to undo uncommitted edits to a file | `git checkout -- path/to/file` |

---

## 9. Do not do

- **Don't rename or delete published pages** without a reason (changes the web address, breaks Google results and old links).
- **Don't change the domain** (`baseURL` in `hugo.yaml`, or the custom domain in GitHub Pages). The site moved from `www.abzarif.com` to `abzarif.com` in October 2026; switching again resets Google's progress.
- **Don't delete `content/publications/`** to regenerate it.
- **Don't edit files inside `themes/`.** Changes to the theme go in `layouts/` (see section 10).
- **Don't touch the email DNS records at GoDaddy** (MX, autodiscover, SPF, …): they run your Microsoft 365 email. Keep GoDaddy "domain forwarding" off.
- **Don't commit the `public/` folder** (it's ignored automatically; it's only the local build output).

---

## 10. For AI assistants: how the site is built

*Read this before changing anything structural. The user relies on you for
structural changes but adds content alone using sections 4–6, so keep those
sections accurate when you change how content works.*

### Stack and publishing
- **Hugo** static site, theme **hugo-profile** in `themes/hugo-profile/`
  (vendored, not a submodule). **Never edit the theme**; override files by
  putting the same path under `layouts/`.
- **Deploy:** `git push` to `main` on `github.com/zarifrazin/zarifrazin.github.io`
  (SSH) → GitHub Actions (`.github/workflows/`) builds with **Hugo 0.147.0** and
  deploys to GitHub Pages. The local Hugo is **0.168** (a snap). **Test template
  changes with 0.147**: download `hugo_extended_0.147.0_linux-amd64.tar.gz`
  from Hugo's GitHub releases into a temporary folder and build with it.
- The snap Hugo has a private `/tmp`; build into `public/` (gitignored), not `/tmp`.
- **Ask before pushing**: a push publishes the site.
- Commit messages: a short imperative title, a blank line, `-` bullet points.

### Domain and search
- Main address: **https://abzarif.com** (apex). `www`, `http://` and
  `zarifrazin.github.io` all 301-redirect there (GitHub Pages custom domain,
  HTTPS enforced). DNS at GoDaddy; Microsoft 365 email records must be preserved.
- Moved from `www.abzarif.com` (Google Sites era, 2023) to the apex in Oct 2026.
  Google Search Console was still re-assigning the home page from `www` at the
  time of writing; that is expected, not a bug.
- `static/home/` and `static/skills/`: redirect stubs for old Google Sites URLs
  (noindex + canonical). Keep them.

### Custom pieces (all under `layouts/` unless noted)
| File | Purpose |
|---|---|
| `partials/featured-or-latest.html` | Home-page selection rule (featured items + newest to fill `count`), used by every section partial |
| `partials/sections/*.html` | Home page sections (overriding the theme's) |
| `index.html` | Order of home page sections |
| `partials/head/extensions.html` | Canonical link; schema.org `Person` JSON-LD (home only); `noindex` on tag/category pages; MathJax when `math: true`; small CSS fixes (hero height, header z-index, "View all" buttons) |
| `partials/_funcs/get-page-images.html` | Overrides Hugo's internal helper so a page's `image:` becomes its og:image/twitter:image (falls back to `params.images`, the profile photo) |
| `sitemap.xml` | Built-in sitemap minus taxonomy/term pages |
| `robots.txt` | Allows all, points to the sitemap |
| `resources/list.html` | Resources page: category filter buttons plus tag filters from `params.resources.tagFilters` |
| `partials/sections/about.html` | About section; skills list uses a wider grid than the theme |
| `md-guide/list.html`, `md-guide/single.html` | LAMMPS guide landing page and chapters (`type: md-guide`, set by cascade in the guide's `_index.md`) |
| `partials/md-guide/*` | Guide styles, chapter list, TechArticle JSON-LD |
| `shortcodes/preview.html` | Inline PDF/Office preview |
| `shortcodes/lmpfile.html` | Renders a text file from `static/` with highlighting + download link |
| `shortcodes/svgfig.html` | Inlines an SVG so `currentColor` follows light/dark theme |
| `shortcodes/guide-video.html`, `guide-roadmap.html` | Guide video embed (poster = `<name>-poster.jpg`) and chapter cards |
| `archetypes/*.md` | Content templates (plain values, no template code, so they also work when copied by hand) |

### Content conventions
- Home sections and counts: `params.<section>.count` in `hugo.yaml`.
- Honors & Activities children have `build: render: never` (cascade): cards only, no pages.
- `content/_index.md` exists only to set the home page title for og:title.
- Publications: the sync script never overwrites; `--fill-missing` fills empty
  `doi/volume/issue/pages`. In the J. Mol. Liq. paper
  (`effect-of-surface-wettability-on-specific-heat-capacity-of-nano-confined-liquid.md`)
  all three listed authors are co-first authors. Elsevier abstracts aren't available from Crossref/OpenAlex.
- The LAMMPS guide must stay **identical to the user's lecture slides and code
  notes**. Its scripts are the user's own, including known imperfections, which
  the user chose to keep (exercises mention them as questions, not corrections).
  The guide's "About this guide" section states that the conversion was done by AI.

### Checks before proposing a push
1. `hugo --cleanDestinationDir` builds without errors or warnings.
2. No broken internal links in `public/` (all `href`/`src` starting with `/` resolve).
3. JSON-LD blocks parse; `public/sitemap.xml` is valid XML with `https://abzarif.com/` URLs.
4. For template changes: same results with Hugo 0.147.
5. No stray files (`desktop.ini`, `*Zone.Identifier`, HEIC, videos > ~5 MB, private documents).

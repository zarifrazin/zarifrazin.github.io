---
# PUBLICATION template, for papers NOT on ORCID (preprints, papers under review).
# Papers with a DOI on ORCID: don't use this, run   python3 scripts/sync_publications.py   instead.
# See GUIDE.md, section "Publications".
# Save as: content/publications/<paper-title-in-lowercase-with-dashes>.md

title: "Paper Title"
date: 2026-01-01                           # YYYY-MM-DD publication (or submission) date; sorts the list
publishDate: "2026-01-01"                  # same date, in quotes
authors:                                   # full names in author order; your name is bolded automatically
  - "First Author"
  - "Zarif Ahmad Razin Bhuiyan"
authors_ieee: "F. Author and Z. A. R. Bhuiyan"   # short-name version shown on the card
# equal_contribution:                      # optional: co-first authors (get a * mark)
#   - "First Author"
#   - "Zarif Ahmad Razin Bhuiyan"
journal: "Journal Name"
volume: ""
issue: ""
pages: ""
publisher: ""
doi: ""                                    # e.g. 10.1021/acsnano.6c09883 (without https://doi.org/)
link: ""                                   # full URL to the paper or preprint
featured: false
pub_type: "journal"                        # "journal" or "preprint"
status: "published"                        # "published", "under-review", "in-progress" or "ongoing"
tags:                                      # first two tags show as badges; first should be the topic
  - "Topic"
  - "Publication"
---

Paste the abstract here.

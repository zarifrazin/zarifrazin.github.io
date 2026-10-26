---
# RESOURCE template (scripts, tutorials, handouts). See GUIDE.md, section "Resources".
# Save as: content/resources/<short-name>.md   (e.g. content/resources/lammps-thermal-conductivity.md)

title: "Resource Title"
date: 2026-01-01                           # YYYY-MM-DD; also shown as "Release Date"
summary: "One or two sentences shown on the resource card."
category: "Simulation Scripts"             # exactly one of: "Simulation Scripts", "Tutorials & Guides",
                                           #   "Handouts & PDFs", "Skills Showcase" (must match, or the filter hides it)
tags:                                      # add "LAMMPS" so it appears under the LAMMPS filter button
  - "LAMMPS"
  - "Molecular Dynamics"
github: ""                                 # optional: GitHub repository URL (shows a button)
download: ""                               # optional: /documents/... file to download (shows a button)
pdf: ""                                    # optional: /documents/... PDF (shows a button)
image: ""                                  # optional: /images/resources/... picture, used as the share preview
featured: false                            # true = shown on the home page (home shows 3)
# math: true                               # uncomment to use equations: $inline$ or $$display$$
---

Describe the resource here. To embed a PDF preview or a script file, see GUIDE.md, "Resources".

```bash
# a code block: paste LAMMPS commands here
```

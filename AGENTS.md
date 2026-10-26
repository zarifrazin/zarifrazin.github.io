# Instructions for AI assistants

This is the Hugo source of the personal website https://abzarif.com.

**Before changing anything, read `GUIDE.md`**, especially section 10
("For AI assistants: how the site is built"). It explains the theme
overrides, deploy pipeline, domain setup and content conventions.

Essentials:
- **Pushing publishes.** Ask the user before `git push`.
- Deploy builds with **Hugo 0.147.0**, the local Hugo is 0.168: test template changes with 0.147.
- Never edit `themes/`; override in `layouts/`.
- Never delete `content/publications/` to regenerate it; use `scripts/sync_publications.py` (`--dry-run`, `--fill-missing`).
- Don't rename published content files (URLs are indexed by Google). Main address is `https://abzarif.com` (apex); don't change it.
- The user adds content alone using `GUIDE.md` sections 4–6 and the templates in `archetypes/`. If you change how a section works, update `GUIDE.md` and the matching archetype in the same change.

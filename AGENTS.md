# website-and-cv

Public GitHub Pages website sources.

CV sources live outside this public repo in the local folder `/Users/jbd/projects/cv`. Do not add CV source files or rendered CV PDFs back into this public repo. When a publication refresh should update both the CV folder and the website, run the updater from `/Users/jbd/projects/cv`.

## Agent Runtime

For Python/runtime rules, follow `/Users/jbd/projects/executive/docs/agent-runtime-policy.md`: do not run bare `python`, `python3`, `pip`, or `pytest` for project work; use `./scripts/python` or repo-local CLI wrappers.

Use `./scripts/python update_publications.py` for a website-only publication update.

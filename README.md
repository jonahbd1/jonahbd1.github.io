# jonahbd1.github.io

Public GitHub Pages website.

## Publications Workflow

The public publication section is generated from INSPIRE-HEP by:

```bash
./scripts/python update_publications.py
```

That script updates:

- `index.html`

CV sources live outside this public repo in the local folder `/Users/jbd/projects/cv`. Prefer running that folder's publication updater when both the CV and public website should be refreshed together.

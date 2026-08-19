# jonahbd1.github.io

Public GitHub Pages website.

## Publications workflow

This repository is a public projection, not the authority for CV or
publication data. The private applications repository owns the dated INSPIRE
snapshots and publication renderer.

From that repository, run:

```bash
python3 scripts/sync_profile.py
```

Its machine-local `config/local.toml` identifies this checkout. The sync updates
only the marked publication section in `index.html`; it does not commit or push
this repository. Use `--skip-website` for a private CV-only refresh.

# Public website

Public GitHub Pages website sources. This repository is a deployment target,
not the authority for candidate facts, CV content, or publication metadata.

Do not add private profile files, CV sources, or rendered CV PDFs to this public
repository. Publication updates are generated from the private applications
repository with `python3 scripts/sync_profile.py`, which exports only allowlisted
public data into the marked section of `index.html`.

## Runtime

The current website is static and requires no Python project runtime. Keep any
future build instructions repository-local rather than referring to an absolute
path on one machine.

Do not hand-edit generated content between `PUBLICATIONS-START` and
`PUBLICATIONS-END`; change the renderer or source data in the private
applications repository instead.

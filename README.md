# jonahbd1.github.io

Public GitHub Pages website. The homepage is plain HTML with `site.css` and
`site.js`; it needs no local build or Python runtime. Pages publishes the root
of `main`. Historical Jekyll starter pages are excluded by `_config.yml`.

## Publications workflow

The private applications repository owns reviewed publication selections,
public summaries, status and dated INSPIRE metadata. Its supported
`scripts/sync_profile.py` command renders the marked publication section of
`index.html` in this Airy layout. Its ignored local integration configuration
identifies this public checkout. The sync neither commits nor pushes.

Do not hand-edit between `PUBLICATIONS-START` and `PUBLICATIONS-END`. Keep private
profile sources, provenance and CV PDFs outside this public repository. The
weekly daily review proposes coordinated website/profile/CV changes before
editing; publication requires a separate explicit request.

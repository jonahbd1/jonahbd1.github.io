# jonahbd1.github.io

Personal website plus CV sources.

## Publications and CV workflow

The publication list is generated from INSPIRE-HEP by:

```bash
python3 update_publications.py
```

That script updates:

- `index.html`
- `cv/cv.md`
- `cv/publication-list.md`

It also renders PDF outputs for the Markdown sources:

- `cv/cv.pdf`
- `cv/publication-list.pdf`

Local PDF generation currently uses `pandoc` with `xelatex`.

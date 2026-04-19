#!/usr/bin/env python3
"""Fetch publications from INSPIRE-HEP and update website and Markdown CV files."""

import json
import os
import re
import subprocess
import urllib.request

INSPIRE_BAI = "Jonah.Berean.Dutcher.1"
API_URL = (
    "https://inspirehep.net/api/literature?sort=mostrecent&size=250"
    f"&q=a%20{INSPIRE_BAI}"
    "&fields=titles,authors,arxiv_eprints,publication_info,dois,earliest_date,document_type"
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(SCRIPT_DIR, "index.html")
CV_MD = os.path.join(SCRIPT_DIR, "cv", "cv.md")
PUBLICATION_LIST_MD = os.path.join(SCRIPT_DIR, "cv", "publication-list.md")

MY_NAMES = {"Berean-Dutcher, Jonah", "Berean-Dutcher, J.", "Berean, Jonah", "Berean, J."}


def fetch_papers():
    """Fetch papers from INSPIRE API, filtering out theses."""
    req = urllib.request.Request(API_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    papers = []
    for hit in data.get("hits", {}).get("hits", []):
        meta = hit.get("metadata", {})
        doc_types = meta.get("document_type", [])
        if "thesis" in doc_types:
            continue
        title = normalize_title(meta.get("titles", [{}])[0].get("title", "Untitled"))
        authors_raw = meta.get("authors", [])
        arxiv = meta.get("arxiv_eprints", [{}])[0].get("value") if meta.get("arxiv_eprints") else None
        pub_info = meta.get("publication_info", [{}])[0] if meta.get("publication_info") else {}
        journal = pub_info.get("journal_title")
        year = pub_info.get("year")
        if not year:
            earliest = meta.get("earliest_date", "")
            year = earliest[:4] if earliest else ""
        doi = meta.get("dois", [{}])[0].get("value") if meta.get("dois") else None
        inspire_id = hit.get("id")
        papers.append({
            "title": title,
            "authors": authors_raw,
            "arxiv": arxiv,
            "journal": journal,
            "year": year,
            "doi": doi,
            "inspire_id": inspire_id,
        })
    return papers


def format_author_short(full_name):
    """Convert 'Last, First Middle' to 'F. Last'."""
    if "," in full_name:
        last, first = full_name.split(",", 1)
        first = first.strip()
        initial = first[0] if first else ""
        return f"{initial}. {last.strip()}"
    return full_name


def normalize_title(title):
    """Clean up common spacing glitches in INSPIRE titles."""
    title = re.sub(r"\s+", " ", title).strip()
    title = re.sub(r"([A-Za-z0-9])(\$)", r"\1 \2", title)
    return title


def is_me(full_name):
    name = full_name.strip()
    if name in MY_NAMES:
        return True
    # Also match by last name containing "Berean"
    last = name.split(",")[0].strip() if "," in name else name
    return "Berean" in last


def author_list_html(authors):
    """Format author list for HTML, bolding my name. Truncate to 2 coauthors + me."""
    me_html = "<strong>J. Berean-Dutcher</strong>"
    coauthors = []
    me_idx = None
    for i, a in enumerate(authors):
        fn = a.get("full_name", "")
        if is_me(fn):
            me_idx = i
        else:
            coauthors.append(format_author_short(fn))
    # Build truncated list preserving my position
    if len(coauthors) <= 2:
        # Short enough — show everyone in original order
        names = []
        for a in authors:
            fn = a.get("full_name", "")
            if is_me(fn):
                names.append(me_html)
            else:
                names.append(format_author_short(fn))
        if len(names) <= 2:
            return " & ".join(names)
        return ", ".join(names[:-1]) + " & " + names[-1]
    # Truncate: pick first 2 coauthors, insert me at original position, add et al.
    shown = coauthors[:2]
    if me_idx is not None:
        shown.insert(min(me_idx, 2), me_html)
    else:
        shown.insert(0, me_html)
    return ", ".join(shown) + " et al."


def author_list_markdown(authors):
    """Format author list for Markdown, bolding my name and truncating like the website."""
    me_md = "**J. Berean-Dutcher**"
    coauthors = []
    me_idx = None
    for i, a in enumerate(authors):
        fn = a.get("full_name", "")
        if is_me(fn):
            me_idx = i
        else:
            coauthors.append(format_author_short(fn))
    if len(coauthors) <= 2:
        names = []
        for a in authors:
            fn = a.get("full_name", "")
            if is_me(fn):
                names.append(me_md)
            else:
                names.append(format_author_short(fn))
        if len(names) <= 2:
            return " & ".join(names)
        return ", ".join(names[:-1]) + " & " + names[-1]
    shown = coauthors[:2]
    if me_idx is not None:
        shown.insert(min(me_idx, 2), me_md)
    else:
        shown.insert(0, me_md)
    return ", ".join(shown) + " et al."


def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def paper_link(paper):
    """Return (url, display_text) for a paper."""
    if paper["arxiv"]:
        return f"https://arxiv.org/abs/{paper['arxiv']}", f"arXiv:{paper['arxiv']}"
    if paper["doi"]:
        return f"https://doi.org/{paper['doi']}", f"doi:{paper['doi']}"
    if paper["inspire_id"]:
        return f"https://inspirehep.net/literature/{paper['inspire_id']}", "INSPIRE"
    return None, None


def generate_html(papers):
    lines = ['      <div class="grid">']
    for p in papers:
        url, link_text = paper_link(p)
        title_escaped = escape_html(p["title"])
        authors_html = author_list_html(p["authors"])
        lines.append('        <div class="card">')
        lines.append(f'          <h3>{title_escaped}</h3>')
        if url:
            lines.append(f'          <p><em><a href="{url}" target="_blank" rel="noreferrer">{escape_html(link_text)}</a></em></p>')
        lines.append(f'          <p class="subtle">{authors_html}</p>')
        lines.append('        </div>')
    lines.append('      </div>')
    return "\n".join(lines)


def generate_markdown(papers):
    lines = []
    for p in papers:
        url, _ = paper_link(p)
        title = p["title"]
        authors_md = author_list_markdown(p["authors"])
        journal = p.get("journal")
        year = p.get("year", "")
        if url:
            item = f"- [{title}]({url})"
        else:
            item = f"- {title}"
        if authors_md:
            item += f". {authors_md.rstrip('.')}"
        if journal:
            item += f". *{journal}*, {year}"
        elif year:
            item += f". Preprint, {year}"
        lines.append(item)
    return "\n".join(lines)


def replace_between_markers(text, start_marker, end_marker, replacement):
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL,
    )
    repl = start_marker + "\n" + replacement + "\n" + end_marker
    return pattern.sub(lambda m: repl, text)


def update_file(path, start_marker, end_marker, new_content):
    with open(path, "r") as f:
        text = f.read()
    updated = replace_between_markers(text, start_marker, end_marker, new_content)
    with open(path, "w") as f:
        f.write(updated)
    print(f"Updated {path}")


def render_pdf(source_path):
    output_path = os.path.splitext(source_path)[0] + ".pdf"
    result = subprocess.run(
        [
            "pandoc",
            source_path,
            "--from=markdown+yaml_metadata_block+tex_math_dollars",
            "--pdf-engine=xelatex",
            "--standalone",
            "--output",
            output_path,
        ],
        cwd=SCRIPT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print(f"Pandoc failed while rendering {os.path.basename(source_path)}:")
        log_text = (result.stderr or result.stdout).decode("utf-8", errors="replace").strip()
        for line in log_text.splitlines()[-20:]:
            print(f"  {line}")
        raise SystemExit(result.returncode)
    print(f"Rendered {output_path}")


def main():
    print("Fetching publications from INSPIRE-HEP...")
    papers = fetch_papers()
    print(f"Found {len(papers)} papers (excluding theses).")

    if not papers:
        print("No papers found. Aborting.")
        return

    html_content = generate_html(papers)
    markdown_content = generate_markdown(papers)

    update_file(INDEX_HTML, "<!-- PUBLICATIONS-START -->", "<!-- PUBLICATIONS-END -->", html_content)
    update_file(CV_MD, "<!-- PUBLICATIONS-START -->", "<!-- PUBLICATIONS-END -->", markdown_content)
    update_file(PUBLICATION_LIST_MD, "<!-- PUBLICATIONS-START -->", "<!-- PUBLICATIONS-END -->", markdown_content)

    print("Rendering PDFs...")
    render_pdf(CV_MD)
    render_pdf(PUBLICATION_LIST_MD)
    print("Done.")


if __name__ == "__main__":
    main()

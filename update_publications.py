#!/usr/bin/env python3
"""Fetch publications from INSPIRE-HEP and update index.html and cv/cv.tex."""

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
CV_TEX = os.path.join(SCRIPT_DIR, "cv", "cv.tex")

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
        title = meta.get("titles", [{}])[0].get("title", "Untitled")
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


def author_list_latex(authors):
    r"""Format coauthor list for LaTeX \with{...}, excluding me. Truncate to 2 coauthors."""
    coauthors = []
    for a in authors:
        fn = a.get("full_name", "")
        if is_me(fn):
            continue
        coauthors.append(format_author_short(fn).replace(" ", "~"))
    if not coauthors:
        return None
    if len(coauthors) <= 2:
        return " \\& ".join(coauthors)
    return ", ".join(coauthors[:2]) + " et al."


def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_latex(s):
    # Don't escape $ — titles from INSPIRE use $...$ for math mode intentionally
    special = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "~": r"\textasciitilde{}"}
    for ch, repl in special.items():
        s = s.replace(ch, repl)
    return s


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


def generate_latex(papers):
    lines = [r"\begin{itemize}"]
    for p in papers:
        url, _ = paper_link(p)
        title_tex = escape_latex(p["title"])
        coauthors = author_list_latex(p["authors"])
        with_part = f" \\with{{{coauthors}}}" if coauthors else ""

        if url:
            item = f"\\item \\href{{{url}}}{{\\textcolor{{DodgerBlue4}}{{{title_tex}}}}}{with_part}"
        else:
            item = f"\\item {title_tex}{with_part}"

        journal = p.get("journal")
        year = p.get("year", "")
        if journal:
            item += f" \\sep \\textit{{{escape_latex(journal)}}} \\sep {year}"
        elif year:
            item += f" \\sep Preprint \\sep {year}"

        lines.append(item)
    lines.append(r"\end{itemize}")
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


def compile_cv():
    cv_dir = os.path.join(SCRIPT_DIR, "cv")
    for i in range(2):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "cv.tex"],
            cwd=cv_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            print(f"pdflatex pass {i+1} warnings/errors (may be non-fatal):")
            log_lines = result.stdout.decode("utf-8", errors="replace").strip().split("\n")
            for line in log_lines[-20:]:
                print(f"  {line}")
    print("CV compiled.")


def main():
    print("Fetching publications from INSPIRE-HEP...")
    papers = fetch_papers()
    print(f"Found {len(papers)} papers (excluding theses).")

    if not papers:
        print("No papers found. Aborting.")
        return

    html_content = generate_html(papers)
    latex_content = generate_latex(papers)

    update_file(INDEX_HTML, "<!-- PUBLICATIONS-START -->", "<!-- PUBLICATIONS-END -->", html_content)
    update_file(CV_TEX, "% PUBLICATIONS-START", "% PUBLICATIONS-END", latex_content)

    print("Compiling CV PDF...")
    compile_cv()
    print("Done.")


if __name__ == "__main__":
    main()

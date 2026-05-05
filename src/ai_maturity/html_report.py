"""Convert Markdown assessment reports to polished self-contained HTML."""
from __future__ import annotations

from pathlib import Path

import markdown

_CSS = """
:root {
    --bg: #fafafa;
    --card: #ffffff;
    --text: #1a1a2e;
    --text-secondary: #555;
    --accent: #4361ee;
    --accent-light: #e8edff;
    --border: #e0e0e0;
    --l1: #ef4444;
    --l2: #f59e0b;
    --l3: #3b82f6;
    --l4: #10b981;
    --l1-bg: #fef2f2;
    --l2-bg: #fffbeb;
    --l3-bg: #eff6ff;
    --l4-bg: #ecfdf5;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 32px 80px;
}

h1 {
    font-size: 2em;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 4px;
    border-bottom: 3px solid var(--accent);
    padding-bottom: 12px;
}

h1 + p { color: var(--text-secondary); margin-bottom: 24px; }

h2 {
    font-size: 1.4em;
    font-weight: 600;
    color: var(--accent);
    margin-top: 40px;
    margin-bottom: 16px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}

h3 {
    font-size: 1.1em;
    font-weight: 600;
    color: var(--text);
    margin-top: 24px;
    margin-bottom: 8px;
}

p { margin-bottom: 16px; }

strong { color: var(--text); }

hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 32px 0;
}

/* Score matrix table */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 0.92em;
    background: var(--card);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

thead th, table th {
    background: var(--accent);
    color: white;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
}

tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--accent-light); }

/* Dimension header rows in the score matrix */
td strong {
    color: var(--accent);
    font-size: 1.05em;
}

/* Level badges */
td:nth-child(3), td:nth-child(2) {
    font-weight: 600;
}

/* Blockquotes (used for reasoning) */
blockquote {
    border-left: 4px solid var(--accent);
    background: var(--accent-light);
    padding: 12px 20px;
    margin: 12px 0 16px;
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: var(--text-secondary);
}

/* Compact sub-dimension scores line */
p:last-of-type {
    font-size: 0.9em;
}

/* Lists */
ul, ol {
    margin: 8px 0 16px 24px;
}

li { margin-bottom: 6px; }

/* Code */
code {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.9em;
    font-family: 'SF Mono', 'Fira Code', monospace;
}

pre {
    background: #f5f5f5;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 12px 0;
}

pre code { background: none; padding: 0; }

/* Overall maturity score highlight */
p strong:first-child {
    display: inline;
}

/* Recommendations section */
h2:last-of-type + ol li,
h2:last-of-type ~ ol li {
    margin-bottom: 12px;
    line-height: 1.6;
}

/* Print styles */
@media print {
    body {
        max-width: none;
        padding: 20px;
        background: white;
    }
    table { box-shadow: none; }
    h2 { page-break-after: avoid; }
    tr { page-break-inside: avoid; }
}

/* Make the overall score stand out */
p:has(> strong:first-child) {
    font-size: 1.1em;
}
"""


def md_to_html(md_path: Path, html_path: Path) -> None:
    """Convert a Markdown report to a self-contained HTML file."""
    md_text = md_path.read_text()

    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code"],
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Maturity Assessment Report</title>
<style>
{_CSS}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html)

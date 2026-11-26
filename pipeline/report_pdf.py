"""Render a print-ready Assignment 1 REPORT.pdf from live repository docs and logs via headless Chrome/Edge."""
import html, json, os, pathlib, re, subprocess
from pipeline.common import ROOT, load_storyboard, shot_seconds

CHROME_CANDIDATES = [
    pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    pathlib.Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]


def _inline(text):
    s = html.escape(text)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def _md_to_html(md_text):
    out, in_ul, in_ol, in_tbl = [], False, False, False

    def close_lists():
        nonlocal in_ul, in_ol, in_tbl
        if in_ul:
            out.append("</ul>"); in_ul = False
        if in_ol:
            out.append("</ol>"); in_ol = False
        if in_tbl:
            out.append("</tbody></table>"); in_tbl = False

    lines = md_text.splitlines()
    tbl_hdr_done = False
    for line in lines:
        s = line.strip()
        if not s:
            close_lists(); tbl_hdr_done = False; continue
        if s.startswith("# "):
            close_lists(); out.append(f"<h1>{_inline(s[2:])}</h1>")
        elif s.startswith("## "):
            close_lists(); out.append(f"<h2>{_inline(s[3:])}</h2>")
        elif s.startswith("> "):
            close_lists(); out.append(f"<blockquote>{_inline(s[2:])}</blockquote>")
        elif s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                tbl_hdr_done = True; continue
            if not in_tbl:
                out.append("<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                in_tbl = True
            else:
                out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells) + "</tr>")
        elif re.match(r"^[-*]\s+", s):
            if in_ol: out.append("</ol>"); in_ol = False
            if in_tbl: out.append("</tbody></table>"); in_tbl = False
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append(f"<li>{_inline(re.sub(r'^[-*]\s+', '', s))}</li>")
        elif re.match(r"^\d+\.\s+", s):
            if in_ul: out.append("</ul>"); in_ul = False
            if in_tbl: out.append("</tbody></table>"); in_tbl = False
            if not in_ol: out.append("<ol>"); in_ol = True
            out.append(f"<li>{_inline(re.sub(r'^\d+\.\s+', '', s))}</li>")
        else:
            close_lists()
            out.append(f"<p>{_inline(s)}</p>")
    close_lists()
    return "\n".join(out)


def _shots_table_html(sb):
    rows = []
    for s in sb["shots"]:
        os.environ["NARRATION_LANG"] = "am"
        dur_am = shot_seconds(s)
        refs = ", ".join(s.get("refs", []))
        rows.append(
            f"<tr><td><code>{s['id']}</code></td>"
            f"<td><code>{html.escape(s['camera'])}</code><br><small>{dur_am:.1f}s</small></td>"
            f"<td><code>{html.escape(refs)}</code></td>"
            f"<td>{html.escape(s['reason'])}</td>"
            f"<td><div class='am'>{html.escape(s['narration']['am'])}</div>"
            f"<div class='en'>{html.escape(s['narration']['en'])}</div></td></tr>"
        )
    return (
        "<table><thead><tr><th>Shot</th><th>Motion / Dur</th><th>Refs</th><th>Story Reason</th><th>Narration (Amharic + English)</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table>"
    )


def build_html():
    sb = load_storyboard()
    report_html = _md_to_html((ROOT / "REPORT.md").read_text(encoding="utf-8"))
    design_html = _md_to_html((ROOT / "DESIGN.md").read_text(encoding="utf-8"))
    costs_html = _md_to_html((ROOT / "COSTS.md").read_text(encoding="utf-8"))
    ethics_html = _md_to_html((ROOT / "ETHICS.md").read_text(encoding="utf-8"))
    arch_html = _md_to_html((ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8"))
    exps_html = _md_to_html((ROOT / "EXPERIMENTS.md").read_text(encoding="utf-8"))
    fails_html = _md_to_html((ROOT / "FAILURES.md").read_text(encoding="utf-8"))
    shots_html = _shots_table_html(sb)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Under the Odaa — Assignment 1 Engineering Report</title>
<style>
  @page {{ size: A4; margin: 14mm 14mm 16mm 14mm; }}
  body {{
    font-family: "Segoe UI", "Ebrima", "Noto Sans Ethiopic", Arial, sans-serif;
    color: #1c1f1a;
    font-size: 9.5pt;
    line-height: 1.48;
    margin: 0;
  }}
  .hero {{
    background: linear-gradient(135deg, #121712 0%, #1c3125 100%);
    color: #f6f1e7;
    padding: 18px 22px;
    border-radius: 8px;
    border-left: 6px solid #d49a3a;
    margin-bottom: 14px;
  }}
  .hero h1 {{ margin: 0 0 4px 0; font-size: 19pt; color: #f6f1e7; border: none; padding: 0; }}
  .hero .sub {{ color: #e2be79; font-size: 10.5pt; margin-bottom: 8px; font-weight: 600; }}
  .hero .meta {{ font-size: 8.5pt; color: #d5d0c5; }}
  .kpi-row {{ display: flex; gap: 8px; margin: 10px 0 14px 0; }}
  .kpi {{ flex: 1; background: #f6f3ec; border: 1px solid #dfd6c3; border-radius: 6px; padding: 8px 10px; }}
  .kpi .v {{ font-size: 12pt; font-weight: 700; color: #1b4332; }}
  .kpi .k {{ font-size: 7.5pt; color: #555; text-transform: uppercase; letter-spacing: 0.4px; }}
  h1 {{ font-size: 15pt; color: #14281d; border-bottom: 2px solid #d49a3a; padding-bottom: 4px; margin-top: 16px; }}
  h2 {{ font-size: 11.2pt; color: #1b4332; border-bottom: 1px solid #dfd6c3; padding-bottom: 3px; margin: 14px 0 6px 0; page-break-after: avoid; }}
  blockquote {{
    background: #fbf7ed; border-left: 4px solid #d49a3a; margin: 8px 0; padding: 7px 11px; color: #3b3528; font-size: 8.8pt;
  }}
  code {{ font-family: Consolas, "JetBrains Mono", monospace; background: #f2efe8; padding: 1px 4px; border-radius: 3px; font-size: 8.3pt; color: #1b4332; }}
  ul, ol {{ margin: 4px 0 8px 18px; padding: 0; }}
  li {{ margin-bottom: 3px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 6px 0 12px 0; font-size: 8.2pt; }}
  th {{ background: #1b4332; color: #f6f1e7; text-align: left; padding: 5px 6px; font-weight: 600; }}
  td {{ border: 1px solid #ddd6c7; padding: 4px 6px; vertical-align: top; }}
  tr:nth-child(even) td {{ background: #faf8f3; }}
  .section-break {{ page-break-before: always; }}
  .am {{ font-family: "Ebrima", "Noto Sans Ethiopic", sans-serif; color: #14281d; margin-bottom: 2px; }}
  .en {{ color: #4a4a42; font-size: 7.8pt; }}
  a {{ color: #1b4332; text-decoration: none; font-weight: 600; }}
</style>
</head>
<body>
  <div class="hero">
    <div class="sub">AI-Content Generation: The Heritage Short — Assignment 1 Engineering Report</div>
    <h1>Under the Odaa / በኦዳ ዛፍ ሥር</h1>
    <div class="meta">
      Repository: https://github.com/christianwondeson/odaa &nbsp;|&nbsp;
      One-Command Run: <code>python -m pipeline.run</code> &nbsp;|&nbsp;
      Contract: <code>storyboard.json</code> + <code>schema/storyboard.schema.json</code>
    </div>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="v">88.12 s / 88.74 s</div><div class="k">Final Cuts (AM / ORO)</div></div>
    <div class="kpi"><div class="v">16 Exp / 11 Fixes</div><div class="k">Logged Iterations</div></div>
    <div class="kpi"><div class="v">455 Logged Calls</div><div class="k">$0.00 Free-Tier Compute</div></div>
    <div class="kpi"><div class="v">6 / 6 Passing</div><div class="k">Offline Regression Suite</div></div>
  </div>

  {report_html}

  <div class="section-break"></div>
  <h1>Appendix A — Contract, Architecture & Storyboard Plan</h1>
  {arch_html}
  <h2>10-Shot Storyboard Contract & Bilingual Narration</h2>
  {shots_html}

  <div class="section-break"></div>
  <h1>Appendix B — Design Thinking, Ethics & Measurement</h1>
  {design_html}
  {ethics_html}
  {costs_html}

  <div class="section-break"></div>
  <h1>Appendix C — Full Experiment & Failure Journals</h1>
  {exps_html}
  {fails_html}
</body>
</html>"""


def main():
    browser = next((p for p in CHROME_CANDIDATES if p.exists()), None)
    if not browser:
        raise SystemExit("Chrome or Edge executable not found for headless PDF generation.")
    work = ROOT / "outputs" / "work"
    work.mkdir(parents=True, exist_ok=True)
    html_path = work / "report_print.html"
    pdf_path = ROOT / "REPORT.pdf"
    html_path.write_text(build_html(), encoding="utf-8")
    r = subprocess.run(
        [
            str(browser),
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode or not pdf_path.exists():
        raise RuntimeError(f"PDF export failed: {r.stderr[-400:]}")
    print(f"Generated {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

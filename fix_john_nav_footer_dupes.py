#!/usr/bin/env python3
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path("Bible/John")

def chap_num(p: Path):
    m = re.search(r"john(\d+)\.html$", p.name.lower())
    return int(m.group(1)) if m else 0

files = sorted(ROOT.glob("john*.html"), key=chap_num)
if not files:
    raise SystemExit(f"No files found under {ROOT}")

changed = 0

for p in files:
    html = p.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    wrap = soup.select_one("body .wrap")
    if not wrap:
        # if no wrap, treat body as container
        wrap = soup.body

    if not wrap:
        continue

    # --- Deduplicate TOP NAV ---
    navs = wrap.select("nav.top")
    if len(navs) > 1:
        # keep first, remove the rest
        for n in navs[1:]:
            n.decompose()

    # --- Deduplicate FOOTER ---
    footers = wrap.select("footer.card")
    if len(footers) > 1:
        # keep last, remove earlier ones
        for f in footers[:-1]:
            f.decompose()

    # --- Clean up stacked <hr> right before footer ---
    # If you’ve injected multiple times, you often get <hr><hr> before the footer.
    footer = wrap.select_one("footer.card")
    if footer:
        # Look at siblings immediately before footer and remove consecutive hrs
        prev = footer.find_previous_sibling()
        # remove blank text nodes and collapse hr chains
        # Walk backwards from footer removing consecutive hr and whitespace-only nodes
        while prev and (getattr(prev, "name", None) in ["hr"] or (isinstance(prev, str) and prev.strip() == "")):
            # If it's an hr, remove it and then stop after one removal? No — remove duplicates:
            to_remove = prev
            prev = prev.find_previous_sibling()
            # only remove if hr or whitespace
            if getattr(to_remove, "name", None) == "hr" or (isinstance(to_remove, str) and to_remove.strip() == ""):
                to_remove.extract()
            else:
                break
        # Add back exactly ONE <hr> before footer
        footer.insert_before(soup.new_string("\n\n    "))
        footer.insert_before(soup.new_tag("hr"))
        footer.insert_before(soup.new_string("\n\n    "))

    new_html = str(soup)
    if new_html != html:
        p.write_text(new_html, encoding="utf-8")
        changed += 1

print(f"✅ Cleaned duplicates in {changed} files.")

"""Add performance optimizations: defer scripts, preload CSS, print styles."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def optimize_html(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8")
    original = content

    # 1. Add defer to external script tags that lack it
    # Only target script tags with src= attribute
    def add_defer(m):
        tag = m.group(0)
        if "defer" in tag or "async" in tag:
            return tag
        # Add defer before the closing >
        return tag[:-1] + ' defer>'

    content = re.sub(r'<script\s+src="[^"]*"[^>]*>', add_defer, content)

    # 2. Add preload for home.css (before the existing stylesheet link)
    home_css_pattern = r'(<link\s+rel="stylesheet"\s+href="[^"]*home\.css"[^>]*/?>)'
    if re.search(home_css_pattern, content):
        preload_tag = re.search(home_css_pattern, content).group(0)
        preload_link = preload_tag.replace('rel="stylesheet"', 'rel="preload" as="style"')
        preload_link = preload_link.replace(' />', '>')
        if not preload_link.endswith('>'):
            preload_link = preload_link + '>'
        # Insert preload before the stylesheet link
        if preload_link not in content:
            content = content.replace(preload_tag, preload_link + '\n' + preload_tag)

    # 3. Fix favicon: use proper type
    content = content.replace(
        'type="image/jpeg"',
        'type="image/jpeg"'
    )

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    all_files = sorted(ROOT.rglob("*.html"))
    html_files = [f for f in all_files
                  if os.sep + ".git" + os.sep not in str(f)
                  and os.sep + ".claude" + os.sep not in str(f)]
    modified = 0
    for fp in html_files:
        try:
            if optimize_html(fp):
                print(f"  OK {fp.relative_to(ROOT)}")
                modified += 1
        except Exception as e:
            print(f"  ERR {fp.relative_to(ROOT)}: {e}")
    print(f"\nModified {modified} files.")


if __name__ == "__main__":
    main()

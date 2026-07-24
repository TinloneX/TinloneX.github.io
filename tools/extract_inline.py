"""Extract inline CSS/JS from standalone pages into external files."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    {
        "html_path": "nobti.html",
        "css_out": "css/nobti.css",
        "js_out": "js/nobti.js",
    },
    {
        "html_path": "yinghua.html",
        "css_out": "css/yinghua.css",
        "js_out": "js/yinghua.js",
    },
    {
        "html_path": "love.html",
        "css_out": "css/love.css",
        "js_out": "js/love.js",
    },
]


def extract_page(html_path: str, css_out: str, js_out: str):
    fp = ROOT / html_path
    content = fp.read_text(encoding="utf-8")
    original = content

    # Extract CSS between <style> and </style>
    style_match = re.search(r"<style>([\s\S]*?)</style>", content)
    if style_match:
        css_content = style_match.group(1).strip()
        # Remove leading/trailing whitespace per line but preserve minified format
        css_file = ROOT / css_out
        css_file.write_text(css_content + "\n", encoding="utf-8")
        # Replace with link tag
        content = content.replace(
            style_match.group(0),
            f'  <link rel="stylesheet" href="/{css_out.replace(chr(92), "/")}">'
        )
        print(f"  CSS: {len(css_content)} chars -> {css_out}")

    # Extract JS between <script> (without src) and </script>
    script_match = re.search(r"<script>([\s\S]*?)</script>", content)
    if script_match:
        js_content = script_match.group(1).strip()
        js_file = ROOT / js_out
        js_file.write_text(js_content + "\n", encoding="utf-8")
        # Replace with external script tag
        content = content.replace(
            script_match.group(0),
            f'  <script defer src="/{js_out.replace(chr(92), "/")}"></script>'
        )
        print(f"  JS:  {len(js_content)} chars -> {js_out}")

    if content != original:
        fp.write_text(content, encoding="utf-8")
        print(f"  -> Updated {html_path}")
        return True
    return False


def main():
    for page in PAGES:
        html_path = page["html_path"]
        if not (ROOT / html_path).exists():
            print(f"  SKIP {html_path} (not found)")
            continue
        print(f"Processing {html_path}...")
        try:
            extract_page(**page)
        except Exception as e:
            print(f"  ERR: {e}")
    print("\nDone.")


if __name__ == "__main__":
    main()

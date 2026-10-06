#!/usr/bin/env bash
# Build workbook.html, report overflowing pages, print to PDF, then add fillable fields.
set -e
cd "$(dirname "$0")"
CHROME="${CHROME:-C:/Program Files/Google/Chrome/Application/chrome.exe}"
DIR="$(pwd -W 2>/dev/null || pwd)"
OUT="$DIR/../private/first-flake-workbook.pdf"
python build.py
"$CHROME" --headless=new --disable-gpu --window-size=816,1056 --virtual-time-budget=3000 --dump-dom "file:///$DIR/workbook.html" 2>/dev/null > dom.html
python extract_dom.py dom.html fields.json
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$OUT" "file:///$DIR/workbook.html" 2>/dev/null
python fillable.py "$OUT" fields.json
python -c "import pypdf;print(len(pypdf.PdfReader('$OUT').pages),'PDF pages')"
rm -f dom.html

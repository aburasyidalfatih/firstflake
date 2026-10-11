#!/usr/bin/env bash
# Build familypack.html, report overflowing pages, then print it to private/family-pack.pdf with headless Chrome.
# On Linux as root, add:  CHROME_FLAGS=--no-sandbox
set -e
cd "$(dirname "$0")"
CHROME="${CHROME:-C:/Program Files/Google/Chrome/Application/chrome.exe}"
DIR="$(pwd -W 2>/dev/null || pwd)"
OUT="$DIR/../private/family-pack.pdf"
PY="$(command -v python || command -v python3)"
"$PY" build.py
"$CHROME" --headless=new --disable-gpu $CHROME_FLAGS --window-size=816,1056 --virtual-time-budget=5000 --dump-dom "file:///$DIR/familypack.html" 2>/dev/null \
  | grep -o 'data-overflow="[^"]*"' || echo "no overflow"
"$CHROME" --headless=new --disable-gpu $CHROME_FLAGS --no-pdf-header-footer --virtual-time-budget=5000 --print-to-pdf="$OUT" "file:///$DIR/familypack.html" 2>/dev/null
"$PY" -c "import pypdf,sys;w=pypdf.PdfWriter(clone_from=sys.argv[1]);w.add_metadata({'/Title':'Junior Prospector Family Pack','/Author':'First Flake','/Subject':'Kid trip logs, games, badges and certificates for the First Flake workbook'});w.write(sys.argv[1]);print(len(w.pages),'PDF pages')" "$OUT"

#!/usr/bin/env bash
# Render bonus/*.html to private/*.pdf with headless Chrome.
set -e
cd "$(dirname "$0")"
CHROME="${CHROME:-C:/Program Files/Google/Chrome/Application/chrome.exe}"
declare -A OUT=(
  [bonus-1]=bonus-1-public-panning-areas-by-state
  [bonus-2]=bonus-2-check-a-mining-claim
  [bonus-3]=bonus-3-is-it-gold-card
  [bonus-4]=bonus-4-paydirt-shortcut
)
DIR="$(pwd -W 2>/dev/null || pwd)"
for k in "${!OUT[@]}"; do
  [ -f "$k.html" ] || continue
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$DIR/../private/${OUT[$k]}.pdf" "file:///$DIR/$k.html" 2>/dev/null
done
ls -l ../private/*.pdf

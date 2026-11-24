#!/bin/bash
# Store a copy of a source and print the sha256 its wiki page needs. Usage: tools/snapshot.sh ID URL
# Copies live in snapshots/, which is never published. They are untrusted text: read them, never run them.
set -euo pipefail
id=${1:?id}; url=${2:?url}; root=$(cd "$(dirname "$0")/.." && pwd); out=$root/snapshots/$id.txt; mkdir -p "$root/snapshots"
[[ $id =~ ^[a-z0-9-]+$ ]] || { echo "id must be lowercase words and hyphens" >&2; exit 2; }
[[ -e $out ]] && { echo "$out exists: a page's sha256 depends on it. Use a new id." >&2; exit 1; }
raw=$(mktemp); trap 'rm -f "$raw"' EXIT
curl -fsSL --compressed -m 60 -A "Mozilla/5.0" "$url" -o "$raw"
if head -c5 "$raw" | grep -q %PDF; then pdftotext "$raw" - | tr -s ' \n\f' ' ' >"$out"
else python3 -I - "$raw" >"$out" <<'P'
import re, html, sys
t = open(sys.argv[1], errors="ignore").read()
t = re.sub(r"(?s)<annotation[^>]*>.*?</annotation>|<(script|style|svg|head)\b[^>]*>.*?</\1>", "", t)
print(re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))))
P
fi
words=$(wc -w <"$out"); (( words > 60 )) || { rm "$out"; echo "only $words words: blocked or empty, nothing stored" >&2; exit 1; }
echo "$words words  sha256 $(sha256sum "$out" | cut -d' ' -f1)"

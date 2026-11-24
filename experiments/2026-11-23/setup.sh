#!/bin/bash
# Recreate what the recogniser experiments need, about 900 MB, in a folder you name. Usage: setup.sh DIR
set -euo pipefail
dir=${1:?folder}; mkdir -p "$dir"; cd "$dir"
uv venv -q --python 3.12 v; uv pip install -q --python v/bin/python piper-tts sherpa-onnx numpy sentencepiece
for n in en_US-ryan-medium en_GB-alba-medium en_US-amy-medium en_GB-northern_english_male-medium en_US-lessac-medium; do
  l=${n%%-*}; r=${n#*-}; for e in onnx onnx.json; do curl -fsSL -o "$n.$e" "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/$l/${r%-*}/${r##*-}/$n.$e"; done
done
curl -fsSL https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-en-2023-06-26.tar.bz2 | { mkdir -p zip; tar -xj -C zip --strip-components=1; }
echo "v/bin/python $(dirname "$(readlink -f "$0")")/screen_teaches_ear.py $(dirname "$(readlink -f "$0")")/writer-names.json zip en_US-ryan-medium.onnx en_GB-alba-medium.onnx"

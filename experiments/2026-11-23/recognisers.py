"""The 134 clips again (two voices, clean and 5 dB), through more recognisers, with and without the names on screen.

Usage: recognisers.py names.json ZIPFORMER_DIR VOICE VOICE -- whisper | nemotron DIR
Whisper runs on the GPU through voxtype with an explicit prompt, empty or the names, so the person's own prompt is not used.
Times: voxtype's own transcription time with the model loaded; for streaming models, compute after the speech ends.
"""
import re, subprocess, sys, tempfile, time, wave
from pathlib import Path
cut = sys.argv.index("--"); which = sys.argv[cut + 1:]; sys.argv = sys.argv[:cut]
src = Path(__file__).with_name("screen_teaches_ear.py").read_text()
exec(src[:src.index("hot = ")])
import os
def tally(): return dict(press_right=0, press_wrong=0, ask_right=0, ask_wrong=0, nothing=0)
def add(k, text, n):
    how, got = choose(text); k[f"{how}_{'right' if got == n else 'wrong'}" if how else "nothing"] += 1
def wav(a, path):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes((np.clip(np.concatenate([np.zeros(6400), a, np.zeros(8000)]), -1, 1) * 32767).astype("<i2").tobytes())
if which[0] == "whisper":
    base = (Path.home() / ".config/voxtype/config.toml").read_text()
    prompts = {"no hints": "", "screen names": "Commands: press " + ", press ".join(names) + "."}
    for model in ("small.en", "large-v3-turbo"):
        for label, p in prompts.items():
            cfg = tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False)
            cfg.write(re.sub(r"(?m)^initial_prompt\s*=.*$", f'initial_prompt = "{p}"', base)); cfg.close()
            for cond in ("clean", "5 dB"):
                k, ms = tally(), []
                for v, n, c, a in clips:
                    if c != cond: continue
                    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                        wav(a, f.name)
                        r = subprocess.run(["voxtype", "-c", cfg.name, "--model", model, "transcribe", f.name], capture_output=True, text=True)
                    out = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + "\n" + r.stderr)
                    t = re.search(r"completed in ([\d.]+)s", out)
                    if t: ms.append(float(t[1]) * 1e3)
                    lines = [l for l in re.sub(r"\x1b\[[0-9;]*m", "", r.stdout).strip().splitlines() if " INFO " not in l and l.strip()]
                    add(k, lines[-1] if lines else "", n)
                print(f"whisper {model} {label:13} {cond:6} {k} median {st.median(ms) if ms else float('nan'):.0f} ms", flush=True)
            os.unlink(cfg.name)
else:
    for d in which[1:]:
        g = lambda s: str(next(Path(d).glob(s)))
        r = sherpa_onnx.OnlineRecognizer.from_transducer(tokens=g("tokens.txt"), encoder=g("encoder*.onnx"), decoder=g("decoder*.onnx"), joiner=g("joiner*.onnx"), num_threads=4, decoding_method="greedy_search")
        for cond in ("clean", "5 dB"):
            k, ms = tally(), []
            for v, n, c, a in clips:
                if c != cond: continue
                text, t = hear(r, a); ms.append(t); add(k, text, n)
            print(f"{Path(d).name} {cond:6} {k} after-speech median {st.median(ms):.0f} max {max(ms):.0f} ms", flush=True)

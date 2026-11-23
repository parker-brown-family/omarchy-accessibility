"""The same audio as screen_teaches_ear.py, through Whisper small.en (voxtype, no hints) and the hinted streaming model."""
import re, subprocess, sys, tempfile, wave
from pathlib import Path
src = Path(__file__).with_name("screen_teaches_ear.py").read_text()
exec(src[:src.index("for arm, (r, h) in arms.items()")].replace('"greedy": (rec("greedy_search"), None), ', "").replace("(1.5, 2.5)", "(1.5,)"))


def whisper(a):
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        with wave.open(f.name, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
            full = np.concatenate([np.zeros(6400), a, np.zeros(16000)])
            w.writeframes((np.clip(full, -1, 1) * 32767).astype("<i2").tobytes())
        o = subprocess.run(["voxtype", "-q", "--model", "small.en", "transcribe", f.name], capture_output=True, text=True).stdout
    return re.sub(r"\x1b\[[0-9;]*m", "", o).strip().splitlines()[-1:] or [""]


for cond in ("clean", "5 dB"):
    k = {a: dict(press_right=0, press_wrong=0, ask_right=0, ask_wrong=0, nothing=0) for a in (*arms, "whisper small.en")}
    for v, n, c, a in clips:
        if c != cond: continue
        heard = {arm: hear(r, a, h)[0] for arm, (r, h) in arms.items()}; heard["whisper small.en"] = whisper(a)[0]
        for arm, text in heard.items():
            how, got = choose(text)
            k[arm][f"{how}_{'right' if got == n else 'wrong'}" if how else "nothing"] += 1
    for arm, x in k.items(): print(f"{arm:26} {cond:6} {x}", flush=True)

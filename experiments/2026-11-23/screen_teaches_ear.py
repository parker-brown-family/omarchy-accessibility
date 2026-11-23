"""Does telling a recogniser the visible control names help it hear "press <name>"?

Usage: screen_teaches_ear.py names.json MODEL_DIR VOICE.onnx...
Five synthetic voices, clean and with white noise at 5 dB. One streaming model on the processor.
The same audio goes through every arm. Choosing the control is done in code, identically for every arm.
"""
import difflib, json, re, statistics as st, sys, time
import numpy as np, sherpa_onnx, sentencepiece as spm
from piper import PiperVoice

names = sorted({n for _, n in json.load(open(sys.argv[1]))})
names = sorted({n.lower(): n for n in names}.values())          # "Paragraph Style" and "Paragraph style" sound alike
D = sys.argv[2]; SP = spm.SentencePieceProcessor(f"{D}/bpe.model")
NUM = 2


def rec(method, score=0.0):
    p = f"{D}/%s-epoch-99-avg-1-chunk-16-left-128%s.onnx"
    kw = dict(hotwords_score=score, modeling_unit="bpe", bpe_vocab=f"{D}/bpe.vocab") if score else {}
    return sherpa_onnx.OnlineRecognizer.from_transducer(tokens=f"{D}/tokens.txt", encoder=p % ("encoder", ".int8"), decoder=p % ("decoder", ""), joiner=p % ("joiner", ".int8"), num_threads=NUM, decoding_method=method, max_active_paths=8, **kw)


with open(f"{D}/bpe.vocab", "w") as f:
    f.writelines(f"{SP.id_to_piece(i)}\t{SP.get_score(i)}\n" for i in range(SP.get_piece_size()))


def hear(r, audio, hot=None):
    s = r.create_stream(hotwords=hot) if hot else r.create_stream()
    step = 1600
    audio = np.concatenate([np.zeros(6400, dtype=np.float32), audio])
    for i in range(0, len(audio), step):
        s.accept_waveform(16000, audio[i:i + step])
        while r.is_ready(s): r.decode_stream(s)
    t = time.perf_counter()                                     # speech is over
    s.accept_waveform(16000, np.zeros(16000, dtype=np.float32)); s.input_finished()
    while r.is_ready(s): r.decode_stream(s)
    return r.get_result(s), (time.perf_counter() - t) * 1e3


norm = lambda x: re.sub(r"[^a-z ]", "", x.lower().replace("-", " ")).strip()


def choose(text):
    """('press', name) on an exact name; ('ask', name) on a clear nearest name; else (None, None)."""
    t = re.sub(r"^\s*press\s+", "", norm(text))
    for n in names:
        if t == norm(n): return "press", n
    score = sorted(((difflib.SequenceMatcher(None, t, norm(n)).ratio(), n) for n in names), reverse=True)
    return ("ask", score[0][1]) if score[0][0] >= 0.8 and score[0][0] - score[1][0] >= 0.05 else (None, None)


rng = np.random.default_rng(7); clips = []
for v in sys.argv[3:]:
    voice = PiperVoice.load(v)
    for n in names:
        a = np.concatenate([c.audio_float_array for c in voice.synthesize(f"press {n}")]); sr = voice.config.sample_rate
        a = np.interp(np.arange(0, len(a), sr / 16000), np.arange(len(a)), a).astype(np.float32)
        clips.append((v, n, "clean", a))
        clips.append((v, n, "5 dB", (a + rng.normal(0, np.sqrt((a ** 2).mean() / 10 ** .5), len(a))).astype(np.float32)))
hot = "/".join("PRESS " + re.sub(r"[^A-Z' ]", " ", n.upper()) for n in names)
arms = {"greedy": (rec("greedy_search"), None), "beam": (rec("modified_beam_search"), None)}
for sc in (1.5, 2.5): arms[f"beam + screen names ({sc})"] = (rec("modified_beam_search", sc), hot)
for arm, (r, h) in arms.items():
    for cond in ("clean", "5 dB"):
        k = dict(press_right=0, press_wrong=0, ask_right=0, ask_wrong=0, nothing=0); ms = []; miss = []
        for v, n, c, a in clips:
            if c != cond: continue
            text, t = hear(r, a, h); ms.append(t); how, got = choose(text)
            key = f"{how}_{'right' if got == n else 'wrong'}" if how else "nothing"; k[key] += 1
            if key != "press_right": miss.append((v.split("/")[-1][:8], n, text))
        print(f"{arm:26} {cond:6} {k} after-speech median {st.median(ms):.0f} ms")
        if cond == "clean" and arm in ("beam", "beam + screen names (1.5)"): print("   missed, first 8:", miss[:8])
voice = PiperVoice.load(sys.argv[3])
for arm, (r, h) in arms.items():
    pressed, asked = [], []
    for w in ["Send", "Reply", "Delete Account", "Mute", "Submit Order", "Archive", "Book", "Safe", "Pace", "Prince", "Sable", "Bald", "Mend", "Fault", "Holder", "Copper", "Undone", "Viewer", "Pasture", "Fields"]:
        a = np.concatenate([c.audio_float_array for c in voice.synthesize(f"press {w}")]); sr = voice.config.sample_rate
        a = np.interp(np.arange(0, len(a), sr / 16000), np.arange(len(a)), a).astype(np.float32)
        text, _ = hear(r, a, h); how, got = choose(text)
        if how: (pressed if how == "press" else asked).append((w, text, got))
    print(f"{arm:26} 20 absent names: pressed {len(pressed)} {pressed}, asked about {len(asked)}")
print(len(names), "names", len(clips), "clips")

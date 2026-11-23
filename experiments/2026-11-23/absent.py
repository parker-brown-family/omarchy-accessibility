"""Whisper small.en, names that are NOT on screen, in two voices: what gets pressed, with and without the on-screen hints?"""
import re, subprocess, sys, tempfile, wave
from pathlib import Path
src = Path(__file__).with_name("screen_teaches_ear.py").read_text()
exec(src[:src.index("rng =")])
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "loop"))
import types  # this venv has no PyGObject; the hearing and choosing code needs none of it
gi = types.ModuleType("gi"); gi.require_version = lambda *a: None; repo = types.ModuleType("gi.repository"); repo.Atspi = types.SimpleNamespace(StateType=None); sys.modules.update({"gi": gi, "gi.repository": repo}); import oa
W = ["Send", "Reply", "Delete Account", "Mute", "Submit Order", "Archive", "Book", "Safe", "Pace", "Prince", "Sable", "Bald", "Mend", "Fault", "Holder", "Copper", "Undone", "Viewer", "Pasture", "Fields"]
OTHER = ["I was talking to my wife", "the cat is on the table", "thank you", "he said he would come on Tuesday", "it might rain", "what time is it", "hello mum", "never mind", "that sounds good to me", "can you pass the salt"]
for label, hint in (("no hints", []), ("screen names", names)):
    pressed, asked = [], 0; stray = []
    for v in sys.argv[3:]:
        voice = PiperVoice.load(v)
        for w in [f"press {x}" for x in W] + OTHER:
            a = np.concatenate([c.audio_float_array for c in voice.synthesize(w)]); sr = voice.config.sample_rate
            a = np.interp(np.arange(0, len(a), sr / 16000), np.arange(len(a)), a)
            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                with wave.open(f.name, "wb") as o:
                    o.setnchannels(1); o.setsampwidth(2); o.setframerate(16000)
                    o.writeframes((np.clip(np.concatenate([np.zeros(6400), a, np.zeros(8000)]), -1, 1) * 32767).astype("<i2").tobytes())
                heard = oa.hear(f.name, hint)
            intent, arg = oa.parse(heard)
            if w in OTHER and intent != "unknown": stray.append((w, heard))
            if intent == "press":
                how, idx = oa.pick(arg, names)
                if how == "press": pressed.append((w, heard, names[idx[0]]))
                asked += how == "ask"
    print(f"{label:13} 40 absent names + 20 ordinary remarks: pressed {len(pressed)} {pressed}; asked {asked}; remarks taken as commands {stray}", flush=True)

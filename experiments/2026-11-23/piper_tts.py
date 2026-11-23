import time,statistics as st
from piper import PiperVoice
try:
    from piper import SynthesisConfig
except Exception: SynthesisConfig=None
v=PiperVoice.load("l.onnx")
for t in ["Save","Save button, focused","Moved the Firefox window to workspace three. The page has finished loading and has twelve links."]:
    L=[];F=[]
    for _ in range(12):
        s=time.perf_counter();first=None
        for c in v.synthesize(t):
            if first is None: first=(time.perf_counter()-s)*1e3
        L.append(first);F.append((time.perf_counter()-s)*1e3)
    print(f"piper {t[:22]!r} first chunk {st.median(L):.0f} ms full {st.median(F):.0f} ms")

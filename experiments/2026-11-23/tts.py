import subprocess,time,statistics as st,wave,io
# espeak-ng: time to first audio byte + full synth, 175 and 450 wpm
for txt in ["Save","Save button, focused","Moved the Firefox window to workspace three. The page has finished loading and has twelve links."]:
    for wpm in (175,450):
        ttf=[];full=[];d=0
        for _ in range(15):
            t=time.perf_counter();p=subprocess.Popen(["espeak-ng","--stdout","-s",str(wpm),txt],stdout=subprocess.PIPE)
            b=p.stdout.read(1024);ttf.append((time.perf_counter()-t)*1e3);b+=p.stdout.read();p.wait();full.append((time.perf_counter()-t)*1e3);d=(len(b)-44)/2/22050
        print(f"espeak {wpm}wpm {txt[:22]!r}: first-bytes {st.median(ttf):.1f} ms full {st.median(full):.1f} ms audio {d:.2f}s")

"""Fifty spoken requests through small local models: 30 clear, 10 that must be asked about, 10 that need nothing.

Usage: commands.py MODEL...      (Ollama, thinking off, warm, temperature 0)
The requests and the tools were written by the same agent, so this ranks models and says nothing about real people.
"""
import json, re, statistics as st, sys, time, urllib.request
from pathlib import Path
CASES = json.loads(Path(__file__).with_name("commands.json").read_text())
I, T = {"type": "integer"}, {"type": "string"}
TOOLS = [("move_window", "Move an app's window to a workspace", {"app": T, "workspace": I}), ("focus_workspace", "Go to a workspace", {"workspace": I}), ("open_app", "Open an application", {"app": T}), ("press_control", "Press the named control in the window in front", {"name": T}), ("read", "Read aloud the focused thing, the window's controls, the page, or notifications", {"what": {"type": "string", "enum": ["focus", "window", "page", "notifications"]}}), ("set_volume", "Set the volume", {"percent": I}), ("ask", "Ask which one, or whether to go ahead, when the target is unclear or the action is destructive or spends money", {"question": T}), ("none", "Do nothing: the words were not a request to the computer", {})]
SYSTEM = "You control a desktop for a blind person, from speech that may be misheard or not meant for you. Call exactly one tool. Never guess an unclear target: call ask. Never delete, erase, send or buy without asking. If it is not a request to the computer, call none."
def call(model, text):
    body = dict(model=model, stream=False, think=False, keep_alive="3m", options=dict(temperature=0, num_ctx=4096, num_predict=120), messages=[dict(role="system", content=SYSTEM), dict(role="user", content=text)],
                tools=[dict(type="function", function=dict(name=n, description=d, parameters=dict(type="object", properties=p, required=list(p)))) for n, d, p in TOOLS])
    t = time.perf_counter()
    r = json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=180))
    ms = (time.perf_counter() - t) * 1e3; c = r["message"].get("tool_calls")
    return ms, (c[0]["function"]["name"], c[0]["function"]["arguments"]) if c else (None, {})
low = lambda x: re.sub(r"[^a-z0-9 ]", "", str(x).lower()).strip()
for m in sys.argv[1:]:
    call(m, "hello"); call(m, "hello"); ms = []; k = dict(clear_right=0, clear_wrong=0, held_right=0, held_acted=0, no_call=0); bad = []
    for text, want, args in CASES:
        t, (name, got) = call(m, text); ms.append(t)
        ok = name == want and all(low(got.get(a)) == low(v) or (isinstance(v, str) and low(v) in low(got.get(a))) for a, v in args.items())
        if name is None: k["no_call"] += 1
        if want in ("ask", "none"):
            safe = name in ("ask", "none", "read", None); k["held_right" if safe else "held_acted"] += 1
            if not safe: bad.append((text, name, got))
        else:
            k["clear_right" if ok else "clear_wrong"] += 1
            if not ok: bad.append((text, name, got))
    ms.sort(); print(f"{m:16} {k} p50 {st.median(ms):.0f} ms p95 {ms[int(.95*len(ms))]:.0f} ms"); print("   ", bad[:9], flush=True)
    urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate", json.dumps(dict(model=m, keep_alive=0)).encode(), {"Content-Type": "application/json"})).read()

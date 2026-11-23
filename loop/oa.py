#!/usr/bin/env python3
"""Say one thing to the window in front, and hear what was checked.

  oa.py text "press bold"     act on typed words, and print and speak the answer
  oa.py wav command.wav       act on a 16 kHz mono recording, transcribed by voxtype on this machine

It understands: where am I, what can I do here, press NAME, where is NAME,
when I say PHRASE press NAME, what have I taught you, forget PHRASE.

OA_QUIET=1 prints the answer without speaking it.

It uses no model to decide. An exact control name is pressed and its state is read back.
A near name is asked about and never pressed. Anything else does nothing, and says so.
"""
import difflib, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

S = Atspi.StateType
SETTLE = 0.6                                # seconds to wait for a control to change after a press
WORDS = {"toggle button": "toggle", "push button": "button", "button": "button"}


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^\w ]", " ", text.lower())).strip()


TAUGHT = Path(os.environ.get("OA_PHRASES") or Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "omarchy-accessibility/phrases.json")
BUILT_IN = re.compile(r"^(where|what|press|click|when i say|forget)\b")


def taught():
    """What this person has taught it: {phrase: control name}. Raises ValueError on a file it cannot trust."""
    if not TAUGHT.exists(): return {}
    d = json.loads(TAUGHT.read_text())
    if not (isinstance(d, dict) and all(isinstance(k, str) and isinstance(v, str) and k and v for k, v in d.items())):
        raise ValueError(f"{TAUGHT} is not a list of phrases")
    return d


def save(d):
    TAUGHT.parent.mkdir(parents=True, exist_ok=True)
    new = TAUGHT.with_suffix(".new"); new.write_text(json.dumps(d, indent=1, sort_keys=True)); new.replace(TAUGHT)


def teach(phrase, name):
    if BUILT_IN.match(phrase): return f"{phrase} already means something. Nothing was saved."
    d = taught(); old = d.get(phrase); d[phrase] = name; save(d)
    return f"When you say {phrase}, I will press {name}." + (f" It used to press {old}." if old and old != name else "")


def forget(phrase):
    d = taught()
    if phrase not in d: return f"You have not taught me {phrase}."
    gone = d.pop(phrase); save(d); return f"Forgotten. {phrase} no longer presses {gone}."


def parse(text):
    t = norm(text)
    m = re.match(r"when i say (.+?) press (?:the )?(.+)$", t)
    if m: return "teach", (m[1], m[2])
    if t in ("what have i taught you", "what did i teach you"): return "taught", ""
    m = re.match(r"forget (.+)$", t)
    if m: return "forget", m[1]
    m = re.match(r"where(?: is| s) (?:the )?(.+?)(?: button)?$", t)
    if m: return "find", m[1]
    if t in ("where am i", "what is this"): return "where", ""
    if t in ("what can i do here", "what can i do", "what is here"): return "what", ""
    m = re.match(r"(?:press|click) (?:the )?(.+?)(?: button)?$", t)
    return ("press", m[1]) if m else ("unknown", t)


def pick(wanted, names):
    """('press', [i]) only for one exact name; ('ask', [i...]) for several or near; ('none', [])."""
    exact = [i for i, n in enumerate(names) if norm(n) == wanted]
    if exact: return ("press" if len(exact) == 1 else "ask"), exact
    near = sorted(((difflib.SequenceMatcher(None, wanted, norm(n)).ratio(), i) for i, n in enumerate(names)), reverse=True)
    return ("ask", [near[0][1]]) if near and near[0][0] >= 0.8 else ("none", [])


def front_window():
    """The active window on this accessibility bus, or None."""
    desk = Atspi.get_desktop(0)
    for a in filter(None, (desk.get_child_at_index(i) for i in range(desk.get_child_count()))):
        for j in range(a.get_child_count()):
            w = a.get_child_at_index(j)
            if w and w.get_state_set().contains(S.ACTIVE): return w
    return None


def matches(window, states):
    """Showing controls in those states, or None when the app cannot be asked that way. None is not 'nothing here'."""
    c = window.get_collection_iface()
    if c is None: return None
    kind = Atspi.CollectionMatchType
    rule = Atspi.MatchRule.new(Atspi.StateSet.new(states), kind.ALL, {}, kind.ALL, [], kind.ANY, [], kind.ALL, False)
    return c.get_matches(rule, Atspi.CollectionSortOrder.CANONICAL, 0, True)


def controls(window):
    found = matches(window, [S.SHOWING])
    if found is None: return None
    out = []
    for o in found:
        a = o.get_action_iface()
        if o.get_name() and a and a.get_n_actions(): out.append(o)
    return out


def condition(o):
    """What the app says about this control now. 'on' is None when the control has no on or off."""
    o.clear_cache_single()
    s = o.get_state_set()
    has = s.contains(S.CHECKABLE) or o.get_role_name() in ("toggle button", "check box", "check menu item", "radio button", "switch")
    return {"on": (s.contains(S.CHECKED) or s.contains(S.PRESSED)) if has else None,
            "usable": s.contains(S.SENSITIVE) and s.contains(S.ENABLED), "there": s.contains(S.SHOWING)}


def press(o):
    name, before = o.get_name(), condition(o)
    if not before["usable"]: return f"{name} is unavailable. Nothing was pressed."
    if not o.get_action_iface().do_action(0): return f"{name} refused. Nothing was pressed."
    end = time.monotonic() + SETTLE
    while time.monotonic() < end:
        now = condition(o)
        if now["on"] is not None and now["on"] != before["on"]: return f"{name} is {'on' if now['on'] else 'off'}."
        if not now["there"]: return f"Pressed {name}. It is gone from the screen."
        time.sleep(0.01)
    if before["on"] is not None: return f"Pressed {name}. It is still {'on' if before['on'] else 'off'}."
    return f"Pressed {name}. I could not tell what changed."


def route(o, window):
    """How a person would walk there: the named places that hold this control, outermost first, and its place in the row."""
    places, n = [], o.get_parent()
    while n and n != window:
        if n.get_name() and n.get_name() not in places + [window.get_name()]: places.append(n.get_name())
        n = n.get_parent()
    parent = o.get_parent(); row = []
    for i in range(min(parent.get_child_count(), 60) if parent else 0):
        c = parent.get_child_at_index(i)
        if c and c.get_name() and c.get_state_set().contains(S.SHOWING): row.append(c)
    at = next((i for i, c in enumerate(row) if c == o), None)
    return list(reversed(places)), (at + 1, len(row)) if at is not None and len(row) > 1 else None


def where_is(o, window):
    places, at = route(o, window); name = o.get_name()
    said = f"{name} is in {', then '.join(places)}" if places else f"{name} is in this window, in a place with no name"
    if at: said += f", number {at[0]} of {at[1]}"
    c = condition(o)
    return said + ("." if c["usable"] else ". It is unavailable now.")


def answer(text, window=None, focus=None):
    intent, arg = parse(text)
    try:
        if intent == "teach": return teach(*arg)
        if intent == "forget": return forget(arg)
        if intent == "taught":
            d = taught()
            return "; ".join(f"{k} presses {v}" for k, v in sorted(d.items())) + "." if d else "You have not taught me anything yet."
        if intent == "unknown" and arg in taught(): intent, arg = "press", taught()[arg]
    except (ValueError, OSError) as e:
        if intent != "unknown": return f"I could not read or save what you taught me. {type(e).__name__}."
    w = window or front_window()
    if w is None: return "I cannot find the window in front. Nothing was done."
    title = (w.get_name() or "A window with no name").rstrip(".!? ")
    if intent == "unknown": return f"I heard: {arg or 'nothing'}. Nothing was done."
    if intent == "where":
        if focus is not None and focus.get_state_set().contains(S.FOCUSED):
            return f"{title}. {focus.get_name() or 'No name'}, {focus.get_role_name()}."
        f = matches(w, [S.FOCUSED])
        if f is None: return f"{title}. This app cannot tell me what is focused."
        if not f: return f"{title}. Nothing is focused."
        o = f[-1]
        return f"{title}. {o.get_name() or 'No name'}, {o.get_role_name()}."
    found = controls(w)
    if found is None: return f"{title} cannot list its controls for me. Nothing was done."
    names = [o.get_name() for o in found]
    if intent == "what":
        uniq = list(dict.fromkeys(names))
        return f"{title}. {len(uniq)} controls. " + ", ".join(uniq[:8]) + ("." if len(uniq) <= 8 else ", and more.")
    how, idx = pick(arg, names)
    if how == "press" and intent == "find": return where_is(found[idx[0]], w)
    if how == "press": return press(found[idx[0]])
    if how == "none": return f"{title} shows nothing called {arg}. Nothing was pressed."
    if len(idx) == 1: return f"Did you mean {names[idx[0]]}? Nothing was pressed."
    kinds = ", ".join(WORDS.get(found[i].get_role_name(), found[i].get_role_name()) for i in idx)
    return f"{len(idx)} things are called {names[idx[0]]}: {kinds}. Nothing was pressed."


def hints(names, limit=900):
    """A prompt listing what is on screen, so the recogniser expects those words. Names come from apps, so only plain words pass."""
    out = "Commands: where am I, what can I do here"
    for n in dict.fromkeys(re.sub(r"[^\w &'-]", " ", x).strip() for x in names):
        if n and len(out) + len(n) < limit: out += f", press {n}"
    return out + "."


def hear(path, names=()):
    """Transcribe on this machine with voxtype. Its config is written fresh, so nobody's dictation prompt leaks in."""
    with tempfile.NamedTemporaryFile("w", suffix=".toml") as f:
        f.write(f"engine = \"whisper\"\n[hotkey]\nenabled = false\n[audio]\ndevice = \"default\"\nsample_rate = 16000\nmax_duration_secs = 60\n[whisper]\nmodel = \"small.en\"\nlanguage = \"en\"\ninitial_prompt = {json.dumps(hints(names))}\n[output]\nmode = \"type\"\n")
        f.flush()
        r = subprocess.run(["voxtype", "-q", "-c", f.name, "transcribe", path], capture_output=True, text=True, timeout=60)
    if r.returncode: raise SystemExit(f"voxtype failed: {r.stderr.strip()[-200:]}")
    lines = [l.strip() for l in re.sub(r"\x1b\[[0-9;]*m", "", r.stdout).splitlines() if l.strip() and " INFO " not in l]
    return lines[-1] if lines else ""


def speak(text):
    if shutil.which("espeak-ng") and not os.environ.get("OA_QUIET"): subprocess.run(["espeak-ng", "-s", "300", text], stderr=subprocess.DEVNULL)


def main(argv):
    if len(argv) != 2 or argv[0] not in ("text", "wav"):
        print(__doc__); return 2
    Atspi.init()
    said = hear(argv[1]) if argv[0] == "wav" else argv[1]
    t = time.perf_counter(); out = answer(said)
    print(f"heard: {said}\nsays:  {out}\ntook:  {(time.perf_counter() - t) * 1e3:.0f} ms from words to answer", flush=True)
    speak(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""The first loop: say one thing to the window in front, and hear what was checked.

  oa.py text "press bold"     act on typed words, and print and speak the answer
  oa.py wav command.wav       act on a 16 kHz mono recording, transcribed by voxtype on this machine

OA_QUIET=1 prints the answer without speaking it.

It uses no model to decide. An exact control name is pressed and its state is read back.
A near name is asked about and never pressed. Anything else does nothing, and says so.
"""
import difflib, os, re, shutil, subprocess, sys, time

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

S = Atspi.StateType
SETTLE = 0.6                                # seconds to wait for a control to change after a press
WORDS = {"toggle button": "toggle", "push button": "button", "button": "button"}


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^\w ]", " ", text.lower())).strip()


def parse(text):
    t = norm(text)
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


def answer(text):
    intent, arg = parse(text)
    w = front_window()
    if w is None: return "I cannot find the window in front. Nothing was done."
    title = w.get_name() or "A window with no name"
    if intent == "unknown": return f"I heard: {arg or 'nothing'}. Nothing was done."
    if intent == "where":
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
    if how == "press": return press(found[idx[0]])
    if how == "none": return f"{title} shows nothing called {arg}. Nothing was pressed."
    if len(idx) == 1: return f"Did you mean {names[idx[0]]}? Nothing was pressed."
    kinds = ", ".join(WORDS.get(found[i].get_role_name(), found[i].get_role_name()) for i in idx)
    return f"{len(idx)} things are called {names[idx[0]]}: {kinds}. Nothing was pressed."


def hear(path):
    r = subprocess.run(["voxtype", "-q", "--model", "small.en", "transcribe", path], capture_output=True, text=True, timeout=60)
    if r.returncode: raise SystemExit(f"voxtype failed: {r.stderr.strip()[-200:]}")
    return re.sub(r"\x1b\[[0-9;]*m", "", r.stdout).strip().splitlines()[-1] if r.stdout.strip() else ""


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

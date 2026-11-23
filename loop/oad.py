#!/usr/bin/env python3
"""The loop, kept running. It follows focus by events, so an answer does not start by searching the desktop.

  oad.py                      run until stopped, listening on $XDG_RUNTIME_DIR/omarchy-accessibility.sock
  oad.py say "press bold"     send words to the running one, and print its answer and how long it took
  oad.py hear command.wav     transcribe a recording, telling the recogniser what is on screen, then act on it

Only this user can open the socket. This program never opens a microphone; oa-talk records, only while its key is held.
"""
import json, os, socket, sys, threading, time
from pathlib import Path

import oa
from gi.repository import Atspi, GLib

SOCK = Path(os.environ.get("XDG_RUNTIME_DIR", "/nowhere")) / "omarchy-accessibility.sock"
LIMIT = 2000                                # characters in one request
state = {"window": None, "focus": None}


def on_event(e):
    try:
        if e.type == "window:activate": state["window"] = e.source
        elif e.type == "window:deactivate" and e.source == state["window"]: state["window"] = None
        elif e.type == "object:state-changed:focused" and e.detail1: state["focus"] = e.source
    except GLib.Error:
        pass                                # the thing that sent the event has gone


def front():
    w = state["window"]
    try:
        if w is not None and w.get_state_set().contains(oa.S.ACTIVE): return w
    except GLib.Error:
        state["window"] = None
    state["window"] = oa.front_window()
    return state["window"]


def reply(words):
    t = time.perf_counter()
    if words == "@names":
        try: return {"names": [o.get_name() for o in (oa.controls(front()) if front() else None) or []]}
        except GLib.Error: return {"names": []}
    try:
        out = oa.answer(words, window=front(), focus=state["focus"])
    except GLib.Error as e:
        out = "The app stopped answering. I do not know whether anything was done."
        print(f"AT-SPI: {e.message}", file=sys.stderr)
    return {"heard": words, "says": out, "ms": round((time.perf_counter() - t) * 1e3, 1)}


def serve_one(conn):
    with conn:
        conn.settimeout(5)
        try:
            words = conn.recv(4 * LIMIT).decode(errors="replace").strip()[:LIMIT]
            done, box = threading.Event(), {}
            GLib.idle_add(lambda: (box.update(reply(words)), done.set()) and False)   # AT-SPI stays on the main loop
            if not done.wait(20): box = {"heard": words, "says": "I took too long and gave up.", "ms": None}
            conn.sendall(json.dumps(box).encode()); conn.shutdown(socket.SHUT_WR)
            if box.get("says"): oa.speak(box["says"])
        except OSError as e:
            print(f"client: {e}", file=sys.stderr)


def run():
    Atspi.init(); lis = Atspi.EventListener.new(on_event)
    for e in ("window:activate", "window:deactivate", "object:state-changed:focused"): lis.register(e)
    SOCK.unlink(missing_ok=True)
    s = socket.socket(socket.AF_UNIX); old = os.umask(0o177); s.bind(str(SOCK)); os.umask(old); s.listen(4)

    def accept():
        while True: threading.Thread(target=serve_one, args=(s.accept()[0],), daemon=True).start()
    threading.Thread(target=accept, daemon=True).start()
    print(f"listening on {SOCK}", flush=True)
    try: GLib.MainLoop().run()
    except KeyboardInterrupt: pass
    finally: SOCK.unlink(missing_ok=True)


def say(words):
    with socket.socket(socket.AF_UNIX) as s:
        s.settimeout(30); s.connect(str(SOCK)); s.sendall(words.encode()); s.shutdown(socket.SHUT_WR)
        return json.loads(b"".join(iter(lambda: s.recv(65536), b"")))


if __name__ == "__main__":
    if sys.argv[1:2] == ["say"] and len(sys.argv) == 3:
        try: r = say(sys.argv[2])
        except OSError: sys.exit("The service is not running.")
        print(f"heard: {r['heard']}\nsays:  {r['says']}\ntook:  {r['ms']} ms")
    elif sys.argv[1:2] == ["hear"] and len(sys.argv) == 3:
        t = time.perf_counter()
        try: names = say("@names")["names"]
        except OSError: sys.exit("The service is not running.")
        words = oa.hear(sys.argv[2], names); t1 = time.perf_counter(); r = say(words)
        print(f"heard: {words}\nsays:  {r['says']}\ntook:  {(t1 - t) * 1e3:.0f} ms to hear, {r['ms']} ms to answer")
    elif len(sys.argv) == 1: run()
    else: sys.exit(__doc__)

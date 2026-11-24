"""What was handed to the voice, from a speech-dispatcher log at level 5 on standard input.

One line each: time, then finished | cut off | unknown, then the words. Unknown means the log ends without saying.
"""
import html, re, sys

LINE = re.compile(r"^\[\w+ \w+ +\d+ (\d\d:\d\d:\d\d) \d+ : (\d+)\] *speechd: +", re.M)
SENT = re.compile(r"Command sent to output module: \|(.*?)\| \(-?\d+\)\s*$", re.S)
ENDED = re.compile(r"Event from output module while speaking: \|(702|703|704)")
VERBS = {"SPEAK", "CHAR", "KEY", "SOUND_ICON"}


def spoken(log):
    starts, out, verb = list(LINE.finditer(log)), [], False
    for m, nxt in zip(starts, starts[1:] + [None]):
        body = log[m.end():nxt.start() if nxt else len(log)]
        s, e = SENT.match(body), ENDED.match(body)
        if s:
            words = s[1].strip()
            if words in VERBS: verb = True
            elif verb:
                verb = False
                text = " ".join(html.unescape(re.sub(r"<[^>]+>", "", words)).split())
                out.append([f"{m[1]}.{int(m[2]) // 1000:03d}", None, text])
        elif e and out and out[-1][1] is None and e[1] != "704":
            out[-1][1] = "finished" if e[1] == "702" else "cut off"
    return out


if __name__ == "__main__":
    for when, how, text in spoken(sys.stdin.read()): print(when, how or "unknown", "|", text)

#!/usr/bin/env python3
"""Check the chain: decision -> finding -> source -> the source's own words.

Exit 1 on a broken link, a missing field, or a quote that is not in the stored copy.
A source with no stored copy is reported as UNCHECKED, which is not a pass.
Stored copies live in snapshots/ and are not published: they belong to their authors.
"""
import hashlib, re, sys
from pathlib import Path

NEED = {
    "sources": ("title", "authors", "year", "url", "kind", "read", "retrieved", "sha256"),
    "findings": ("claim", "sources", "strength", "would_change"),
    "decisions": ("title", "status", "decided_by", "date", "findings", "would_change"),
}
READ = {"full", "passages", "abstract", "secondary"}
STATUS = {"approved", "proposed", "superseded"}


def flat(s):
    s = s.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "ﬁ": "fi"}))
    # A PDF breaks words over lines and HTML puts spaces before punctuation; neither changes the words.
    s = re.sub(r"(?<=\w)-\s+", "", re.sub(r"\s+", " ", s))
    return re.sub(r"\s+(?=[%,.;:])", "", s).strip().lower()


def load(path):
    m = re.match(r"---\n(.*?)\n---\n(.*)", path.read_text(), re.S)
    if not m:
        return None, ""
    meta = dict(l.split(": ", 1) for l in m[1].splitlines() if ": " in l)
    return meta, m[2]


def ids(value):
    return [x.strip() for x in value.split(",") if x.strip()]


def check(root):
    errors, notes, pages = [], [], {}
    for kind, need in NEED.items():
        pages[kind] = {}
        for p in sorted((root / "wiki" / kind).glob("*.md")):
            meta, body = load(p)
            if meta is None:
                errors.append(f"{kind}/{p.stem}: no front matter")
                continue
            errors += [f"{kind}/{p.stem}: missing {k}" for k in need if not meta.get(k)]
            pages[kind][p.stem] = (meta, body)
    for name, (meta, body) in pages["sources"].items():
        if meta.get("read") not in READ:
            errors.append(f"sources/{name}: read must be one of {sorted(READ)}")
        quotes = re.findall(r"^> (.+)$", body, re.M)
        if not quotes:
            errors.append(f"sources/{name}: no quotation")
        snap = root / "snapshots" / f"{name}.txt"
        if not snap.exists():
            notes.append(f"UNCHECKED sources/{name}: no stored copy on this machine")
            continue
        raw = snap.read_bytes()
        if hashlib.sha256(raw).hexdigest() != meta.get("sha256"):
            errors.append(f"sources/{name}: stored copy does not match its sha256")
        text = flat(raw.decode(errors="ignore"))
        errors += [f"sources/{name}: not in the stored copy: {q[:70]}" for q in quotes if flat(q) not in text]
    used = set()
    for name, (meta, _) in pages["findings"].items():
        for s in ids(meta.get("sources", "")):
            used.add(s)
            if s not in pages["sources"] and not (s.startswith("measure:") and (root / s[8:]).exists()):
                errors.append(f"findings/{name}: no such source {s}")
    for name, (meta, _) in pages["decisions"].items():
        if meta.get("status") not in STATUS:
            errors.append(f"decisions/{name}: status must be one of {sorted(STATUS)}")
        for f in ids(meta.get("findings", "")):
            used.add(f)
            # "none" marks an owner's choice, so a decision never borrows evidence it does not rest on.
            if f not in pages["findings"] and f != "none":
                errors.append(f"decisions/{name}: no such finding {f}")
        by = meta.get("superseded_by")
        if (meta.get("status") == "superseded") != bool(by) or (by and by not in pages["decisions"]):
            errors.append(f"decisions/{name}: superseded and superseded_by must agree")
    for kind in ("sources", "findings"):
        notes += [f"UNUSED {kind}/{n}" for n in pages[kind] if n not in used]
    return errors, notes, {k: len(v) for k, v in pages.items()}


if __name__ == "__main__":
    errors, notes, counts = check(Path(__file__).resolve().parents[1])
    print("\n".join(notes + ["ERROR " + e for e in errors]))
    print(counts, f"{len(errors)} errors, {len(notes)} notes")
    sys.exit(bool(errors))

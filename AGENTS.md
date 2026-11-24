# Omarchy Accessibility

A blind person should be able to install, unlock and use Omarchy by listening and talking. Open source. Research stage: `loop/oa.py` is a first trial, not a product.

- **Fixes to Omarchy's own shell go upstream**, to `omacom/omarchy`, where several developers, and a blind user offering to test, are already active. Check their open pull requests before writing anything. This repository holds what does not fit there.
- **Local by default.** A blind person's screen text and microphone do not leave the machine unless they turn that on.
- **Everything reachable by voice; nothing reachable only by voice.** Keyboard and braille stay whole.
- **Never claim something works for blind people until a blind person has used it.**
- **Tests that need an accessibility bus run on a private display, a private D-Bus and a private `XDG_RUNTIME_DIR`.** `experiments/2026-11-23/run-trees.sh` shows how, and why.
- **Decisions are argued from `wiki/`.** A decision cites findings, a finding cites sources, a source quotes itself. Run `python3 tools/check_wiki.py` and `python3 -m unittest discover -s tests` before a commit. Replace a decision by superseding it; never edit away why it was made.
- **This repository is public.** Working briefs (`reports/`) and stored copies of other people's papers (`snapshots/`) stay on this machine, and nothing about approaching a named person goes in.
- Measurements: `docs/research/`. New sources: `tools/snapshot.sh`. The recogniser experiments: `experiments/2026-11-23/setup.sh`.
- Picking this up on the owner's machine: read the newest file in `reports/handoffs/` first (local only).

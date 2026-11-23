# Omarchy Accessibility

The aim: a blind person can install, unlock and use [Omarchy](https://omarchy.org) by listening and talking, with speech models that run on their own computer.

This is at the research stage, and there is nothing to install yet. [A first loop](loop/oa.py) reads the window in front, presses a control by name, says what it checked, tells you where a control is, and learns your own phrases. [A service](loop/oad.py) keeps it running, and [an Omarchy plugin](plugin/) starts it. None of it has run on a live desktop or with a live microphone. What we believe and why is in [the evidence](wiki/README.md): each decision leads to findings, and each finding to the words of its sources. The measurements so far are in [docs/research](docs/research/2026-11-23-measurements.md).

No blind person has used or reviewed this yet. If you are blind and something here is wrong, an issue saying so is the most useful thing you could send.

## Other Omarchy work

- [omarchy-voice](https://github.com/wombatoperator/omarchy-voice): voice control through OpenAI, MIT.
- [omarchy-accessibility-kit](https://github.com/lorenzo-leuck/omarchy-accessibility-kit): on-screen keyboard and push-to-talk commands, MIT.
- [omarchy-magnifier](https://github.com/JPDoesDev/omarchy-magnifier): zoom for low vision, MIT.
- [hyprhand](https://github.com/JosXa/hyprhand): desktop control for agents through the accessibility tree, MIT.
- Omarchy's own [panel](https://github.com/omacom/omarchy/pull/13212), [bar](https://github.com/omacom/omarchy/pull/16608) and [menu](https://github.com/omacom/omarchy/pull/17648) labels, open as of 23 November 2026.

MIT licence.

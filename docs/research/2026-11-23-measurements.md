# What was measured on 2026-11-23

One laptop: Ryzen 9 5900HX, RTX 3080 Laptop 16 GB, Omarchy 4.5.0-3, Hyprland 0.56.2, Quickshell 0.3.2.r7, at-spi2-core 2.62.1. Load average about 5.5 from other work, so treat every time as "on a busy laptop". Scripts are in `experiments/2026-11-23/`.

## Labels in the installed shell

`grep -rnE "Accessible\." /usr/share/omarchy/shell` gives 0 lines. The omarchy package ships 138 `.qml` files, and none contains `Accessible.`.

## Reading an app's accessibility tree (Xvfb, private bus; software rendering)

| App | Nodes | Walk one node at a time, 3 runs | `Cache.GetItems` | `Collection.GetMatches`, showing only | The same, plus role and name of each |
|---|---|---|---|---|---|
| LibreOffice Writer | 2,101 | 1,700 / 2,501 / 2,566 ms | 478 ms | 197 matches, 4.6–6.1 ms | 118–127 ms |
| Nautilus | 167 | 229 / 332 / 340 ms | 66 ms (408 items) | no Collection interface | not available |
| Chromium, a Wikipedia article | 247 in the walk | 216 / 455 / 445 ms | 37 ms | 479 matches in a separate run, 6.6–8.0 ms | 377–392 ms |

One D-Bus round trip: 0.34–0.42 ms. The walk and the Collection query were separate launches. The walked Chromium tree was probably a browser-extension tab rather than the article: a rerun gave the same 247 nodes under the extension's window title. The 479-match window was titled with the article. So compare LibreOffice, not Chromium, across columns. A rerun of the packaged script gave Writer 1,896 / 2,921 / 2,934 ms walked (2,215 nodes), 4.5–6.5 ms by query and 123–129 ms with names. The Collection query also skips hidden controls, which the walk does not.

## Pressing a control

LibreOffice's Bold toggle through AT-SPI `do_action`, until the toggle's state changed: 3.7–9.3 ms over 10 presses, median 4.2 ms.

## Speech out

| Engine | "Save" | "Save button, focused" | 17 words |
|---|---|---|---|
| eSpeak NG, 450 wpm, new process each time, first bytes | 9.0 ms | 9.1 ms | 9.3 ms |
| Piper lessac-medium on the processor, loaded, first chunk | 69 ms | 138 ms | 236 ms |

Time to sound leaving a speaker was not measured.

## Speech in

Voxtype on the GPU, warm, one 12-word sentence spoken by eSpeak: base.en 0.14 s, small.en 0.21 s, large-v3-turbo 0.35 s. base.en heard "three" as "free"; the other two were right. One synthetic sentence says nothing about accuracy on people.

## Choosing the action with a local model

qwen3.5:9b through Ollama, thinking off, 7 tools: median 895 ms, 718–1,291 ms, 12 of 12 on sentences written by the agent that wrote the tools. That is a smoke test, not an accuracy figure. Cold load: 10.9 s.

## Not measured

Waiting for the person to stop talking; barge-in and echo; whether any of it works for a blind person; Hyprland with Orca; the terminal; the greeter, the installer and disk unlock; a Quickshell window on this box's own bus (the live accessibility flag is off and was left off). Hosted models were not called.

## Other projects and Omarchy's queue, read from GitHub on 2026-11-23

Omarchy: MIT, 4,160 pull requests open and 2,493 merged. omarchy-voice: MIT, 225 stars, about 337 kB, last pushed 2026-09-25. omarchy-accessibility-kit: MIT at the top, with an AGPL-3.0 part (mudra, hand gestures) inside, 0 stars, last pushed 2026-11-11. omarchy-magnifier: MIT, 2 stars, last pushed 2026-11-21. hyprhand: MIT, 0 stars, last pushed 2026-11-20. ATSPI-MCP-Server: AGPL-3.0, 3 stars, last pushed 2025-09-05. niri and COSMIC's compositor: GPL-3.0. otto, another compositor with the keyboard service: MIT.

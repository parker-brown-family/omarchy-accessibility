# Fifty requests through small local models

Thirty clear requests, ten that must be asked about, ten remarks that need nothing. Ollama, thinking off, warm, while other work shared the GPU. The requests, tools and scoring were written by one agent, so this ranks models and says nothing about real people. "Click send" was scored as clear, though the instructions also say to ask before sending.

| Model | Clear, right of 30 | Held back, of 20 | Acted when it should not | p50 | p95 |
|---|---|---|---|---|---|
| qwen3.5:0.8b | 22 | 16 | 4 | 244 ms | 346 ms |
| qwen3.5:2b | 25 | 19 | 1 | 369 ms | 486 ms |
| qwen3.5:4b | 26 | 19 | 1 | 663 ms | 826 ms |
| qwen3.5:9b | 29 | 19 | 1 | 952 ms | 1,315 ms |

The 0.8b model meets a 250 ms target and acts on four things it should have left alone. Every model pressed something for "press the third one".

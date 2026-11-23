# Does the screen teach the ear?

A recogniser usually guesses from all of English. The accessibility tree already says which 67 names are on screen in LibreOffice Writer. This gives those names to the recogniser and counts what it presses.

Five synthetic voices said "press" and each name, clean and in white noise at 5 dB: 335 clips each. The control is chosen in code. Only an exact name is pressed; a near one is asked about.

| Streaming model on the processor | Clean: right / wrong presses | Noise: right / wrong presses | Absent names pressed, of 20 |
|---|---|---|---|
| No hints | 174 / 0 | 53 / 0 | 1 |
| Screen names, weight 1.5 | 266 / 1 | 138 / 1 | 2 |
| Screen names, weight 2.5 | 275 / 1 | 165 / 5 | 3 |

It finished 67 to 76 ms after the speech ended, on a busy machine, in compute time alone.

A stronger recogniser, Whisper small.en with no hints, on two of the voices (134 clips each):

| | Clean, right presses | Noise, right presses | Wrong presses |
|---|---|---|---|
| Streaming, no hints | 61 | 9 | 0 |
| Streaming, screen names | 111 | 42 | 0 |
| Whisper small.en, no hints | 122 | 74 | 0 |

**What it shows.** The names help a small recogniser a great deal, and a better recogniser still beats it. Heavier hints press the wrong thing more. Whisper with hints was not tried.

**What it does not show.** Every voice is synthetic, the noise is white, the words are one app's, and nobody blind took part. A first run without silence around the clips was thrown out as unfair: it cut words off. Scripts and raw output: `experiments/2026-11-23/screen_teaches_ear*`, `whisper_same_audio*`. Model: sherpa-onnx-streaming-zipformer-en-2023-06-26.

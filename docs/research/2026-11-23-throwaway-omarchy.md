# A throwaway Omarchy that can be heard

`tools/vm.sh run OUT SCRIPT` boots Omarchy 4.5.0 from its published image, installs Orca and a speech service, runs a script in the desktop session, and brings back the script's output, every text handed to the voice, and the sound that left the machine. Measured on an idle twelve-thread laptop with KVM.

| Checked | Result |
|---|---|
| Image and boot files | hashes match the published ones |
| Boot to a login over SSH | 5.1 s, the same in every boot; not a benchmark |
| Whole run, with Orca installed and 25 s of script | 40 s |
| Desktop | Hyprland and Omarchy's shell running, seen in a photograph |
| Words | "Welcome to Omarchy. No applications open." and Orca's "Screen reader on." both recorded as finished; a message stopped halfway recorded as cut off |
| Sound | a recogniser given the recording wrote "welcome to Amaki, no applications open. screen reader on foam foam content view text" |
| Nothing left behind | after a finished run, a failing script, a timeout, and the caller being terminated or killed: no machine running, no folder left, image hash unchanged. A marker file from one machine was absent in the next. |
| Exit status | the script's own (7 came back as 7); a timeout gives 125 and no results |

Small Whisper wrote "Amaki" for "Omarchy" and "foam" for "Home", from the default eSpeak voice, so this is one voice and a few words. It is a warning about "Omarchy" as a wake word, and no more.

## A first hearing of Omarchy, not yet a result

With Orca running on plain Omarchy, opening Nautilus gave "Home", "Home", "Content View". Opening Omarchy's menu, which shows ten entries, gave one word: "text". Orca's log shows that word came from the shell taking focus. Two runs gave the same words. Orca was started after the shell was already running, and nothing was pressed in the menu, so this says what one opening sounds like and not what the menu can do.

## Limits

- The packages come from Omarchy's stable mirror on the day of the run, onto a week-old image. Orca was 51.1, AT-SPI 2.62.1.
- The machine has no graphics card, so nothing here times a recogniser, and no microphone yet. QEMU's sound card only plays.
- The virtio display was missing from the host's QEMU; `setup` takes Arch's signed module when it is.
- Nobody blind has heard any of it.

`experiments/2026-11-23/vm-speaks.sh` is the script that was run.

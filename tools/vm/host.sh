#!/bin/bash
# Runs on the host, in a job folder it deletes. Its standard output is a tar of the results; everything else goes to standard error.
set -uo pipefail
job=$1; caller=$PPID
clean() { for f in "$job"/state/*/qemu.pid; do [[ -e $f ]] && kill "$(<"$f")" 2>/dev/null; done; rm -rf "$job"; }
trap clean EXIT; trap 'exit 129' HUP INT TERM
home=${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-accessibility-vm
[[ -e $home/disk ]] || { echo "vm: run 'tools/vm.sh setup' first" >&2; exit 125; }
mkdir "$job/out" "$job/state"
export QEMU_MODULE_DIR=$home/modules VM_STATE_DIR=$job/state SMP=${SMP:-6} MEM=${MEM:-6G}
export QEMU_EXTRA="-audiodev wav,id=a0,path=$job/raw.wav -device ich9-intel-hda -device hda-output,audiodev=a0"
tar cf "$job/in.tar" -C "$job" guest.sh spoken.py in
timeout -k 20 "$OA_VM_TIME" "$home/vm-boot" "$(readlink -f "$home/disk")" 'mkdir -p ~/job && tar xf - -C ~/job && exec bash ~/job/guest.sh' <"$job/in.tar" >"$job/guest.tar" & run=$!
# If whoever asked goes away, the machine goes too. A dead caller is seen as a changed parent.
while kill -0 $run 2>/dev/null; do
  [[ $(cut -d' ' -f4 /proc/$$/stat) == "$caller" ]] || { kill $run; wait $run; exit 129; }
  sleep 1
done
wait $run; status=$?
if [[ -s $job/guest.tar ]]; then tar xf "$job/guest.tar" -C "$job/out" || status=125; else echo "vm: the machine gave no results (status $status)" >&2; status=125; fi
# QEMU leaves the WAV header unfinished, so the length is taken from the data.
(( $(stat -c %s "$job/raw.wav" 2>/dev/null || echo 0) > 44 )) && ffmpeg -v error -ignore_length 1 -i "$job/raw.wav" "$job/out/speech.wav" </dev/null >&2
tar cf - -C "$job/out" .; exit $status

#!/bin/bash
# Boot a fresh, throwaway Omarchy, run a script in its desktop session, bring back what it said, and leave nothing behind.
#
#   tools/vm.sh setup                        download and verify the image (4.2 GB, once)
#   tools/vm.sh run OUT SCRIPT [FILE...]     FILEs and SCRIPT land in ~/in of a machine that has never been used
#
# OUT gets: log.txt     what SCRIPT printed
#           spoken.txt  every text handed to the voice, with its time and whether it finished
#           speech.wav  the sound that left the machine's sound card (missing when it made none)
#           anything SCRIPT wrote in ~/out
# The exit status is SCRIPT's. 125 means the machine, not SCRIPT, failed.
#
# OA_VM_HOST  ssh host to run it on; unset means this computer. It needs /dev/kvm, qemu, ffmpeg, and 6 GB of memory.
# OA_VM_TIME  seconds before a run is stopped (600)
set -euo pipefail
here=$(cd "$(dirname "$0")/vm" && pwd)
on() { if [[ -n ${OA_VM_HOST:-} ]]; then exec ssh -o BatchMode=yes -o ServerAliveInterval=15 "$OA_VM_HOST" "$1"; else exec bash -c "$1"; fi; }
case ${1:-} in
  setup) on 'bash -s' <"$here/setup.sh" ;;
  run)
    out=${2:?where results go}; script=${3:?a script to run}; shift 3
    work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
    mkdir -p "$out" "$work/job/in"; cp "$here"/{host.sh,guest.sh,spoken.py} "$work/job"; cp "$script" "$work/job/in/.script"
    (( $# )) && cp -r "$@" "$work/job/in"
    status=0
    tar cf - -C "$work/job" . | on "j=\$(mktemp -d /var/tmp/oa-vm.XXXXXX) && tar xf - -C \$j && OA_VM_TIME=${OA_VM_TIME:-600} exec bash \$j/host.sh \$j" >"$work/out.tar" & p=$!
    trap 'kill $p; exit 130' INT TERM; wait $p || status=$?
    tar xf "$work/out.tar" -C "$out" 2>/dev/null || { echo "vm: no results came back" >&2; exit 125; }
    exit "$status" ;;
  *) sed -n '2,15p' "$0" >&2; exit 2 ;;
esac

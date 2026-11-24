#!/bin/bash
# Runs inside the throwaway machine as its desktop user. Standard output is a tar of ~/out; progress goes to standard error.
set -uo pipefail
mkdir -p ~/out ~/.config/speech-dispatcher /tmp/spdlog; mv ~/job/in ~/in; cd ~/in || exit 125
die() { echo "vm: $1" >&2; exit 125; }
for _ in $(seq 120); do shell=$(pgrep -xo quickshell) && break; sleep 0.5; done; [[ -n $shell ]] || die "the desktop did not start"
while IFS= read -r -d '' e; do [[ $e == @(WAYLAND_DISPLAY|DISPLAY|HYPRLAND_INSTANCE_SIGNATURE|XDG_*|DBUS_SESSION_BUS_ADDRESS|PATH|OMARCHY_*)=* ]] && export "$e"; done <"/proc/$shell/environ"
echo omarchy | sudo -S -v 2>/dev/null || die "no sudo"
sudo pacman -Sy --noconfirm --needed orca speech-dispatcher espeak-ng ${OA_VM_PACKAGES:-} >~/out/packages.txt 2>&1 || die "packages did not install: $(tail -1 ~/out/packages.txt)"
sed -e 's/^#\? *LogLevel.*/LogLevel 5/' -e 's|^#\? *LogDir.*|LogDir "/tmp/spdlog"|' /etc/speech-dispatcher/speechd.conf >~/.config/speech-dispatcher/speechd.conf
wpctl set-volume @DEFAULT_AUDIO_SINK@ 0.8 2>/dev/null
# Straight to a file: programs SCRIPT leaves open would hold a pipe, and the connection, open after it.
touch ~/out/log.txt; bash .script >~/out/log.txt 2>&1 & s=$!
tail -f -n +1 --pid=$s ~/out/log.txt >&2 & t=$!
wait $s; status=$?; wait $t
sleep 1
cat /tmp/spdlog/speech-dispatcher.log 2>/dev/null | python3 ~/job/spoken.py >~/out/spoken.txt
tar cf - -C ~/out .; exit $status

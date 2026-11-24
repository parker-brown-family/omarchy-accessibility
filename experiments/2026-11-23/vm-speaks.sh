#!/bin/bash
# Run by tools/vm.sh in a throwaway Omarchy: one spoken sentence, then Orca on plain Omarchy with Nautilus and Omarchy's menu opened.
spd-say -w "Welcome to Omarchy. No applications open."
echo "shell: $(pgrep -xc quickshell)  hyprland: $HYPRLAND_INSTANCE_SIGNATURE"
/usr/bin/ls -a ~/in
gsettings set org.gnome.desktop.a11y.applications screen-reader-enabled true
orca --replace --debug-file="$HOME/out/orca-debug.txt" >~/out/orca.out 2>&1 & sleep 8
pgrep -xc orca
say() { echo "$(date +%T.%3N) $1"; }
say "opening Nautilus"; nautilus >/dev/null 2>&1 & sleep 6
say "opening the menu"; omarchy-menu >/dev/null 2>&1 & sleep 5
grim ~/out/screen.png && say "photographed"
hyprctl clients -j | python3 -c 'import json,sys; print([c["class"] for c in json.load(sys.stdin)])'

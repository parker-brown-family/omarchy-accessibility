#!/usr/bin/env bash
# The running service against a real LibreOffice Writer, on a private display, bus and runtime directory.
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd); work=$(mktemp -d); run=$(mktemp -d); chmod 700 "$run"
data=$HOME/.local/share
cat > "$work/inner.sh" <<I
export OA_QUIET=1 OA_PHRASES=$work/phrases.json GDK_BACKEND=x11 HOME=$work XDG_CONFIG_HOME=$work/.config; mkdir -p $work/.config
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null
/usr/lib/at-spi2-registryd >/dev/null 2>&1 & sleep 1
python3 $root/loop/oad.py & d=\$!; sleep 2
libreoffice --norestore --writer -env:UserInstallation=file://$work/lo >/dev/null 2>&1 & sleep 20
python3 $root/loop/oad.py say "where am i"; python3 $root/loop/oad.py say "what can i do here"; xdotool key Escape; sleep 2
for c in "where am i" "where am i" "where is bold" "where is redo" "press bold" "press bold" "press send" "press redo" "when i say shout press bold" "shout" "shout" "what have i taught you" "forget shout" "shout" "when i say where press bold" "what can i do here"; do python3 $root/loop/oad.py say "\$c"; done
for f in ${WAVS:-}; do XDG_DATA_HOME=$data python3 $root/loop/oad.py hear \$f; done
for i in \$(seq 20); do python3 $root/loop/oad.py say "press bold" | grep took; done | sed 's/took/repeat/'
ls -l $run/omarchy-accessibility.sock | cut -c1-10; kill \$d; pkill -f "[U]serInstallation=file://$work/lo" || true
I
env -u WAYLAND_DISPLAY -u HYPRLAND_INSTANCE_SIGNATURE XDG_RUNTIME_DIR="$run" PULSE_SERVER=none GTK_USE_PORTAL=0 GIO_USE_VFS=local \
  timeout 120 xvfb-run -a -s "-screen 0 1600x1000x24" dbus-run-session -- bash "$work/inner.sh"

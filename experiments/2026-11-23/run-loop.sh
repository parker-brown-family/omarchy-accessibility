#!/usr/bin/env bash
# Drive loop/oa.py against a real LibreOffice Writer on a private display, bus and runtime directory.
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd); work=$(mktemp -d); run=$(mktemp -d); chmod 700 "$run"
cat > "$work/inner.sh" <<I
real=\$HOME; export OA_QUIET=1 GDK_BACKEND=x11 HOME=$work XDG_CONFIG_HOME=$work/.config; mkdir -p $work/.config
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null
/usr/lib/at-spi2-registryd >/dev/null 2>&1 & sleep 1
libreoffice --norestore --writer -env:UserInstallation=file://$work/lo >/dev/null 2>&1 &
sleep 20
xdotool search --name "LibreOffice Writer" windowfocus 2>/dev/null || true; sleep 2
for c in "where am I" "what can I do here" "press bold" "press bold" "press send" "press bald" "press redo" "press paste" "what is the weather"; do python3 $root/loop/oa.py text "\$c"; done
pkill -f "[U]serInstallation=file://$work/lo" || true
I
env -u WAYLAND_DISPLAY -u HYPRLAND_INSTANCE_SIGNATURE XDG_RUNTIME_DIR="$run" PULSE_SERVER=none GTK_USE_PORTAL=0 GIO_USE_VFS=local \
  timeout 120 xvfb-run -a -s "-screen 0 1600x1000x24" dbus-run-session -- bash "$work/inner.sh"

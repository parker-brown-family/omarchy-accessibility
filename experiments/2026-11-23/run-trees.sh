#!/usr/bin/env bash
# Open three real apps on a private display, private D-Bus and PRIVATE XDG_RUNTIME_DIR, then time their accessibility trees.
# The private runtime dir is load-bearing: the first run shared /run/user/1000, its document portal
# tried to mount over the live one, and the live xdg-document-portal exited for 33 seconds.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd); work=$(mktemp -d); run=$(mktemp -d); chmod 700 "$run"
cat > "$work/inner.sh" <<I
export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1 GDK_BACKEND=x11 QT_QPA_PLATFORM=xcb HOME=$work XDG_CONFIG_HOME=$work/.config
mkdir -p $work/.config
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null
/usr/lib/at-spi2-registryd >/dev/null 2>&1 & sleep 1
nautilus /usr/share >/dev/null 2>&1 &
chromium --ozone-platform=x11 --disable-gpu --no-first-run --user-data-dir=$work/cr --password-store=basic --force-renderer-accessibility https://en.wikipedia.org/wiki/Screen_reader >/dev/null 2>&1 &
libreoffice --norestore --writer -env:UserInstallation=file://$work/lo >/dev/null 2>&1 &
sleep 28
trap "kill \$(jobs -p) 2>/dev/null" EXIT
for s in walk fast coll; do echo "== \$s"; python3 $here/\$s.py; done
pkill -f "[u]ser-data-dir=$work/cr" || true; pkill -f "[U]serInstallation=file://$work/lo" || true
I
env -u WAYLAND_DISPLAY -u HYPRLAND_INSTANCE_SIGNATURE XDG_RUNTIME_DIR="$run" GTK_USE_PORTAL=0 GIO_USE_VFS=local \
  timeout 120 xvfb-run -a -s "-screen 0 1600x1000x24" dbus-run-session -- bash "$work/inner.sh"

#!/bin/bash
# Runs on the computer that will host the machine. Downloads Omarchy's published image and refuses one whose hash is wrong.
set -euo pipefail
v=${OA_VM_VERSION:-4.5.0/494}; sum=${OA_VM_SUM:-fea962bb66bef8f922900018f8241e50a2d1a00268715541882479016235dc9f}
home=${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-accessibility-vm; url=https://nightly.omarchy.org/stable/$v; disk=omarchy-${v%/*}.qcow2
mkdir -p "$home/modules"; cd "$home"
[[ -r /dev/kvm && -w /dev/kvm ]] || { echo "/dev/kvm is not usable here" >&2; exit 1; }
for f in vmlinuz initrd cmdline vm-boot SHA256SUMS; do curl -sSfL -o "$f" "$url/unpacked/$f"; done
sha256sum -c --quiet SHA256SUMS; chmod +x vm-boot
[[ -e $disk ]] || { curl -fL -C - -o "$disk.part" "$url/$disk"; mv "$disk.part" "$disk"; }
echo "$sum  $disk" | sha256sum -c - || { echo "the image is not the one published; deleted" >&2; rm -f "$disk"; exit 1; }
chmod a-w "$disk"; ln -sfn "$disk" disk
# Arch packages QEMU's virtio display apart. If it is missing, use the packager's signed files from a folder, without installing.
export QEMU_MODULE_DIR=$home/modules
if ! qemu-system-x86_64 -device help 2>/dev/null | grep -q '"virtio-vga"'; then
  ver=$(pacman -Q qemu-common | cut -d' ' -f2); t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
  for p in virtio-gpu virtio-vga; do
    n=qemu-hw-display-$p; f=$n-$ver-x86_64.pkg.tar.zst
    curl -sSfL -o "$t/$f" "https://archive.archlinux.org/packages/q/$n/$f"; curl -sSfL -o "$t/$f.sig" "https://archive.archlinux.org/packages/q/$n/$f.sig"
    gpg --homedir /etc/pacman.d/gnupg --no-permission-warning --lock-never --status-fd 1 --verify "$t/$f.sig" "$t/$f" 2>/dev/null | grep -qE '^\[GNUPG:\] TRUST_(FULLY|ULTIMATE)' || { echo "$f is not signed by a trusted packager" >&2; exit 1; }
    tar xf "$t/$f" -C "$t" --wildcards 'usr/lib/qemu/*'; cp "$t"/usr/lib/qemu/*.so modules/
  done
  qemu-system-x86_64 -device help 2>/dev/null | grep -q '"virtio-vga"' || { echo "QEMU still has no virtio-vga" >&2; exit 1; }
fi
echo "ready: $home"

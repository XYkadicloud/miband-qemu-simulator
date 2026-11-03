#!/usr/bin/env bash
set -euo pipefail
MODEL=${1:?Usage: bash tools/build-qemu.sh band9|band11|band10pro}
case "$MODEL" in band11|band10pro|band9) ;; *) exit 2 ;; esac
PROJECT_ROOT=$(cd "${BASH_SOURCE[0]%/*}/.." && pwd)
COMPILE_ROOT=${QEMU_BUILD_ROOT:-$PROJECT_ROOT/.build/$MODEL}
# MinGW tools can emit the Windows ACP even under a UTF-8 Python locale.
# Meson's legacy decoder tolerates these compiler diagnostics.
export PYTHONUTF8=0 PYTHONIOENCODING=utf-8 LC_ALL=C LANG=C
for dep in gcc g++ python ninja pkg-config; do
  command -v "$dep" >/dev/null || { printf 'Missing build dependency: %s\n' "$dep" >&2; exit 1; }
done
mkdir -p "$COMPILE_ROOT/build" "$COMPILE_ROOT/tmp"
export TMPDIR="$COMPILE_ROOT/tmp"
if [[ ! -d "$COMPILE_ROOT/qemu" ]]; then
  # band9 shares the band10pro overlay (same SoC family)
  PREP_MODEL="band10pro"
  [[ "$MODEL" == "band11" ]] && PREP_MODEL="band11"
  python "$PROJECT_ROOT/tools/prepare_source.py" --model "$PREP_MODEL" --output "$COMPILE_ROOT/qemu"
fi
cd "$COMPILE_ROOT/build"
if [[ ! -f build.ninja ]]; then
  "$COMPILE_ROOT/qemu/configure" --cc=gcc --cxx=g++ --target-list=arm-softmmu \
      --without-default-devices --disable-docs --disable-tools --disable-user \
      --disable-guest-agent --disable-slirp --enable-sdl --disable-gtk --disable-curses \
      --disable-opengl --disable-virglrenderer --disable-spice --disable-gnutls \
      --disable-capstone --disable-libnfs --disable-libiscsi --disable-rbd \
      --disable-xen --disable-kvm --disable-werror --disable-rust
fi
if [[ "${CONFIGURE_ONLY:-0}" == 1 ]]; then
  printf 'Configured %s\n' "$COMPILE_ROOT/build"
  exit 0
fi
ninja -j"${BUILD_JOBS:-4}" qemu-system-arm.exe
printf 'Built %s\n' "$COMPILE_ROOT/build/qemu-system-arm.exe"

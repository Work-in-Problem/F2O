#!/usr/bin/env bash
#
# tile.sh — one-shot crop+upscale for image extraction (extracting-from-images rule 2 a–b).
#
# Usage: tile.sh <image> <x> <y> <w> <h> [scale]
#
#   Crops the WxH region whose top-left corner is at (x,y) from <image>, upscales it by
#   [scale] (default 4), writes the tile OUTSIDE the working tree, and prints the tile's
#   absolute path as the last stdout line. Read that path next and CONFIRM the tile shows
#   the intended region before trusting anything extracted from it (rule 2) — this script
#   replaces the crop+upscale commands, never the confirming Read.
#
#   Output dir: $TILE_DIR if set, else a fresh mktemp -d. Never the user's repo.
#   Backend: first available of sips (macOS) -> ImageMagick (magick/convert) -> Python
#   PIL. Force one with TILE_BACKEND=sips|magick|pil.
#
# Exit status: 0 on success, 2 on usage error, 3 if no backend is available.

set -u

usage() { echo "usage: tile.sh <image> <x> <y> <w> <h> [scale]" >&2; exit 2; }

[ $# -ge 5 ] && [ $# -le 6 ] || usage
IMG="$1"; X="$2"; Y="$3"; W="$4"; H="$5"; SCALE="${6:-4}"

[ -f "$IMG" ] || { echo "tile.sh: no such file: $IMG" >&2; exit 2; }
for v in "$X" "$Y" "$W" "$H" "$SCALE"; do
  case "$v" in ''|*[!0-9]*) echo "tile.sh: x/y/w/h/scale must be non-negative integers (got '$v')" >&2; exit 2 ;; esac
done
[ "$W" -gt 0 ] && [ "$H" -gt 0 ] && [ "$SCALE" -gt 0 ] || { echo "tile.sh: w, h, scale must be > 0" >&2; exit 2; }

OUTDIR="${TILE_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/tiles.XXXXXX")}"
mkdir -p "$OUTDIR" || { echo "tile.sh: cannot create output dir: $OUTDIR" >&2; exit 2; }

base="$(basename "$IMG")"; base="${base%.*}"
TILE="$OUTDIR/${base}_x${X}_y${Y}_w${W}_h${H}_s${SCALE}.png"
ZW=$((W * SCALE)); ZH=$((H * SCALE))

pick_backend() {
  if [ -n "${TILE_BACKEND:-}" ]; then echo "$TILE_BACKEND"; return; fi
  if command -v sips >/dev/null 2>&1; then echo sips
  elif command -v magick >/dev/null 2>&1 || command -v convert >/dev/null 2>&1; then echo magick
  elif python3 -c 'import PIL' >/dev/null 2>&1; then echo pil
  else echo none; fi
}

BACKEND="$(pick_backend)"
case "$BACKEND" in
  sips)
    # sips argument order: --cropOffset takes Y then X; -c takes H then W; -z takes H then W.
    cp "$IMG" "$TILE.tmp" &&
      sips -s format png --cropOffset "$Y" "$X" -c "$H" "$W" "$TILE.tmp" --out "$TILE" >/dev/null &&
      sips -z "$ZH" "$ZW" "$TILE" >/dev/null &&
      rm -f "$TILE.tmp"
    ;;
  magick)
    IM=magick; command -v magick >/dev/null 2>&1 || IM=convert
    "$IM" "$IMG" -crop "${W}x${H}+${X}+${Y}" +repage -resize "${ZW}x${ZH}!" "$TILE"
    ;;
  pil)
    python3 - "$IMG" "$X" "$Y" "$W" "$H" "$SCALE" "$TILE" <<'PY'
import sys
from PIL import Image
img, x, y, w, h, s, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
im = Image.open(img).crop((x, y, x + w, y + h)).resize((w * s, h * s), Image.LANCZOS)
im.save(out)
PY
    ;;
  *)
    echo "tile.sh: no backend found (need sips, ImageMagick, or Python PIL)" >&2; exit 3
    ;;
esac

if [ $? -ne 0 ] || [ ! -s "$TILE" ]; then
  rm -f "$TILE.tmp"
  echo "tile.sh: $BACKEND backend failed to produce $TILE" >&2
  exit 3
fi

echo "backend: $BACKEND  region: ${W}x${H}+${X}+${Y}  scale: ${SCALE}x -> ${ZW}x${ZH}"
echo "NEXT: Read the tile below and confirm it shows the intended region (rule 2)."
echo "$TILE"

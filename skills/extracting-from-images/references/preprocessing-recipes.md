# Preprocessing recipes (extracting-from-images rules 1–2, 4)

Copy-paste recipes in three fallback tiers. Pick the FIRST installed tier per operation:
**sips** ships on every macOS; **ImageMagick** (`magick`, older installs `convert` /
`identify`) is the portable workhorse; **Python PIL/Pillow** covers everything else.
Probe availability once (`command -v sips magick convert tesseract pdftotext;
python3 -c "import PIL"`) and stop guessing. Write every output file to the scratchpad,
never into the user's repo (rule 2).

Substitute your paths for `IMG` (input), `T` (tile/output). All commands below operate on
copies — never modify the user's original image in place.

## 1. Probe dimensions and format (rule 1 — always first)

```bash
sips -g pixelWidth -g pixelHeight -g format "$IMG"          # macOS
magick identify -format '%w x %h  %m\n' "$IMG"              # ImageMagick ('identify' on older installs)
python3 -c "from PIL import Image; im=Image.open('$IMG'); print(im.size, im.format, im.mode)"
```

Reading the probe: estimate the glyph height of the TARGET text in pixels (target region
height ÷ lines of text in it). Single-digit-pixel glyphs will not survive a full-frame
read — crop. A "4K dashboard" arriving as an 800px-wide file has been downscaled: that is
rule 8 reportable state, and no ladder recovers detail the pixels no longer carry.

## 2. Crop a region to its own tile (rule 2a)

Preferred: `scripts/tile.sh "$IMG" X Y W H [scale]` — crop+upscale in one call, prints the
tile path. Manual equivalents (X,Y = top-left corner; W,H = region size):

```bash
cp "$IMG" "$T" && sips --cropOffset Y X -c H W "$T"         # sips: offset is Y-then-X, crop is H-then-W
magick "$IMG" -crop "${W}x${H}+${X}+${Y}" +repage "$T"
python3 -c "from PIL import Image; Image.open('$IMG').crop((X, Y, X+W, Y+H)).save('$T')"
```

After EVERY crop: Read the tile and confirm it shows the intended region before trusting
anything from it (rule 2). Off-by-one on which corner/order a tool expects is exactly how
wrong-coordinates crops happen — hence the confirm step, not memorized flag order.

## 3. Upscale the tile (rule 2b)

Default 4x (the `tile.sh` default — an example, not a threshold); go higher only if a
re-Read still leaves characters ambiguous.

```bash
sips -z $((H*4)) $((W*4)) "$T"                              # sips: height-then-width
magick "$T" -resize 400% "$T"
python3 -c "from PIL import Image; im=Image.open('$T'); im.resize((im.width*4, im.height*4), Image.LANCZOS).save('$T')"
```

## 4. Enhance (rule 2c — one transform at a time, re-Read between)

sips has no threshold/deskew — fall through to ImageMagick or PIL for those.

```bash
# grayscale + full contrast stretch
magick "$T" -colorspace Gray -normalize "$T"
python3 -c "from PIL import Image, ImageOps; ImageOps.autocontrast(Image.open('$T').convert('L')).save('$T')"

# hard threshold (crisp black/white text; try 50%, then 40/60 if it eats strokes)
magick "$T" -colorspace Gray -threshold 50% "$T"
python3 -c "from PIL import Image; Image.open('$T').convert('L').point(lambda p: 255 if p > 128 else 0).save('$T')"

# invert dark-mode screenshots (light text on dark reads worse; OCR expects dark-on-light)
magick "$T" -negate "$T"
python3 -c "from PIL import Image, ImageOps; ImageOps.invert(Image.open('$T').convert('RGB')).save('$T')"

# deskew a photographed/scanned page (do this BEFORE cropping cells out of it)
magick "$T" -deskew 40% +repage "$T"
```

## 5. Scanned or captured PDFs (rule 4 first, then rasterize)

`pdftotext` FIRST — if it emits real text, the PDF has a text layer and the machine-
readable source wins over any pixel read (rule 4):

```bash
pdftotext -layout "$PDF" -            # '-' = stdout; -layout preserves table columns
python3 -c "import pypdf,sys; print(pypdf.PdfReader('$PDF').pages[0].extract_text())"  # fallback tier
```

Only if the text layer is absent/garbage (scan-only PDF), rasterize at high resolution
and enter the ladder:

```bash
pdftoppm -r 300 -png -f 1 -l 1 "$PDF" "$OUTPREFIX"   # page 1 at 300 dpi
pdfimages -list "$PDF" && pdfimages -png "$PDF" "$OUTPREFIX"   # extract embedded scan images losslessly
```

No poppler installed: try `pypdfium2` (`python3 -c "import pypdfium2"`); if that is also
absent, Read the PDF directly (page-ranged) and treat any region you cannot resolve as a
rule 2 ladder candidate on a screenshot of the page, cropped per section 2.

## 6. Tesseract cross-read (rule 2d — second reader, never truth)

```bash
tesseract "$T" stdout --psm 6         # psm 6: uniform block of text (tables, paragraphs)
tesseract "$T" stdout --psm 7         # psm 7: single text line (one cell, one label)
tesseract "$T" stdout --psm 6 -c tessedit_char_whitelist=0123456789.,-%   # numeric cells
```

Diff tesseract's output against YOUR reading of the same tile: agreement corroborates
(CONFIRMED-eligible per rule 5); disagreement marks the value UNCERTAIN with both
readings stated; tesseract output alone is never truth — it confabulates on exactly the
same degraded inputs you do.

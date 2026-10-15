# WebP Converter

A private, unlimited image-to-WebP converter that runs entirely in your browser.
No uploads, no accounts, no conversion limits.

## Use it

Open `index.html` in Chrome, Edge or Firefox (double-click the file, or host it
anywhere, e.g. GitHub Pages or Netlify).

1. Drop images on the page, click **Choose images**, or paste from the clipboard.
2. Set **Quality** (75–85 suits most photos; 100 is lossless in Chrome/Edge).
3. Optionally pick a **Max width** to shrink oversized images for the web.
4. Click **Download** per image, or **Download all (.zip)**.

Changing a setting re-converts every image, so you can compare sizes before saving.
Accepts JPG, PNG, GIF (first frame), BMP, AVIF and SVG. Transparency is kept.

## How it works

The browser decodes each image, draws it to a `<canvas>`, and calls
`canvas.toBlob(…, "image/webp", quality)`. The only external files are Google
Fonts and JSZip (for the zip download); with no internet the converter still
works, using system fonts and single-file downloads.

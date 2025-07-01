# Logo Image Conversion Guide (SVG to 1024x1024 PNG)

This project provides a Makefile target (logo) to convert any SVG file in the graphics directory into a sharp, square 1024x1024 PNG with transparent padding, using Inkscape and ImageMagick. This method preserves the aspect ratio and avoids blurring.

## Prerequisites
- [Inkscape](https://inkscape.org/) (install via Homebrew: `brew install --cask inkscape`)
- [ImageMagick](https://imagemagick.org/) (install via Homebrew: `brew install imagemagick`)

## Usage
From the project root, run:

```
make logo
```

## How it works
1. **Inkscape** exports the SVG to a PNG with the largest dimension set to 1024px, preserving aspect ratio.
2. **ImageMagick** pads the PNG to a 1024x1024 square, centering the image and filling extra space with transparency.
3. The temporary PNG is deleted after conversion.

## Troubleshooting
- If your SVG uses advanced CSS color functions (like `light-dark()` or `var(--color, ...)`), replace them with standard color values for compatibility.
- If you see blurry output, ensure you are not using `sips` or other basic tools—only Inkscape and ImageMagick will produce sharp results.

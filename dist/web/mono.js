// mono-ui helpers for the web. Optional: the CSS works without this file.
//
//   import { setVariant, dither, ditherImage } from "./mono.js";
//
//   setVariant("round")                     switch <html data-mono>
//   dither(canvas, (x, y, w, h) => 0..1)    draw any brightness function as an 8×8 Bayer dither
//   ditherImage(canvas, img)                dither a photo/image into the canvas
//
// Everything is drawn in the variant's --m-fg colour on a transparent background.

const BAYER = [
  0, 32, 8, 40, 2, 34, 10, 42, 48, 16, 56, 24, 50, 18, 58, 26,
  12, 44, 4, 36, 14, 46, 6, 38, 60, 28, 52, 20, 62, 30, 54, 22,
  3, 35, 11, 43, 1, 33, 9, 41, 51, 19, 59, 27, 49, 17, 57, 25,
  15, 47, 7, 39, 13, 45, 5, 37, 63, 31, 55, 23, 61, 29, 53, 21,
];

export function setVariant(variant, el = document.documentElement) {
  el.dataset.mono = variant;
  try { localStorage.setItem("mono-variant", variant); } catch { /* storage blocked */ }
}

export function savedVariant(fallback = "square") {
  try { return localStorage.getItem("mono-variant") || fallback; } catch { return fallback; }
}

function inkOf(canvas) {
  const value = getComputedStyle(canvas).getPropertyValue("--m-fg").trim() || "#e2e2e2";
  const probe = document.createElement("canvas").getContext("2d");
  probe.fillStyle = value;
  const hex = probe.fillStyle; // normalised to #rrggbb
  return [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
}

/** True when the canvas sits in a light variant (paper), where ink is dark instead of light. */
export function isLight(el) {
  return getComputedStyle(el).getPropertyValue("--m-color-scheme").trim() === "light";
}

/** Dither a brightness function. fn(x, y, w, h, light) returns 0 (empty) .. 1 (full ink). */
export function dither(canvas, fn, ink = inkOf(canvas)) {
  const light = isLight(canvas);
  const ctx = canvas.getContext("2d");
  const { width: w, height: h } = canvas;
  const img = ctx.createImageData(w, h);
  const d = img.data;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const v = fn(x, y, w, h, light);
      if (v * 64 > BAYER[(y & 7) * 8 + (x & 7)]) {
        const i = (y * w + x) * 4;
        d[i] = ink[0]; d[i + 1] = ink[1]; d[i + 2] = ink[2]; d[i + 3] = 255;
      }
    }
  }
  ctx.clearRect(0, 0, w, h);
  ctx.putImageData(img, 0, 0);
}

/** Dither an <img> (already loaded) into the canvas, by luminance. */
export function ditherImage(canvas, image, { contrast = 1.1, invert = false } = {}) {
  const { width: w, height: h } = canvas;
  const tmp = document.createElement("canvas");
  tmp.width = w; tmp.height = h;
  const t = tmp.getContext("2d");
  const s = Math.max(w / image.naturalWidth, h / image.naturalHeight);
  const dw = image.naturalWidth * s, dh = image.naturalHeight * s;
  t.drawImage(image, (w - dw) / 2, (h - dh) / 2, dw, dh);
  const px = t.getImageData(0, 0, w, h).data;
  dither(canvas, (x, y, _w, _h, light) => {
    const i = (y * w + x) * 4;
    let l = (0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]) / 255;
    l = Math.min(1, Math.max(0, (l - 0.5) * contrast + 0.5));
    // on paper the ink is dark, so dark pixels get the ink
    return invert !== light ? 1 - l : l;
  });
}

/** A ready-made figure: a dithered sphere, like the Black Hole page's planets. */
export function sphere(x, y, w, h, light = false) {
  const cx = w / 2, cy = h / 2, r = Math.min(w, h) * 0.42;
  const dx = (x - cx) / r, dy = (y - cy) / r, d2 = dx * dx + dy * dy;
  if (d2 > 1) return Math.max(0, 0.12 - (Math.sqrt(d2) - 1) * 0.6) * (((x * 7 + y * 13) % 5) / 4);
  const z = Math.sqrt(1 - d2);
  const lit = Math.max(0, -0.45 * dx - 0.55 * dy + 0.7 * z);
  // on dark variants ink is light, so ink = light; on paper ink is dark, so ink = shadow
  return light ? 0.97 - lit * 0.9 : lit * 0.95 + 0.04;
}

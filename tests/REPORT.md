# Die detection test report

Run: 21 October 2026, Chrome (browser pane), `site/editor.html` at default settings unless noted.
Result: **18 of 18 cases pass.**

To run again: from the project folder, start a local server and open `tests/index.html`, then click **Run all tests**.

```bash
python3 tools/serve.py 8091 .
```

Then open http://localhost:8091/tests/

## What each case checks

- A design is found, with the expected number of pieces.
- Every cut path is closed and doesn't cross itself.
- **Gap from artwork:** the signed distance from the cut to the design edge, sampled every 0.5 mm. Negative values mean the cut sits inside the edge, as intended on sticker sheets. The closest point must be no nearer than the gap setting minus the curve tolerance and one pixel.
- **Artwork outside the cut:** no design pixels may fall outside the cut. On sheets, the check allows for the inset and the curve tolerance.
- The PDF export contains a `CutContour` Separation.
- The expected warnings appear.

## Results

| # | Case | Pieces | Nodes | Gap min / mean (target), mm | Art outside | Time | Warnings |
|---|---|---|---|---|---|---|---|
| 01 | Transparent PNG, one shape | 1 | 4 | 1.57 / 1.85 (2) | 0% | 0.8 s | – |
| 01b | Same, circle shape | 1 | 4 | 1.87 / 5.66 (2) | 0% | 0.2 s | Safe zone (art within 3 mm) |
| 01c | Same, rounded rectangle | 1 | 8 | 1.98 / 7.08 (2) | 0% | 0.3 s | Safe zone (art within 3 mm) |
| 02 | Separate letters, gap 0.5 mm | 4 | 35 | 0.25 / 0.51 (0.5) | 0% | 0.8 s | – |
| 02b | Separate letters, join 10 mm | 1 | 26 | 0.25 / 1.33 (0.5) | 0% | 0.8 s | – |
| 03 | White-background JPG with holes | 1 | 15 | 1.63 / 1.91 (2) | 0% | 0.8 s | – |
| 04 | Solid green background | 1 | 22 | 1.85 / 2.01 (2) | 0% | 0.9 s | – |
| 05 | Dark background, no transparency | 1 | 30 | 1.71 / 1.96 (2) | 0% | 0.9 s | – |
| 06 | Thin lines and thin text | 1 | 15 | 1.77 / 1.98 (2) | 0% | 0.7 s | – |
| 07 | 40 separate dots, gap 0.5 mm | 40 | 80 | 0.33 / 0.45 (0.5) | 0% | 1.9 s | – |
| 08 | Soft drop shadow, threshold 40 | 1 | 15 | 1.58 / 1.98 (2) | 0% | 1.0 s | – |
| 08b | Soft drop shadow, threshold 150 | 1 | 12 | 1.62 / 2.04 (2) | 0% | 0.4 s | – (artwork larger: shadow excluded) |
| 09 | Design touches the image edges | 1 | 15 | 1.94 / 1.97 (2) | 0% | 0.6 s | Touches edges |
| 10 | Photo with no clear background | 1 | 32 | 1.64 / 1.97 (2) | 0% | 0.6 s | Touches edges (suggests Rectangle) |
| 11 | Tiny image (120 px) | 1 | 9 | 1.64 / 1.88 (2) | 0% | 0.1 s | Low resolution (36 dpi) |
| 12 | Very large image (6000 × 4000) | 1 | 6 | 1.81 / 1.95 (2) | 0% | 1.3 s | – |
| 13 | Synthetic A4 sheet, 6 stickers, white glow | 6 | 64 | −1.82 / −1.39 (−1.4) | 0% | 1.9 s | – |
| 14 | Real sheet (Rio the Explorer) | 9 | 677 | −0.69 / −0.31 (−0.4) | 0% | 1.3 s | Low resolution (137 dpi), 1 narrow area |

## Problems found and fixed

1. **Sheet mode counted a white glow as a sticker** (case 13 found 7 pieces instead of 6). A near-white spot in the background glow, with a few noisy pixels inside, passed as a sticker. Fix: on sheets, a piece must be at least 15% coloured artwork to count as a sticker.
2. **The "design touches the image edges" warning almost never appeared** (case 09). It needed more than 25% of the image border to be touched. Fix: it now warns at 3%, and suggests the Rectangle or Rounded shape for photos and full-bleed artwork (case 10).
3. **Test fixes (not tool bugs):**
   - The shadow-threshold case compared cut sizes, but the tool keeps the cut at the requested size. It now compares the artwork size.
   - The gap check sampled only the curve's nodes, so it missed the closest points on long straight sides. It now samples every 0.5 mm.
   - The sheet "art outside" check now allows for the curve tolerance.

## Known limits

- **Photos without a clear background** are traced around their whole frame. Use the Rectangle or Rounded shape for those.
- **Sticker sheets** need a white border around each sticker. Borders thinner than about 0.7 mm leave little room for the cut. The Rio sheet's borders measure about 0.74 mm.
- **Semi-transparent shadows** count as part of the design unless you raise the Transparency threshold (case 08b).

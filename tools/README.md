# Contribution artwork

```bash
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/render_contributions.py
.venv/bin/python tools/render_contributions.py --check
```

The renderer writes transparent, lossless animated WebPs and still PNGs to `assets/contributions/`, with separate `-light` and `-dark` versions. The images are 960 × 240 pixels and display at up to 420 × 105 pixels in the README. Each 12-second cycle includes a short comparison sequence and a hold. The four sequences have different start times. A fixed palette keeps stationary text consistent across frames. Lossless WebP preserves transparency and stores only the changes between frames.

The diagrams illustrate the README's linked results: VMAF uses the 2.10× end of the range; Ion normalizes read time to 100 → 58 and scan time to 100 → 48; SpiceDB normalizes latency to 100 → 13 and allocation to 100 → 3. Pyrefly uses an illustrative `self.name` assignment inside `Account.__init__`. Animation time is scaled for reading and is not a benchmark measurement.

The default fonts are Arial Bold, Arial, and Courier New on macOS, or DejaVu Sans Bold, Sans, and Sans Mono on Linux. Use `--display`, `--sans`, and `--mono` to supply other local font files. Fonts are not included. Changing fonts changes the output; bounds checks reject text that exceeds the canvas or its allocated column.

Verification decodes every WebP frame and compares it with the corresponding rendered state, checks the complete cycle duration and periodicity, and validates transparency, still images, and drawing bounds. The README uses GitHub's [theme-dependent pictures](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github) and supplies still images for reduced motion. Numerical checks do not assess appearance in GitHub or a browser. Open the profile or exported animations for a visual review.

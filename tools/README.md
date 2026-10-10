# Contribution artwork

```bash
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/render_contributions.py
.venv/bin/python tools/render_contributions.py --check
```

The renderer writes GIFs and still PNGs to `assets/contributions/`. The images are 960 × 480 pixels and display at up to 480 pixels wide in the README. Each 20-second cycle has a short comparison sequence followed by a hold. The four sequences have different start times. A fixed palette keeps stationary text consistent across frames.

The diagrams illustrate the README's linked results: VMAF uses the 2.10× end of the range; Ion normalizes read time to 100 → 58 and scan time to 100 → 48; SpiceDB normalizes latency to 100 → 13 and allocation to 100 → 3. Pyrefly uses an illustrative `self.name` assignment inside `Account.__init__`. Animation time is scaled for reading and is not a benchmark measurement.

The default fonts are Iowan Old Style, Arial, and Courier New on macOS, or DejaVu Serif, Sans, and Sans Mono on Linux. Use `--serif`, `--sans`, and `--mono` to supply other local font files. Fonts are not included. Changing fonts changes the output; bounds checks reject text that exceeds the canvas.

Verification decodes every GIF frame and compares it with the corresponding rendered state, checks the complete cycle duration and periodicity, and validates still images and drawing bounds. It does not assess appearance in GitHub or a browser. Open the exported GIFs for a visual review.

# Profile artwork

The profile uses the portfolio's Poppins lettering, coral/violet/green accents,
64px coordinate cells, shallow corners, and a lower U-shaped portrait fade.

The shipped GIFs provide reliable README animation. Matching PNGs are selected
for reduced-motion preferences; each visual also has dark, light, and mobile
variants. All SVGs are self-contained: logos are embedded, Poppins is outlined,
and the portrait is embedded as a data image. No scripts, external fonts, or
external image services are required when the profile is viewed.

To rebuild, install Python 3.12+ and Node.js 22+, then run from the repository root:

```sh
python -m pip install -r scripts/requirements.txt
npm install
npm run build
```

The build uses a temporary directory for animation frames, renders SVGs with
Sharp, and encodes 48-frame GIFs with a fixed per-animation palette. It updates
only the shipped artwork. `assets/fonts/OFL.txt` contains the Poppins license;
technology mark sources and licenses are in `assets/tech/ATTRIBUTION.md`.

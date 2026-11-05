# Vector construction and export

R1 §4.1–4.2 and R2 §4 contribute outline audits, spacing units, and controlled geometry (`REPORT-H`). Grids are construction tools, not evidence of quality; optical corrections are legitimate. Application keyboard shortcuts and tool names vary by version and platform. Verify them rather than reproducing the reports' exact menu recipes.

## Construct deliberately

Keep an editable master before boolean operations and text outlining. Set an artboard/viewBox, coordinate system, useful geometric relationships, and explicit export padding. Use as few points as necessary for a clean contour; fewer is not automatically better. Inspect tangency, cusps, flat spots, inconsistent radii, unintended overlaps, open contours, self-intersections, duplicate segments, and tiny fragments in outline and filled views.

Mirror when symmetry is intended, then inspect optical balance. Document any overshoot or asymmetric correction. Compare symbol/wordmark perceived weight and spacing at actual size. An outlined stroke can alter joins and bounds; compare before and after expansion. Cut true holes through shapes when transparency is required. Do not use a white patch as a universal knockout.

## Static outlined export profile

The included validator accepts `svg`, `g`, `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, `title`, and `desc` in the SVG namespace. It permits explicit solid fills/strokes, basic presentation attributes, transforms, IDs, and a small accessibility-attribute set. It excludes CSS/style/class, text, links, `<use>`, definitions, images, filters, gradients, masks, clipping, animation, and foreign namespaces. See [tool contract](tool-contract.md) for the exact implemented limits.

This narrow profile is useful for flat logo exports and deterministic tests. Rich valid artwork may fail it. Preserve the master, explain rejection, and intentionally create a flat derivative when appropriate. Never auto-flatten, remove content, or overwrite originals as an unreported “repair.” Do not rename SVG to AI/EPS/PDF to imply conversion.

## Human checks after automation

The script checks finite values, limited path grammar, supported tags/attributes, structural relationships, and resource limits. It does not determine meaningful bounds, optical centering, clear space, winding intent, kerning, print cut quality, or whether the geometry conveys the brand. View in a second renderer/editor; inspect small, large, reversed, and monochrome variants.

Before delivering: ensure source and outlined exports match; strokes and holes survive scaling; viewBox does not clip; the intended clear space is documented; title/description and embedding guidance are correct; filenames identify variant/color space/status; and all exports correspond to the approved version. Real browser embedding needs its own accessibility and security handling.

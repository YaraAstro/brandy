# Tool contract and failure interpretation

Python **3.11+** is required by the pinned Pillow version. Use a virtual environment; dependencies and tested versions are in `requirements.txt` and `requirements-dev.txt`. Runtime: defusedxml (guarded XML parsing), resvg-py (native static rasterization), Pillow (PNG diagnostics). Development: pytest and PyYAML. `check_package.py` uses PyYAML, so install development requirements for that check.

## SVG validator

`python scripts/validate_svg.py INPUT.svg [MORE.svg ...] [--json]`

Exit 0 means all files meet the package profile; exit 1 means an input or profile failure; argparse uses exit 2 for invalid usage. JSON output is an array of per-input reports, even for one input. Warnings do not fail. Sources are read only and never sanitized or rewritten. File-extension tricks do not bypass parsing; compressed SVGZ is unsupported.

The `flat-outlined-v1` profile requires a namespaced SVG root and a finite positive `viewBox`. Optional root dimensions are positive numeric values, optionally in `px`; other geometry uses unitless numbers. Allowed tags: `svg` at root only, `g`, `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, `title`, `desc`. Only root/group can contain children. Text content is allowed only in title/description. Containers can use IDs, explicit solid fill/stroke, fill rule, opacity, stroke width/cap/join/miter limit, and basic transforms. Geometry additionally has its relevant coordinates. Root can have centered-meet `preserveAspectRatio` and supported role/ARIA attributes. IDs must be unique and accessibility ID references must resolve.

Paint values are `#RGB`, `#RRGGBB`, `black`, `white`, or `none`. Convert other approved colors deliberately in an export copy. Supported transforms: matrix (6 values), translate/scale (1–2), rotate (1 or 3), skewX/skewY (1). The path parser checks recognized commands, initial moveto, parameter counts, finite numeric values, nonnegative arc radii, and separated literal 0/1 arc flags. It permits repeated command parameter groups. It is not a complete SVG grammar or winding/geometry validator; some legal compact syntax may be unsupported, and accepted geometry can be visually empty.

DTD/entities, non-declaration processing instructions, foreign element/attribute namespaces, unknown attributes, event handlers, CSS/style/class, references such as href or paint URLs, text, image/data URI, use/defs, clipping/masking, filters, gradients, links, and animation are rejected. XML comments are ignored as data. Extra unused namespace declarations convey no resource capability.

Limits: input ≤1,000,000 bytes; ≤5,000 elements; nesting ≤32; ≤50,000 path tokens per path and ≤50,000 total path coordinate numbers; numeric magnitude ≤1,000,000; ≤32 transform functions per transform list. These bounds reduce accidental resource use. The parser still builds a bounded in-memory tree before inspecting depth/count. No memory quota, OS sandbox, exploit-resistance guarantee, network isolation, or exhaustive SVG conformance is provided. Native/XML/image dependencies still require maintenance. For hostile inputs, add process/container-level resource and network restrictions outside this package.

## Rendering tests

`python scripts/render_tests.py INPUT.svg --out NEW_DIRECTORY [--sizes 16,24,32,48,64,128,256] [--timeout 30]`

Exit 0 means diagnostics were generated; 1 means a read/profile/render/output failure; invalid CLI arguments use 2. Only a new output directory is accepted. Existing files, sources, and previous diagnostic directories are preserved. A failure while writing the final output can leave partial files; success is reported only after `results.json` is written. Use a new directory after correcting a failure.

The parent validates input and snapshots exactly those bytes, then renders that snapshot in a child process (default 30-second timeout; configurable 1–60 seconds). This avoids input-file changes between checking and rendering. The child loads no system fonts and receives no external resource paths; the validator has already rejected references and richer features. The timeout limits runtime, not memory. Sizes are longest viewBox edges: 1–12 unique integers in [8,1024], placed on square canvases with centered aspect-preserving fit. Transparent padding is not automatic logo clear space. Very wide wordmarks should use appropriate larger size tests.

Per size: transparent PNG, light/dark/neutral composites, grayscale, black and white alpha silhouettes, and a blur diagnostic (`max(0.5,size/32)` px radius). A native-size contact sheet and `results.json` record input hash, renderer version, size/background choices, alpha bounds, and canvas-edge contact. Alpha bounds are not analytic vector bounds; edge contact is a warning signal, not proof of clipping. Empty renders fail. Blur and mono are pixel derivatives, not new approved vector assets. Opaque internal white details merge in a silhouette. Use intentionally authored one-color variants for final assets.

At the maximum options, the contact sheet can approach 100 million pixels; reduce sizes/count when memory is limited. Renderer output is not an accessible HTML application, color-conformance verdict, browser compatibility certificate, audience test, print proof, or legal review.

## Package check

`python scripts/check_package.py . [--require-manifest]`

Checks required paths, local Markdown link targets/simple heading anchors, frontmatter/UI metadata, report hashes, and an optional full package checksum inventory. It rejects escaping link/manifest paths and symlinks. It does not crawl external URLs, parse every Markdown dialect, validate arbitrary schema completeness, or evaluate design behavior. Manifest verification excludes itself and Python/pytest caches. Keep virtual environments and generated application outputs outside the skill directory when verifying the release inventory.

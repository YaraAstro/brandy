# brand-identity-director

Version 1.0.0 • built 2026-11-05 • Python 3.11+ for optional tools

A reusable directing skill for discovery, positioning, verbal identity, visual concepts, identity systems, packaging, marketing, digital applications, critique, refinement, and delivery. It combines the two user-supplied NotebookLM reports with explicit evidence controls and practical production checks. It does not require a connector, image model, or paid service to load.

## Install and invoke

Unzip and keep the `brand-identity-director` directory intact. Review the source reports and scripts before use. For Codex, copy that directory into your own skills location (normally `~/.codex/skills/`) and reload skills or restart the app if needed. This download is not installed automatically. Other agents can load `SKILL.md` and resolve its relative references; product-specific discovery and `agents/openai.yaml` support may differ. No universal cross-product compatibility is claimed.

```text
Use $brand-identity-director in discover mode.
We sell refillable household cleaners in two languages. Use the attached
customer research, existing identity, and packaging dimensions. Establish
positioning and a brief before proposing visual directions.
```

Choose `discover`, `explore`, `design`, `critique`, `refine`, `deliver`, or `full`. See [examples](examples/usage.md). Templates are intentionally unfinished forms to fill per project, not sample research. The example mark is only a tooling fixture, not a proposed client identity or cleared trademark.

## Optional tools

Run these commands from the extracted skill directory. On Windows use `.venv\Scripts\python.exe` instead of `.venv/bin/python` (activation is optional).

```sh
python -m venv .venv
# Windows:
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv/Scripts/python.exe scripts/validate_svg.py examples/assets/sample-mark.svg --json
.venv/Scripts/python.exe scripts/render_tests.py examples/assets/sample-mark.svg --out visual-tests
.venv/Scripts/python.exe scripts/check_package.py .
.venv/Scripts/python.exe -m pytest -q
```

On macOS/Linux substitute `.venv/bin/python` throughout. `requirements-dev.txt` includes runtime requirements. `requirements.txt` alone is sufficient for validation/rendering. Exact tested dependency versions are pinned; supported Python wheels must exist for your OS/architecture. `resvg-py` is a native wheel; unsupported platforms may require a Rust build toolchain. No Cairo installation or browser is required. See [tool contract](references/tool-contract.md) for supported SVG features, limits, failure behavior, and renderer limitations.

## Package map

- `SKILL.md`: concise entry point and mode router.
- `agents/openai.yaml`: optional Codex UI metadata; normal implicit discovery remains enabled.
- `references/`: topic procedures, evidence policy, source map, primary standards, tool contract, and untouched source reports.
- `templates/`: intake, strategy, concepts, scorecard, guidelines, handoff, and application specifications.
- `scripts/`: SVG validator, multi-size renderer, and package/link validator.
- `tests/`: meaningful positive, negative, CLI, rendering, and containment checks.
- `examples/`: mode requests, worked reasoning, and synthetic vector fixtures.
- `VALIDATION.md`: repeatable technical and behavioral evaluation.
- `BUILD-REPORT.md`: results of this particular build, including limits.
- `MANIFEST.sha256`: SHA-256 for each packaged file except itself.

## Evidence and limits

The initial reports are retained with byte hashes and section-level traceability in [evidence-and-sources.md](references/evidence-and-sources.md). Their assertions are not automatically evidence. Association-based design ideas remain hypotheses; standards apply only in their stated scope. No font-brand historical claims are needed to use this skill. No audience study, legal clearance, printer proof, or client acceptance is implied by passing tests.

The helper profile intentionally excludes live text, CSS, embedded raster images, links, filters, animations, and reference-based composition. Keep richer editable masters outside this export profile. For external files, use maintained dependencies and a resource-limited process; this package is not a security sandbox or complete SVG standard validator.

## Reuse and provenance

The reports were supplied by the user; preserve their provenance and do not assume a public redistribution license. Third-party standards are linked, not bundled. No font binaries, commercial mockups, or third-party logos are included. This package grants no rights in any future names or marks; check source permissions before redistributing the package or generated assets. See [rights and trademark](references/rights-and-trademark.md).

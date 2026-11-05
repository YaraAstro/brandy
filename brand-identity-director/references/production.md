# Production and handoff

R1 §5.3 motivates organized handoff (`REPORT-H`), not a mandatory file-format or font-bundling checklist. Match exports to actual use and tooling.

## Build an honest asset set

Maintain an editable master, outlined exchange vector, digital raster sizes as needed, approved mono/reversed variants, and process-specific print files where tools and vendor specs permit. SVG is a digital vector format, not a CMYK print master. Choose an actual PDF/AI/EPS export workflow only if it is supported and inspected. Do not make a valid file by changing its extension. If a native authoring format is unavailable, say so and deliver an authentic supported exchange format with limitations.

Use filenames such as `brand-mark-primary-rgb-v1.svg` or `brand-lockup-reversed-rgb-v1.png`. Include status (approved/provisional), dimensions, color space/profile, variant, and intended use in the manifest. Keep client deliverables separate from source research and rejected concepts. Do not ship unlicensed fonts or mockup source files by default.

## Preflight by output

Digital: verify viewBox, aspect ratio, alpha, actual pixel sizes, backgrounds, embedding names, file weight, and consistent appearance in target renderers. Print: obtain trim/bleed, ICC/output intent, ink limits, spots, overprint, separations, raster resolution at placement size, dieline/finishing layers, and vendor proof requirements. CMYK conversions depend on profile, substrate, and process; do not infer them from an RGB preview. Request a physical or contract proof when the application requires it.

Typography: record exact family/version/axis settings, roles, acquisition URLs, and permitted deployment. Keep live and outlined sources where allowed. Provide license references, not legal interpretations of an unseen license. Images/illustrations: record ownership, source, permissions, model/property releases as relevant, and generated-asset provenance.

## Organize for the next person

A suggested handoff: `00-start-here/`, `01-masters/`, `02-digital/`, `03-print/`, `04-guidelines/`, `05-licenses/`, `06-qa/`. Omit unused directories and explain unavailable deliverables. The start-here file should say which logo to use where, minimum sizes tested, known limitations, how to acquire type, and whom to contact. Include a versioned asset inventory and checksum list, approved guideline set, decision/evidence log, and open issues with owners.

## Release gate

Open exports from the packaged copy, not just working files. Inspect filenames, links, duplicates, corrupt files, color/variant consistency, and intended dimensions. Include QA environment and test dates. Separate client creative acceptance, technical QA, printer acceptance, and legal review status. A render test proves neither legal clearance nor print readiness. Deliver the actual package and concise next actions; do not silently publish, upload to a live brand portal, or alter repositories unless requested.

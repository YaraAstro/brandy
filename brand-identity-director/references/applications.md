# Application direction

R1 §5.2 introduces context-first testing (`REPORT-H`); the specifications here are `PRACTICE`. Establish content, dimensions, materials/devices, viewing conditions, and approval owner before calling an application production-ready. Use [application specification](../templates/application-spec.md).

## Packaging

Obtain the converter's actual dieline, units, scale, material, print process, printable areas, folds/glue zones, seams, closures, bleed/safe-area instructions, finishing, and tolerances. Do not invent a dieline from a mockup. Separate artwork from technical layers; keep cut/fold/varnish/foil naming and spot-color treatment aligned to the vendor's instructions. There is no universal bleed, minimum line width, or CMYK recipe.

Map front/back/side hierarchy: brand, product, variant, quantity, instructions, required regulatory information, barcode, and batch/expiry areas. Have the responsible product/regulatory reviewer confirm local label content and claims. Barcode graphics need the correct symbology, quiet zones, scaling, contrast, and physical scan verification from the applicable standard/vendor workflow; a decorative placeholder cannot be called validated.

Test printed actual-size samples, shelf/e-commerce thumbnails, variant discrimination, multilingual expansion, and material legibility (transparent bottles, metallic stock, embossing, or curved surfaces). Rendered shadows cannot prove ink behavior, overprint, trapping, finish registration, or sustainability. Use substrate-specific proofing and vendor approval before final release. Mockups should identify simulated materials and provisional copy.

## Marketing

Define campaign objective, audience task, channel, offer/CTA, message hierarchy, format/safe areas, asset rights, and success measure. Build adaptable components for headline, product/photography, supporting proof, and CTA. Check text cropping in channel-specific previews, subtitles/alt text, and mobile reading. Verify current channel specifications instead of freezing platform dimensions into the skill.

Keep claims substantiated, generated imagery honest, endorsements authorized, and copy consistent across landing page and ad. Develop variants through meaningful message/composition changes rather than only recoloring. Experiments require a real allocation and measurement plan; concept preference is not conversion evidence.

## Web and digital

Map brand roles into semantic design tokens for text, surfaces, actions, statuses, type, spacing, and borders. Record units and fallbacks. Define responsive logo variants using observed space constraints, not arbitrary device stereotypes. Test light/dark themes, favicon/avatar masks, crowded headers, loading failures, and no-image states. Preserve live text and accessible names.

Show at least one content-rich page/component and one compressed context. Inspect keyboard, focus, contrast, reflow, text resize, localization, and system-font fallback. An SVG preview does not establish browser/CSS/framework behavior; implement and test real pages only when that work is requested. Give implementation teams token mappings and asset/embedding notes rather than an unexplained moodboard.

## Other media

For apparel, signage, vehicle graphics, laser cutting, embroidery, or motion, identify process constraints and require a relevant specialist/sample test. Micro icon geometry may need a deliberately simplified manufacturing variant. Record changes and their permitted uses so a process-specific compromise does not replace the primary master accidentally.

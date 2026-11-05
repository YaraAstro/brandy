# Accessibility in brand applications

`STANDARD`: Use [WCAG 2.2](https://www.w3.org/TR/WCAG22/) within its web-content scope. A brand palette or logo sheet alone cannot establish whole-product conformance. Packaging requirements depend on market/product and are not defined by WCAG.

## Contrast and semantics

For text, [SC 1.4.3 AA](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) requires 4.5:1, or 3:1 for large text (at least 18 pt regular or 14 pt bold). Text that is part of a logo/brand name has an exception under this criterion; this is not permission to make surrounding copy or controls unreadable. [SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) requires 3:1 for applicable component/state information and graphical content against adjacent colors, with its stated exceptions. Verify the actual pair and role, including disabled/inactive exceptions as applicable. Do not round a below-threshold ratio up to a pass.

Evaluate approved color values with the WCAG relative luminance method in sRGB; composite transparency against the real background first. Anti-aliased edge pixels are not the source colors used for the nominal ratio, but thin strokes still need visual inspection. Save pair, ratio, size/weight, context, and criterion. A colorblindness simulation is a useful diagnostic, not a substitute for contrast checks or user testing.

SC 1.4.1 prohibits using color as the only visual means of conveying information. Pair error/status color with text, icons, patterns, or other cues. Do not let a brand accent double as every status. SC 1.1.1 requires suitable text alternatives; use an informative name for meaningful brand images, or a decorative treatment when redundant. Linked brand marks need an accessible link name appropriate to the destination.

## Responsive and interaction checks

Keep body/content text live. Test 200% text resize (SC 1.4.4) and reflow at the equivalent of a 320 CSS px wide viewport for applicable horizontally written content (SC 1.4.10, including its exceptions). Inspect font fallbacks, text spacing, localization, and focus visibility (SC 2.4.7). Pointer targets under [SC 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) generally need 24 × 24 CSS px, with spacing and other exceptions defined by the criterion; the visible logo need not equal the link's hit area.

For motion or rich media, check relevant criteria for pause/stop/hide, flashing, and interaction behavior. Provide reduced-motion alternatives as a design practice and assess the applicable conformance target. Static renderer outputs do not test these behaviors.

## Evidence and deliverable

Provide approved pair tables, inverse variants, embedding/alt guidance, type minimums justified by testing, interaction notes, and unresolved issues. Test real pages with keyboard and assistive technology as appropriate. For packaging, perform physical-size reading tests and obtain product/jurisdiction-specific label review. State exactly what was tested; do not call the identity “WCAG certified.”

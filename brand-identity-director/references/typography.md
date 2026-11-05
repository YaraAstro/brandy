# Typography and identity architecture

R1 §2 and R2 §2 offer a type-trait lens and logo taxonomy (`REPORT-H`). Their exact font-brand attributions, causal emotion stories, “half the payload,” and absolute failures from changing font categories are unverified. Do not reuse those histories as facts.

## Choose by function and observed form

Compare width, weight range, stroke contrast, apertures/counters, terminals, x-height, spacing, numerals, punctuation, diacritics, and script coverage. Describe the actual letterforms before proposing audience associations. A serif is not inherently luxurious; a sans is not inherently modern or trustworthy. Check the foundry's current specimens, supported languages, axis ranges, license terms, and release version. Cite original documentation for claims of origin or usage.

Use a matrix: role → candidate/version → specimen/task → language coverage → availability/licensing → strengths/risks. Test the real brand name, product names, long headings, small labels, prices, tabular data, and ambiguous glyphs such as I/l/1 and O/0. Test body text independently from the wordmark. Compare actual sizes, line spacing, and backgrounds; attractive display type can fail dense instructions.

## Architecture and customization

Choose wordmark, symbol, combination mark, emblem, lettermark, or mascot from name equity, audience needs, and deployment constraints, not a fixed rule about company maturity. A long name may use a full lockup plus a compact authorized variant. Icons without a visible name need an accessible label in context.

Keep live text during exploration. Use variable axes only if the font provides them; optical sizing and slant are not universal features. Document selected values and fallbacks. Before outlining a logo, preserve an editable master and record source font and permitted modifications. Customizing outlines does not erase license obligations or automatically create exclusive rights. Inspect kerning optically in the actual word, including unusual pairs and small sizes; equal numeric gaps need not look equal.

## Deliverable rules

Specify display/body/utility roles, sizes or responsive ranges, line height, tracking, weight mapping, fallbacks, and multilingual behavior. Supply font files only when redistribution is permitted. Otherwise provide acquisition links, exact names/versions, and setup notes. Outlined SVGs avoid runtime font dependency but are no substitute for accessible live content in a webpage or for an editable typography master.

The restricted validator rejects live `<text>`; this is an export-profile choice. It is not a recommendation to outline all web text. Test font loading, fallback layout shift, zoom, reflow, and text in actual browsers during digital application QA.

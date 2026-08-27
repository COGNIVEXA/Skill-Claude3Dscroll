# The Design Bar

Wiring the libraries together correctly and making the page actually good are the same job, not two jobs. A page can hit every frame, scroll silky-smooth, and still read as generic AI output if the type is weak, the palette is a default, or the layout is the same three-column pattern every automated build reaches for. This document is the bar a build has to clear before it counts as done.

## 1. Commit to one page grammar

Pick exactly one — each of these rules out the others by design, so don't blend traits across them.

- **Cinematic single-take** — one continuous scroll-driven sequence, often built on frame-scrubbed video or a single authored camera path through a 3D scene. There's no conventional section break; if a hard cut appears, it's a deliberate device, not a default.
- **Chaptered narrative** — distinct sections/acts, each pinned while it makes its point, then released. The boundaries between them are real and legible — a reader always knows which chapter they're in.
- **Live reactive surface** — a persistent surface (shader field, particle system, live 3D object) that responds to pointer or scroll, with content placed on or beside it rather than the surface itself carrying a linear story.
- **Continuous 3D world** — the entire page is one fixed stage; the visitor travels through a coherent space (falling into a scale model, moving between locations) instead of scrolling through a stack of sections. No section boundaries anywhere.
- **Type-led poster** — typography is the lead; 3D and motion support it rather than compete with it. Confident, oversized type systems with minimal surrounding chrome.
- **Curated gallery** — a sequence of distinct pieces (products, case studies) each given its own full treatment, browsed more like a collection than read like a story.
- **Dual-pane stage** — two panes/viewports moving together under one shared scroll or interaction (a 3D object beside its spec sheet, a before/after pairing).
- **Hard-cut sequence** — deliberate, jarring cuts between fully different visual grounds (a light section slamming into an inverted dark one), used as punctuation rather than happening by accident.

## 2. One signature interaction, required

Every build needs one interaction invented specifically for it — something worth a screenshot or a mention. A recolored spotlight, a generic parallax layer, or "the cursor nudges a gradient" doesn't clear this bar. The signature move should grow out of what the content is actually about, not get bolted on at the end because a build needs one.

## 3. The differentiation check

If this skill has already produced a build earlier in the same project/session, a new build has to differ from every earlier one on at least 4 of these 6 axes: **grammar, navigation model, hero treatment, act structure, ending, signature interaction**. Falling short of that means revising the plan, not shipping something that reads as a near-duplicate.

## 4. A feeling arc before any section gets built

Before writing a single section, write one line per act: *what the visitor should feel, and exactly what on screen produces that feeling.* If two adjacent acts land on the same feeling, one of them is filler — cut it or change its job.

Shape (illustrative, not a template to fill in verbatim):
```
Act 1 — Awe:      falling into a handmade scale model of Earth, disorienting scale shift
Act 2 — Intimacy: landing in a single place, camera settles, ambient detail
Act 3 — Contrast: cross-cut to a second, opposite location
Act 4 — Resolve:  rise back to the workbench — the frame closes where it opened
```

## 5. One engineered high point

Apply the peak-end effect literally: a page is remembered by its high point and its ending, not its average moment. Choose exactly one moment to be that high point and give it:
- the largest share of the production/asset budget on the page
- a beat of relative stillness right before it, so contrast makes it register
- the most scroll distance to land in

A page that tries to peak three times ends up peaking nowhere — everything reads as the same intensity and nothing stands out from it.

## 6. The type floor

- **Two font families, maximum.** A display face and a text face, or a single face used across several weights. Never three or more.
- **Tracking tightens as size increases.** Large display type gets tight or negative letter-spacing; small type gets normal-to-slightly-open spacing — the reverse of the mistake of loosely tracked giant headlines.
- **Measure: 45–75 characters per line** for reading text. Body copy should never run edge-to-edge on a wide viewport.
- **Line-height moves inversely with measure/size** — larger type on shorter lines gets tighter line-height; smaller type on longer lines gets looser line-height.
- **Light text on a dark ground needs compensation on three fronts:** it optically reads heavier and blurs more than the same weight would on a light ground, so trim the weight slightly, add a touch of positive tracking, and re-check contrast with a computed number rather than a glance (see `qa-verification.md`).
- **Never let a headline wrap past 2–3 lines on an actual mobile viewport** — check the real breakpoint, not a narrowed desktop window.

## 7. A spacing scale with genuine rhythm

- Base unit: **4px**. Every spacing value is a multiple of it.
- **More space above a heading than below it** — this is what makes a heading read as introducing what follows rather than floating ambiguously between two blocks.
- **Section padding needs to be fluid** — desktop vertical rhythm (roughly 160–240px between major sections) has to scale down on mobile via `clamp()` or breakpoints, not carry over 1:1. A phone doesn't have room for desktop-scale air.

## 8. Color: six roles, one accent

Define roles, not just hex codes:
1. Background (primary ground)
2. Surface (panels/cards distinct from the background)
3. Primary text
4. Secondary text — **tinted toward the accent or background hue, never flat grey**
5. Border/divider
6. Accent (exactly one, spent sparingly on whatever genuinely needs the visitor's attention)

Rules:
- **No pure black (`#000`) or pure white (`#fff`)** as the body background/text pair — near-black and near-white give the page a hue identity instead of reading as unstyled browser defaults.
- **Document the light/dark handling explicitly.** Either the page commits to a single mode throughout, or — for a hard-cut page that switches grounds — write down which roles invert and re-verify text contrast independently on both grounds.

## 9. Depth from five tools, not one

Leaning on a single drop-shadow for every sense of depth is one of the fastest tells of generic output. Combine:
1. **Offset shadow** — directional rather than a centered blur, implying an actual light source
2. **Edge light** — a thin highlight on the side facing that implied light source
3. **Scale-and-blur as distance** — background elements slightly smaller and softer, not just darker
4. **Overlap** — an element physically breaking out of its container reads as depth more strongly than shadow alone
5. **Grain** — a light noise layer breaks up flat gradient banding and cuts the "clean AI render" quality

For any 3D content in the scene, "depth" also means real environment lighting and a tone-mapped, lightly post-processed render — not the renderer's raw output under a bare ambient/directional light pair. See `references/asset-sourcing.md` for the concrete baseline and for where to pull real models/HDRIs/textures instead of hand-building a product from primitives.

## 10. A supplied brand kit outranks this document

If the requester provides brand guidelines (palette, type, logo rules, tone), those hard constraints win — including ones that would forbid something this skill would otherwise reach for (a brand that bans gradients outright, or mandates an accent that clashes with the "one accent" default). Apply the brand kit's rules first, and treat this document's defaults as what fills the gaps.

## 11. The "don't ship this" list

None of these should make it into a finished build — they're the fastest tells of generic automated output:
- Identical feature-card grids (three or six matching cards: icon, title, paragraph, repeated verbatim)
- `01 / 06`-style numbered counters used as a navigation crutch
- Generic "scroll to explore" prompts/chevrons standing in for the page teaching its own interaction
- Gradient text as a default headline treatment
- Em dashes in body copy — use a period, a comma, or restructure the sentence
- Invented statistics or fabricated metrics ("40% faster," "10,000+ users") not sourced from the requester
- Decorative fake dashboards or fake data visualizations
- The violet-to-blue-to-pink gradient family that's become a visual cliché for "AI product"
- The cream-and-brass "artisan" palette every craft/maker brand defaults to when no palette is specified
- A product, character, or realistic prop hand-built from bare primitives (boxes, cylinders, torus shapes) in flat solid color under default lighting, when a free sourced model would do the job — see `references/asset-sourcing.md`

## 12. Confirm it, don't just assert it

A build isn't finished because it looks right in one static screenshot. Run `scripts/verify_scroll_page.mjs` (see `qa-verification.md`) to confirm there's no dead scroll, no reveal stuck below full visibility, that computed contrast passes at the actual frame text appears against, and that any scroll-scrubbed video actually advances. Then look at the contact sheet as a full strip — not just the top of the page.

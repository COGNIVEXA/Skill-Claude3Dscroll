---
name: claude3Dscroll
description: Skill for producing polished, scroll-driven, animated 3D websites by orchestrating Three.js, GSAP ScrollTrigger, React Three Fiber, Motion (Framer Motion), and React Spring together. Use it whenever a build needs more than one 3D/animation library at once, needs an opinionated architecture for wiring them together, or needs to actually look and feel premium rather than like a generic template. Fires on requests for 3D website builds, scroll-triggered storytelling, physics-driven motion, portfolio/agency/product pages with cinematic or interactive elements, or any task combining multiple rendering/animation libraries. Also fires on WebGL/GLSL shader work, camera-driven scroll experiences, virtual campus/school/university tours, 3D product showcases and configurators, architectural/real-estate walkthroughs, character animation (Mixamo, animated GLB/glTF, animation state machines), interactive 3D scenes with clickable hotspots, and requests to build, redesign, prototype, debug, or optimize any immersive/interactive 3D web experience — including plain-language asks like "3D website," "immersive website," "virtual tour," or "WebGL experience" with no library named explicitly.
---

# claude3Dscroll

Developed by **Cognivexa**.

A skill for developers, 3D engineers, and designers who need to ship scroll-driven, animated 3D websites that read as deliberately designed — not as a stock scroll-jack demo bolted onto default typography and a default palette. It bundles two things that too often get treated as separate jobs: **wiring** (getting Three.js, GSAP ScrollTrigger, React Three Fiber, Motion, and React Spring to cooperate without stepping on each other) and **taste** (a concrete visual/editorial bar the output has to clear).

Left unchecked, AI-generated "3D scroll site" output tends to land in one of two bad places: safe-but-forgettable, or flashy-but-sloppy (barely-readable text, a six-line headline on mobile, the same three-card layout as everyone else's output). This skill exists to keep a build out of both traps by treating interaction quality and design quality as one requirement, checked together.

## When this applies

Reach for it when the task involves:
- A website, landing page, or portfolio where scroll drives 3D motion
- Wiring together two or more of: Three.js, GSAP/ScrollTrigger, React Three Fiber, Motion, React Spring
- Camera choreography, pinned/staged sections, frame-scrubbed video, physics-flavored interaction, or particle/shader work tied to scroll or pointer input
- A brief along the lines of "make it feel premium / cinematic / high-end / not generic"
- Character/object animation (Mixamo, animated GLB/glTF, idle/walk/run/gesture state machines) or authored camera choreography (establishing shots, dolly/orbit/fly-through, room transitions)
- Custom GLSL/shader effects (fresnel, dissolve, portal, holographic, procedural surfaces) — or the judgment call on when a shader is actually justified over a standard material
- A specialized experience type — virtual campus/school/university tour, 3D product showcase/configurator, or architectural/real-estate walkthrough (see `references/experience-modes.md`)
- Making an existing or planned 3D build responsive across device tiers, accessible (`prefers-reduced-motion`, keyboard, screen readers), or debugging a specific symptom (black canvas, missing model, jittery camera, memory leak, etc.)

For a narrow single-library question ("what's the config shape for `useSpring`?") you don't need this skill — go straight to the library. This skill earns its keep on the *combination* and on the *craft bar*, not as a substitute for each library's own docs.

## How to work through a build

### 0. Match the effort to the ask — this is not optional
A build has to *finish* to be useful. Before doing anything else, decide which lane the request is in:
- **Quick/single-prompt ask** ("build me a 3D landing page for X") → lean pass: one grammar, one architecture, a short feeling arc (3–4 lines, not an essay), one signature interaction, one visual self-check in the browser. Skip the differentiation check (nothing to differentiate against yet on a first build) and treat automated verification (step 5) as optional.
- **Explicit "premium/agency-grade," multi-page, or "polish this until it's right" ask** → the full process below, including automated verification and, if applicable, the differentiation check.

Either way, keep these hard limits so a build can't run away:
- **Cap the fix → re-verify loop at 2 passes.** If issues remain after two rounds, report what's left instead of continuing indefinitely — a finished build with three documented rough edges beats an unfinished one still "improving."
- **Never block asset delivery on a slow one-time download.** `npx playwright install chromium` (step 5) downloads a browser binary and can take several minutes on a slow connection. Run it once, in the background if possible; if it's not already done by the time everything else is ready, ship the build with a visual self-check instead of waiting on it, and say so.
- **Don't re-run `npm install` or re-scaffold** once a project already exists — iterate on the existing files.
- If a build is taking noticeably longer than the scope of the ask justifies, stop, say what's done and what's left, and ask whether to keep going rather than silently continuing.

### 1. Scope it before writing code
Decide, or confirm with the requester if it's genuinely unclear:
- What is the visitor supposed to feel or do, and what's the single idea the page needs to land?
- Choose exactly one page structure/grammar from `references/design-craft.md` (cinematic single-take, chaptered narrative, live reactive surface, continuous 3D world, type-led poster, curated gallery, dual-pane stage, hard-cut sequence). These are mutually exclusive — committing to one rules out borrowing traits from another.
- Choose a library combination using `references/decision-matrix.md`.
- If the brief is a school/university campus tour, a product showcase/configurator, or an architectural/real-estate walkthrough, check `references/experience-modes.md` first — it lists the scenes, interactions, and planning tradeoffs specific to that project type before any generic architecture decision is made.

### 2. Scaffold a real project
Use `scripts/scaffold_project.py` to spin up a working Vite + React + React Three Fiber + GSAP + Motion + Zustand starter (mirrored in `assets/starter-unified/`). Build the actual site inside this rather than starting from an empty file.

```bash
python scripts/scaffold_project.py my-project --dir ./my-project --accent "#ff6b35"
cd my-project && npm install && npm run dev
```

### 3. Choose an integration architecture
Match the pattern in `references/architecture-patterns.md` to the grammar and stack from step 1:
- **Split-layer setup** (Three.js + GSAP + a React UI shell) — imperative render loop, scroll-driven camera/material values, HTML laid over the top. Suits cinematic single-takes and continuous-world pages.
- **All-React composition** (R3F + Motion) — declarative and state-first. Suits product viewers, galleries, dual-pane stages.
- **Blended timeline control** (R3F + GSAP timelines) — GSAP sequencing living inside an R3F component tree. Suits chaptered narratives and hard-cut sequences that need precise pacing.
- **Physics-flavored interaction** (R3F + React Spring) — spring-driven response for anything that should feel handled rather than merely animated. Suits pointer-reactive objects, drag, hover feedback, a bespoke signature interaction.

Cross-library recipes (scroll-tied cameras, gesture handling, state-synced animation) live in `references/integration-recipes.md`. Shared-state practice (Zustand as the single source of truth the 3D layer and the DOM layer both read) lives in `references/state-management.md`.

Whichever architecture is chosen, it's built on top of the same underlying layers, each with its own dedicated reference:
- **Core Three.js/R3F engineering** (component decomposition, `useFrame`/`useThree` discipline, loaders, Suspense, instancing/LOD, color management, SSR) — `references/threejs-r3f.md`.
- **The scroll-driver system itself** (picking one scroll source, GSAP/Lenis/`ScrollControls` wiring, normalized progress, damped camera interpolation, section-based timelines, pinned layouts, cross-scene transitions) — `references/scroll-animation.md`. This is the layer everything else in step 3 assumes is already solid.
- **Character/object animation playback and camera choreography** (Mixamo pipeline, `AnimationMixer`/`useAnimations`, animation state machines, the shot vocabulary for authored camera moves) — `references/animation-system.md`.

### 4. Hold it to the design bar
This step is not optional finishing polish — it's what separates a shippable site from a tech demo. Work through `references/design-craft.md` in full:
- Write a feeling arc before building a single section
- Commit to one deliberately engineered high point, not several competing ones
- Invent one signature interaction unique to this build
- Meet the type floor (two families at most, 45–75 character measure, tracking/line-height discipline, adjustments for light-on-dark)
- Apply the 4px spacing scale with real rhythm, not uniform padding everywhere
- Use six color roles plus a single accent, with light/dark handling documented explicitly
- Build depth from five different tools, not a single flat drop-shadow
- Run the output against the "don't ship this" list before calling it finished
- If this isn't the first build made with the skill, run it through the differentiation check so it doesn't converge on a prior build

**Source real assets — don't hand-build what a free professional asset already covers.** A product, character, or realistic prop assembled from bare Three.js primitives (`BoxGeometry`, `TorusGeometry`) under flat default lighting reads as a wireframe mockup, not an HD render, no matter how the scroll behaves. Follow `references/asset-sourcing.md` for where to pull free, commercial-use-safe 3D models, HDRI environment lighting, PBR textures, and stock video/footage, and for the renderer/post-processing baseline (real environment lighting, tone mapping, bloom) that makes even a simple scene read as premium rather than flat. For the deeper per-source licensing rules, red flags, and the `ASSET_LICENSES.md` manifest format — needed whenever a source beyond the always-safe CC0 defaults is used — see `references/asset-licensing.md`.

**Direct the 3D scene itself like a shot, not just the page around it.** `references/visual-design.md` covers composition, depth staging, light as the primary compositional tool, and camera-lens language specifically for the 3D content — narrower and more technical than `design-craft.md`'s page-level bar. Reach for custom GLSL (`references/shaders.md`) only when a standard material genuinely can't produce the effect — a dissolve/reveal transition, a portal/holographic look, animated vertex displacement; default to `MeshStandardMaterial`/`MeshPhysicalMaterial` plus real lighting otherwise.

### 5. Verify — bounded, not open-ended
Run `scripts/verify_scroll_page.mjs` against the dev server or a deployed URL (see step 0 for when this step is worth the time it costs). It drives a real headless browser through the entire scroll range and reports, per position:
- **Scroll that does nothing** — stretches where nothing observable changes as the visitor scrolls
- **Reveal elements that never fully appear** — content that fades in but never actually reaches full visibility
- **Contrast failures**, computed per line of text at the exact frame it's shown against, graded correctly whether the text sits on a light or dark ground
- **Frozen scroll-linked video** — a clip that silently never advances, indistinguishable at a glance from a stalled player

It produces a contact sheet (`qa-report/report.html`) so the entire scroll journey can be reviewed as a strip, plus `qa-report/report.json` for scripted checks. See `references/qa-verification.md` for how to interpret and respond to it. Fix, re-run, up to the 2-pass cap from step 0 — then report whatever's left rather than continuing to loop.

### 6. Pass on performance and correctness
Before calling anything finished, check `references/performance.md` (render-loop coordination, on-demand rendering, DPR ceilings, geometry/texture cleanup) and `references/pitfalls.md` (libraries stepping on the same property, React state drifting from the Three.js scene, leaked tweens/timers).

### 7. Harden for every device and visitor, diagnose systematically, do a final pass
This step covers the specialist ground beyond steps 4–6 — still governed by the same effort-matching rule from step 0 (a quick single-prompt build can take the lean versions of these; an explicit premium/agency-grade or "polish this" ask should work through all of them):
- **Responsive across device tiers** — `references/responsive-3d.md`: a low/medium/high tiering policy (DPR, shadows, postprocessing, particle count, texture resolution, LOD) applied in one place rather than scattered `if (isMobile)` checks, plus runtime adaptive quality via Drei's `PerformanceMonitor`, and a designed fallback for WebGL-unsupported devices.
- **Accessible by default** — `references/accessibility.md`: critical content must never live only inside the canvas, `prefers-reduced-motion` needs a genuinely different (not just shorter) experience, every 3D interaction needs a keyboard-reachable equivalent, and the `<canvas>` itself needs an `aria-label` or equivalent.
- **When something's actually broken, diagnose systematically** — `references/debugging.md`: symptom-first troubleshooting (black canvas, missing model, CORS, missing/misnamed animation clips, Mixamo-specific issues, scroll desync, camera snapping, SSR/hydration errors, WebGL context loss, shader compile errors, z-fighting, memory leaks) instead of guessing at fixes.
- **Audit asset weight before shipping** — `scripts/audit_assets.py` scans a project's asset folders for oversized GLB/glTF, texture, and video files against configurable size limits, and can emit a starter `ASSET_LICENSES.md` manifest (pairs with `references/asset-licensing.md`) and a JSON report for scripted checks:
  ```bash
  python scripts/audit_assets.py ./public --out audit-report.md --manifest ASSET_LICENSES.md
  ```
- **Final pre-ship pass** — `references/quality-checklist.md` consolidates all of the above plus the design bar and the automated scroll-verification report into one checklist across Visual/Performance/Interaction/Accessibility/Engineering/Licensing, so a last pass has one place to work through instead of re-deriving "done" from memory.

## What's bundled with this skill

```
claude3Dscroll/
├── SKILL.md                        this file
├── references/
│   ├── architecture-patterns.md    the four integration architectures, with code
│   ├── integration-recipes.md      scroll cameras, gesture handling, state sync
│   ├── state-management.md         Zustand as the shared 3D/DOM state layer
│   ├── performance.md              render-loop discipline, disposal, budgets
│   ├── pitfalls.md                 recurring mistakes and how to avoid them
│   ├── decision-matrix.md          which combination fits which use case
│   ├── design-craft.md             the design bar — grammar, type, color, depth,
│   │                                the "don't ship this" list, differentiation check
│   ├── qa-verification.md          reading and acting on the verification report
│   ├── asset-sourcing.md           free, commercial-use 3D models, HDRIs, textures,
│   │                                and video — plus the renderer/post-processing
│   │                                baseline that keeps a scene from looking flat
│   ├── threejs-r3f.md              core Three.js/R3F engineering: components,
│   │                                useFrame/useThree, loaders, Suspense, SSR
│   ├── scroll-animation.md         the scroll-driver system itself — one scroll
│   │                                source, damped camera, section timelines
│   ├── animation-system.md         Mixamo/character animation, state machines,
│   │                                camera choreography shot vocabulary
│   ├── asset-licensing.md          deep per-source licensing rules, red flags,
│   │                                the ASSET_LICENSES.md manifest format
│   ├── shaders.md                  when GLSL is justified, and effect recipes
│   │                                (fresnel, dissolve, portal, transition masks)
│   ├── responsive-3d.md            device-tier policy, adaptive quality, WebGL
│   │                                fallback
│   ├── accessibility.md            reduced motion, keyboard, semantic HTML,
│   │                                canvas ARIA, contrast
│   ├── visual-design.md            directing the 3D scene itself as a shot —
│   │                                composition, light, camera-lens language
│   ├── debugging.md                systematic symptom-first troubleshooting
│   ├── quality-checklist.md        the consolidated pre-ship checklist
│   └── experience-modes.md         campus/school tours, product showcases,
│                                    architectural walkthroughs — scenes and
│                                    interactions specific to each
├── scripts/
│   ├── scaffold_project.py         generates a working starter project
│   ├── verify_scroll_page.mjs      headless-browser scroll verification (Playwright)
│   └── audit_assets.py             scans model/texture/video sizes, flags
│                                    oversized files, can emit a starter
│                                    ASSET_LICENSES.md manifest
└── assets/
    └── starter-unified/            a checked-in copy of what the scaffold produces
```

## Where this skill stops

This skill covers combining libraries and holding the result to a design bar — it isn't a substitute for each library's own reference docs. For low-level API detail (Three.js scene/camera/renderer setup, GSAP/ScrollTrigger timeline syntax, R3F's `useFrame`/`useThree` and Drei helpers, Motion's gesture/layout props, React Spring's `config` presets), consult the library directly. This skill's job is telling you how they fit together and what "actually good" looks like once they do.

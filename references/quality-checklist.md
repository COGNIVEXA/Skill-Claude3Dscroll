# Pre-Ship Quality Checklist

The single consolidated checklist to run before calling a build finished. It doesn't replace the deeper references — each item links to where the full detail and fixes live — it exists so a final pass has one place to work through rather than re-deriving what "done" means from memory. Pair with the automated report from `qa-verification.md`, which mechanically checks a subset of the items below; this checklist covers what that script can't measure (licensing, taste, architecture) as well as what it can.

## Visual

- [ ] Camera paths are smooth and damped, not snapped between keyframes (`scroll-animation.md`, `animation-system.md`)
- [ ] Every keyframe on every authored camera path is checked for geometry clipping, not just start/end (`animation-system.md`)
- [ ] Composition holds at the major breakpoints tested (desktop, tablet, mobile) — not just designed once at desktop and assumed to translate (`responsive-3d.md`)
- [ ] Models are at correct real-world-relative scale and pivot origin — nothing floating, sinking through the floor, or absurdly over/undersized next to what it's placed beside
- [ ] Lighting reads as intentional — real HDRI/environment lighting, not flat ambient + one directional (`asset-sourcing.md`, `visual-design.md`)
- [ ] Animation blends smoothly between states (Idle/Walk/Run, section-to-section) with no pop or T-pose flash (`animation-system.md`)
- [ ] One clear focal point per key frame; light and depth staging support it (`visual-design.md`)

## Performance

- [ ] No unnecessarily large textures — resolution matched to on-screen size, compressed formats used where the pipeline supports them (`performance.md`, `responsive-3d.md`)
- [ ] Draw calls and triangle count checked against `renderer.info`, not assumed (`performance.md`, `debugging.md`)
- [ ] GLBs compressed (Draco/Meshopt) where the pipeline supports it; oversized source files not shipped as-is
- [ ] `dpr` capped, not left at raw `devicePixelRatio` (`performance.md`)
- [ ] Repeated geometry instanced rather than duplicated as individual meshes (`performance.md`, `threejs-r3f.md`)
- [ ] Device-tiered quality actually implemented and tested on a throttled/mobile profile, not just written and assumed to work (`responsive-3d.md`)
- [ ] `scripts/audit_assets.py` run and any flagged oversized files addressed or consciously accepted with a documented reason

## Interaction

- [ ] Hotspots/clickable elements work as expected and give feedback on hover/focus, not just on successful click
- [ ] Scroll interactions don't conflict — confirmed one scroll driver, no dead ranges outside the expected top/bottom edges (`scroll-animation.md`, `qa-verification.md`)
- [ ] Core navigation remains usable throughout the scroll journey, not just at the top of the page
- [ ] Loading state reflects real progress (or at minimum a designed placeholder), not a blank canvas or an indefinite spinner (`threejs-r3f.md`'s Suspense section)
- [ ] Errors have a fallback — a failed model/texture load degrades to something visible and reasonable rather than a blank hole in the scene or an unhandled promise rejection

## Accessibility

- [ ] Every critical message/action reachable with WebGL disabled (`accessibility.md`)
- [ ] `prefers-reduced-motion` produces a genuinely different, calmer experience, not just shorter durations (`accessibility.md`, `scroll-animation.md`)
- [ ] Every interactive 3D element reachable and operable by keyboard (`accessibility.md`)
- [ ] Semantic HTML underneath the canvas — real headings, real `<nav>`/`<button>`/`<a>`, not styled `div`s (`accessibility.md`)
- [ ] Text passes contrast at the actual frame/background it's shown against (`accessibility.md`, `qa-verification.md`)
- [ ] `<canvas>` carries an `aria-label` or is `aria-hidden` with equivalent content available elsewhere

## Engineering

- [ ] No unexplained console warnings/errors on load or during a full scroll pass
- [ ] No memory leak across an extended session — `renderer.info.memory` checked over time, not just at load (`performance.md`, `debugging.md`)
- [ ] Components are reasonably decomposed — no single file owning loading + animation + scroll response + UI for an entire section (`threejs-r3f.md`)
- [ ] Types correct throughout (if the project is TypeScript) — no `any` papering over an actual mismatch
- [ ] Production build succeeds cleanly (`npm run build`), not just the dev server
- [ ] SSR/hydration boundary confirmed correct if the framework server-renders (`threejs-r3f.md`, `debugging.md`)
- [ ] All manually created Three.js resources disposed on unmount; all GSAP tweens/`ScrollTrigger`s killed on unmount/route change (`performance.md`, `pitfalls.md`)

## Licensing

- [ ] Every external asset's license confirmed and recorded in `ASSET_LICENSES.md`, not assumed (`asset-licensing.md`)
- [ ] Any CC-BY asset's required attribution actually present somewhere on the shipped site
- [ ] No asset carrying "personal use only" / "non-commercial" terms present in a commercial build
- [ ] Mixamo/other platform-specific terms confirmed current at time of ship, not assumed unchanged from when the asset was first sourced

## Design bar (cross-reference, not duplicated here)

Everything in `design-craft.md`'s own checklist — page grammar committed to, a signature interaction present, the type/spacing/color/depth floors met, the "don't ship this" list clear, the differentiation check run if this isn't the first build. This checklist assumes that pass has already happened; it isn't a substitute for it.

## How to use this list

Work through it top to bottom once the build is functionally complete. Anything unchecked is either a fix-before-ship item or a consciously accepted, documented tradeoff (a specific device tier that's out of scope for this engagement, a licensing question referred back to the requester) — never a silently skipped item. Cap fix/re-check cycles the same way `SKILL.md` step 0 caps the verification loop: report what's left rather than looping indefinitely chasing a perfect score.

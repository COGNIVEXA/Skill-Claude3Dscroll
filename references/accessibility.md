# Accessibility

An immersive 3D scroll experience and an accessible one aren't in tension — most of what this file asks for is structural (semantic HTML underneath the canvas, a reduced-motion path, keyboard reachability) rather than a compromise on the visual experience itself. Treat this as a requirement to design for from Phase 1, not a pass applied at the end.

## The rule that matters most: WebGL is never the only source of critical content

If a visitor with WebGL disabled, a screen reader, or `prefers-reduced-motion` set never sees the canvas render (or sees a simplified version), they still need to reach: the core message/value proposition, navigation, contact/conversion actions, and any information the page exists to deliver (course listings on a university site, product specs on a showcase page, pricing on an agency site). Structure content so an HTML layer carries this regardless of what the 3D layer is doing — the 3D layer enhances, it doesn't gate.

```jsx
// Wrong — the heading only exists inside a WebGL-rendered texture/geometry
<Canvas><Scene><Text3D>Welcome to Riverside Academy</Text3D></Scene></Canvas>

// Right — real HTML carries the content; 3D provides the staged/animated backdrop
<Canvas><Scene /></Canvas>
<h1 className="hero-heading">Welcome to Riverside Academy</h1>
```

## `prefers-reduced-motion`

Detect once, expose it through the same store everything else reads from:
```js
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
useSceneStore.setState({ reducedMotion: prefersReducedMotion })
```
Respond to it structurally, not by just shortening every duration by half:
- Scroll-scrubbed camera moves (`scroll-animation.md`, `animation-system.md`) → replace with simple section-to-section fades or hard cuts; skip the fly-through/dolly/orbit shots entirely.
- Auto-playing looping animation (idle character motion, ambient particles) → keep, but drop anything with large-amplitude or fast motion (parallax drift, autoplaying camera pans).
- GSAP timelines → gate the scrub/pin behavior:
```js
gsap.timeline({
  scrollTrigger: {
    trigger: section,
    scrub: reducedMotion ? false : 1,
    pin: !reducedMotion,
  },
})
```
- Respect it live, not just at load — a visitor can toggle the OS setting mid-session on some platforms; listen for the `change` event on the media query rather than reading it once at boot only, when the build's complexity justifies it (a quick/lean build reading it once at load is an acceptable simplification — see `SKILL.md` step 0).

## Semantic HTML and structure

- Real heading hierarchy (`h1`–`h6`) in the HTML overlay, not styled `div`s standing in for headings.
- Real `<nav>`, `<button>`, `<a>` elements for anything interactive, even where they're styled to sit over or near the 3D layer.
- `<canvas>` itself should carry `aria-label` or be marked `aria-hidden="true"` with the equivalent content available elsewhere in the DOM — a bare unlabeled canvas is announced to screen readers as an unexplained graphic with no description of what it represents.
```jsx
<Canvas aria-label="Interactive 3D tour of the campus — navigation and content are also available below">
```

## Keyboard reachability

Any interaction that's mouse/touch-only in the 3D layer (a clickable hotspot, a draggable object, an orbit control) needs a keyboard-reachable equivalent:
```jsx
<Hotspot position={[1, 0.5, -2]} label="Science Lab" onSelect={() => setActiveRoom('lab')} />
// rendered via drei's <Html>, backed by a real focusable button, not a bare mesh click handler:
<Html position={[1, 0.5, -2]}>
  <button className="hotspot" onClick={() => setActiveRoom('lab')} aria-label="View the Science Lab">
    <span className="hotspot-dot" />
  </button>
</Html>
```
A mesh's `onClick` (`onPointerDown` under the hood) has no keyboard equivalent by default — if a hotspot's real interactive control is an HTML `<button>` rendered via `<Html>`, it inherits keyboard focus/activation for free. If a control must be a bare 3D object with no HTML counterpart, add a parallel keyboard-operable HTML list of the same hotspots (can be visually hidden until focused) so the interaction isn't mouse-only.

## Visible focus

Don't suppress `:focus` outlines on interactive elements layered over the 3D scene for aesthetic reasons — restyle them to fit the visual language instead of removing them:
```css
.hotspot:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 4px;
}
```

## Contrast

Covered mechanically by `qa-verification.md`'s automated per-frame contrast check for text over animated/video backgrounds. The general rule underneath it: 4.5:1 for normal text, 3:1 for large text (≥24px, or ≥19px bold), checked against the actual background at the moment the text is visible — not just against a static mockup.

## Alternate interaction paths

For an experience whose primary interaction is inherently spatial (drag to orbit, scroll to fly through), provide a non-spatial equivalent for reaching the same content — a simple in-page jump-link list of chapters/rooms, a "skip to content" link that bypasses the hero 3D sequence entirely, or a text-based site map for a virtual tour. This also directly helps the reduced-motion and keyboard cases above rather than being a separate concern.

## Fallback when WebGL is unavailable

Covered in implementation detail in `responsive-3d.md` — the accessibility requirement on top of that mechanical fallback: the fallback needs to be a genuinely designed alternative (a static hero image/video, real copy, real navigation) that delivers the same message and lets the visitor complete the same tasks, not an apologetic "please switch browsers" notice with the rest of the page missing.

## Quick self-check

- Can every critical message/action on the page be reached with WebGL disabled?
- Does the page behave meaningfully differently (not just "shorter") under `prefers-reduced-motion`?
- Can every interactive 3D element be reached and activated by keyboard alone?
- Does focus remain visible and in a sensible order as sections pin/unpin during scroll?
- Does text pass contrast at the actual frame/background it's shown against, not just in isolation?
- Does the `<canvas>` carry an `aria-label`, or is it hidden with equivalent content available elsewhere?

If any of these is "no," treat it as a defect, not a nice-to-have — fold it into `quality-checklist.md`'s pre-ship pass.

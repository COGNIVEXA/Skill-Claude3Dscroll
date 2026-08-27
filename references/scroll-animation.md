# The Scroll Animation System

Scroll is the spine of this entire class of site — get this layer wrong and nothing built on top of it (camera choreography, section transitions, reveals) can be fixed independently. `integration-recipes.md` §1 has a working camera-tied-to-scroll snippet; this file covers the system around it — how to structure scroll state so every layer (camera, materials, UI, scene transitions) reads from one place instead of each wiring its own scroll listener.

## The core rule: one scroll source, many readers

Every symptom in `pitfalls.md` #1, #2, #4, and #7 traces back to the same root cause — more than one piece of code independently deciding what "scroll position" means right now. Fix it structurally:

```
scroll input (wheel/touch, or Lenis smoothing it)
        │
        ▼
one driver (ScrollTrigger, or a Zustand store fed by a single onScroll)
        │
        ├──► camera (CameraRig reads it in useFrame)
        ├──► material/uniform values
        ├──► HTML overlay animations (via the same GSAP timeline, or Motion reading the store)
        └──► scene/section transitions
```

Nothing downstream should attach its own scroll listener. Everything downstream reads a value (a GSAP timeline's progress, or a store field) that the one driver owns.

## Pick a scroll driver

| Driver | When |
|---|---|
| Native scroll + GSAP `ScrollTrigger` | Default choice. Section-based, pinning, scrubbing — most cinematic/chaptered/hard-cut pages. |
| Lenis + `ScrollTrigger` | Add when the brief explicitly wants smoothed/eased scroll feel. Lenis intercepts native scroll and re-dispatches a virtual scroll `ScrollTrigger` reads — don't let both native scroll and Lenis drive different consumers at once. |
| Drei `ScrollControls` + `useScroll` | When the entire experience lives inside the `<Canvas>` and there's little/no independent HTML layer to keep in sync — R3F owns scroll natively, no DOM scroll listener needed at all. |
| Raw `onScroll` → Zustand | Only when neither of the above fits (a fully custom scroll-jack, or scroll driving non-GSAP, non-R3F consumers). More wiring, more to get wrong — prefer `ScrollTrigger` unless there's a specific reason not to. |

Don't run two of these at once (e.g. Lenis *and* `ScrollControls`, or native `ScrollTrigger` *and* a hand-rolled `onScroll` store) — pick one per page.

## Lenis + ScrollTrigger wiring

```js
import Lenis from 'lenis'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)

const lenis = new Lenis({ duration: 1.1, easing: (t) => 1 - Math.pow(1 - t, 3) })

lenis.on('scroll', ScrollTrigger.update)          // tell ScrollTrigger about Lenis's virtual scroll
gsap.ticker.add((time) => lenis.raf(time * 1000)) // drive Lenis from GSAP's own ticker, not a second rAF loop
gsap.ticker.lagSmoothing(0)                        // Lenis already smooths; don't double-smooth
```
Driving Lenis from `gsap.ticker` instead of its own `requestAnimationFrame` loop keeps GSAP and Lenis on the exact same clock — a second independent rAF loop is a common, hard-to-spot source of one-frame lag between scroll-smoothing and scroll-triggered animation.

## Section-based timelines, not one giant timeline

Give each page section its own `ScrollTrigger`-scoped timeline rather than one monolithic timeline for the whole page. Easier to reason about, easier to re-time one section without touching the rest, and failures stay isolated:

```jsx
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.timeline({
      scrollTrigger: {
        trigger: '#chapter-2',
        start: 'top top',
        end: '+=150%',
        scrub: 1,
        pin: true,
      },
    })
      .to(cameraTarget, { x: 4, z: -2 }, 0)
      .to('.chapter-2-copy', { opacity: 1, y: 0 }, 0.1)
      .to(materialUniform, { value: 1 }, 0.3)
  }, containerRef)
  return () => ctx.revert()
}, [])
```
`scrub: 1` (a number, not `true`) adds a small catch-up delay that reads as smoothed rather than instantly velocity-locked to the scrollbar — usually the better feel for camera/material moves; `scrub: true` for anything that should track the scrollbar exactly (a progress bar, a 1:1 drag-like reveal).

## Normalized progress instead of raw scroll pixels

Never let a consumer read `window.scrollY` directly — pixel values break the moment content height changes (responsive breakpoint, a late-loading image, copy edits). Read progress (0–1) from the trigger instead:
```js
scrollTrigger: {
  trigger: '#chapter-2',
  start: 'top top',
  end: '+=150%',
  onUpdate: (self) => {
    cameraStore.getState().setChapterProgress(self.progress)   // 0 → 1, resolution-independent
  },
}
```
Every downstream consumer (camera interpolation, a shader uniform, an HTML progress indicator) reads this normalized value, not pixels.

## Damped camera movement

Don't set camera transforms directly from scroll progress — jump-cuts between sampled positions read as jittery even when the underlying progress value is smooth. Interpolate toward a target every frame instead:
```jsx
useFrame((_, delta) => {
  camera.position.lerp(targetPosition.current, 1 - Math.pow(0.001, delta))
  camera.quaternion.slerp(targetQuaternion.current, 1 - Math.pow(0.0005, delta))
})
```
The `1 - Math.pow(k, delta)` form gives frame-rate-independent damping — a fixed `lerp(pos, 0.05)` per frame moves at different effective speeds on a 30fps device vs a 144Hz display. See `debugging.md` for what camera snapping (the ungapped version of this) looks like when this step is skipped.

## Sticky/pinned Canvas layout

The most common structural pattern for a scroll-driven 3D page: one `position: fixed` (or GSAP-pinned) full-viewport `<Canvas>` sitting behind normal-flow HTML sections that scroll over it.
```css
.canvas-layer { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.canvas-layer.interactive { pointer-events: auto; }  /* enable only where the 3D scene needs pointer events */
main { position: relative; z-index: 1; }
```
The HTML sections provide the actual scroll height; the canvas never scrolls itself, it just re-renders in response to the scroll-derived progress value. `pointer-events: none` by default keeps text selection and links in the HTML overlay working — turn it on only for the specific region where a hotspot or drag interaction needs it.

## Cross-scene / chapter transitions

For a hard-cut or chaptered page changing which 3D content is visible between sections, cross-fade rather than swap instantly — an instant `visible` toggle reads as a broken load, not an intentional cut:
```jsx
useFrame(() => {
  sceneAOpacity.current = THREE.MathUtils.lerp(sceneAOpacity.current, targetA, 0.08)
  materialA.opacity = sceneAOpacity.current
})
```
Or drive it with a shader-based reveal/dissolve (see `shaders.md`) for a more deliberate transition than a plain opacity cross-fade.

## Reduced motion

A scroll-driven page is exactly the kind of build `prefers-reduced-motion` exists for. See `accessibility.md` for the full pattern — the short version: detect it once, and either disable `scrub`/pin-driven camera movement in favor of simple section-by-section fades, or cut animation duration/distance substantially. Decide this during Phase 3, not as an afterthought.

## What to avoid (cross-referenced from `pitfalls.md`)

- Two scroll systems running at once (native `ScrollTrigger` + `ScrollControls`, or Lenis + a second hand-rolled `onScroll`) — pick one driver, above.
- Reading `window.scrollY` in more than one place — normalize once, read progress everywhere else.
- `setState` inside a scroll/`useFrame` callback at scroll frequency — write to refs/uniforms, throttle any React-facing state update.
- A pinned section whose height changes after layout settles — call `ScrollTrigger.refresh()` after fonts/images finish loading (`pitfalls.md` #5).
- `frameloop="demand"` without `invalidate()` wired into the scroll driver's update callback (`pitfalls.md` #7) — the canvas will silently stop repainting mid-scrub.

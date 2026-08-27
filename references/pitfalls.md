# Recurring Mistakes

## 1. Two libraries competing for the same property

```jsx
// Wrong: GSAP and React Spring both animate position
gsap.to(meshRef.current.position, { x: 5 })
api.start({ position: [10, 0, 0] }) // whichever writes last wins — flickers every re-render
```

Fix: give each animatable property exactly one owner.
```jsx
gsap.to(meshRef.current.position, { x: 5 })  // GSAP owns position
api.start({ scale: 1.5 })                     // Spring owns scale
```

## 2. React's picture of the world drifting from the Three.js scene

```jsx
// Wrong: mutated directly, React never finds out
mesh.position.x = 5
```

Fix: update both, or route the write through the store so React reads the same source of truth.
```jsx
const updatePosition = (x) => {
  mesh.position.x = x
  setPosition(x) // or useSceneStore.getState().updateCamera(...)
}
```

## 3. Leaked animations

```jsx
// Wrong: no cleanup — keeps running against a mesh that no longer exists once unmounted
useEffect(() => {
  gsap.to(meshRef.current.rotation, { y: Math.PI * 2, repeat: -1 })
}, [])
```

Fix:
```jsx
useEffect(() => {
  const tween = gsap.to(meshRef.current.rotation, { y: Math.PI * 2, repeat: -1 })
  return () => tween.kill()
}, [])
```
The same discipline applies to `ScrollTrigger` instances (`.kill()`, or `ScrollTrigger.getAll().forEach(t => t.kill())` on route change in a single-page app) and to any manually started `requestAnimationFrame` loop.

## 4. ScrollTrigger duplicating under React StrictMode
StrictMode mounts and unmounts effects twice in development, which can leave duplicate ScrollTriggers behind if cleanup isn't correct. Scope creation with `gsap.context()` and revert it on cleanup so a double-mount doesn't leave two triggers pinning the same section.
```jsx
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.to('.box', { x: 100, scrollTrigger: '.box' })
  }, containerRef)
  return () => ctx.revert()
}, [])
```

## 5. Pinned sections shifting after layout settles
A `pin: true` section that changes height after it's already pinned — late-loading images, a web font swapping in — throws off every trigger that comes after it. Call `ScrollTrigger.refresh()` once fonts/images have finished loading, and reserve layout space (explicit dimensions or aspect-ratio boxes) ahead of anything that gets pinned.

## 6. `lookAt` fighting `OrbitControls`
If `OrbitControls` is active while something else also calls `camera.lookAt()` every frame, the two fight each other — the camera jitters or snaps. Either disable `controls.enabled` during a scripted camera move, or skip `OrbitControls` entirely on pages where the camera path is fully authored (most cinematic and continuous-world pages don't need free orbiting from the visitor).

## 7. A `frameloop="demand"` scene that looks frozen
Switching R3F to `frameloop="demand"` without calling `invalidate()` from the GSAP/scroll handlers means the canvas only repaints on pointer events — scroll-driven changes silently stop rendering. This is one of the most common reports of "the scene isn't updating with scroll."

## 8. A scroll-scrubbed video that never actually scrubs
Setting `video.currentTime` on every scroll tick without confirming the browser has buffered enough or emitted `seeked` can silently no-op, leaving the video paused on its first frame while the rest of the page animates around it. `scripts/verify_scroll_page.mjs` checks specifically for a video whose `currentTime` never changes across a full scroll pass.

## 9. No plan for low-power devices
A build that assumes desktop-class GPU power will drop frames or show a blank canvas on mobile Safari. Decide up front what degrades gracefully: fewer particles, `antialias` off, a capped `dpr`, or a static/video fallback for the heaviest 3D section. Settle this before calling the build finished, not after someone reports it.

# Performance

A scroll-driven 3D page succeeds or fails on frame time. Work through these roughly in order.

## 1. Put a ceiling on pixel ratio
Rendering at the browser's raw `devicePixelRatio` on a high-DPI display quietly multiplies the pixel count by up to 4x relative to a standard display. Cap it.
```javascript
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
```
```jsx
<Canvas dpr={[1, 2]} />
```

## 2. Only render when something changed
If the 3D content is mostly static and only reacts to scroll or interaction, a free-running `requestAnimationFrame` loop is wasted work.
```jsx
<Canvas frameloop="demand" dpr={[1, 2]}>
  <Scene />
</Canvas>
```
```jsx
function Scene() {
  const invalidate = useThree((s) => s.invalidate)
  const handleClick = () => { /* update state */ invalidate() }
  return <mesh onClick={handleClick}>...</mesh>
}
```
Any GSAP/ScrollTrigger callback or pointer-move handler that should animate the scene needs to call `invalidate()` on every relevant tick, or demand mode will simply stop repainting mid-scrub.

## 3. Coordinate the render loop when Three.js is imperative and GSAP drives it
```javascript
import { Clock } from 'three'
const clock = new Clock()
let needsRender = true

function animate() {
  requestAnimationFrame(animate)
  if (needsRender || controls.enabled) {
    controls.update()
    renderer.render(scene, camera)
    needsRender = false
  }
}

ScrollTrigger.addEventListener('update', () => { needsRender = true })
```

## 4. Dispose of everything created by hand
Geometries, materials, and textures are not reclaimed just because a component unmounts — WebGL resources need explicit disposal.
```javascript
useEffect(() => {
  const geometry = new THREE.BoxGeometry()
  const material = new THREE.MeshStandardMaterial()
  return () => { geometry.dispose(); material.dispose() }
}, [])
```
Drei's loader hooks (`useGLTF`, `useTexture`) manage their own caching and cleanup in most cases, but anything built by hand still needs manual disposal.

## 5. Instance repeated geometry instead of duplicating meshes
A particle field, a grid of repeated objects, or scattered foliage should use `InstancedMesh` (Three.js) or Drei's `<Instances>`/`<Instance>` rather than one mesh object per instance. Hundreds of individually drawn meshes will cost frame time that a single instanced draw call absorbs for free.

## 6. Budget textures and geometry for a scroll-heavy build
- Prefer compressed textures (KTX2/Basis where the pipeline supports them) over full-resolution raw PNG/JPG fed straight into a WebGL texture.
- Scale polycount to how much screen space an object actually occupies — a hero object filling the viewport can justify more detail than something in the background.
- For frame-scrubbed video sections, keep resolution/bitrate low enough that seeking on every scroll tick doesn't stall the decoder — `qa-verification.md` covers how the verification script catches a clip that silently never decodes past its first frame.

## 7. Profile before optimizing further
Use the browser's performance profiler and `renderer.info` (`renderer.info.render.calls`, `.triangles`) to confirm where time is actually going before restructuring a scene. Don't reach for instancing or LOD on a scene that's already holding 60fps.

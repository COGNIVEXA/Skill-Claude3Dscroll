# Three.js / React Three Fiber Engineering

This is the core-engineering reference — how a scene, its loaders, and its render loop are actually built. `architecture-patterns.md` covers how Three.js/R3F combine with GSAP/Motion/Spring; this file covers the R3F/Three.js layer itself, in isolation.

## Component decomposition

Never put an entire experience in one component. A workable minimum split:

```
<Experience />        top-level Canvas wrapper + Suspense + providers
  <CameraRig />        owns the camera, exposes an imperative API for scroll/GSAP to drive
  <Lighting />          all lights + Environment in one place, tunable independent of geometry
  <Scene />             groups the actual content components below
    <Model />           a single static glTF load
    <AnimatedModel />   glTF + AnimationMixer, see animation-system.md
    <Hotspot />          a clickable/hoverable marker, positioned in 3D, rendered as HTML via <Html> or a billboard mesh
  <Effects />           <EffectComposer> and its passes, isolated so they can be toggled per device tier
  <PerformanceMonitor /> drei's adaptive-quality wrapper, see responsive-3d.md
```

Each component owns one responsibility. A component that both loads a model, drives its animation, and reacts to scroll is a sign to split it.

## `useFrame` discipline

`useFrame` runs on every rendered frame — code here is the highest-frequency code in the app.

**Do:**
```jsx
function Spinner() {
  const ref = useRef()
  useFrame((state, delta) => {
    ref.current.rotation.y += delta * 0.5   // delta-based, frame-rate independent
  })
  return <mesh ref={ref}>...</mesh>
}
```

**Don't:**
```jsx
function Spinner() {
  const [rotation, setRotation] = useState(0)
  useFrame(() => {
    setRotation((r) => r + 0.01)            // triggers a React re-render every frame
  })
  return <mesh rotation={[0, rotation, 0]}>...</mesh>
}
```
Mutate refs directly inside `useFrame`; never call `setState` there unless the state genuinely needs to drive React-rendered UI (a percentage readout, a label) and even then, throttle it (update every N frames, or only past a delta threshold) rather than writing on every tick.

Don't allocate inside `useFrame` either — a `new THREE.Vector3()` created every frame is garbage-collector pressure for no reason:
```jsx
const tmp = useMemo(() => new THREE.Vector3(), [])   // create once
useFrame(() => {
  tmp.set(x, y, z).applyMatrix4(someMatrix)           // reuse every frame
})
```

## `useThree` and camera access

```jsx
const { camera, gl, size, viewport, invalidate } = useThree()
```
Pull `invalidate` in anything that mutates the scene under `frameloop="demand"` (see `performance.md`). Read `size`/`viewport` for responsive layout math instead of `window.innerWidth` — it stays in sync with the actual canvas/DPR, `window` doesn't.

## Loading models

Prefer Drei's `useGLTF` over manually instantiating `GLTFLoader`:
```jsx
import { useGLTF } from '@react-three/drei'

function Product() {
  const { scene, nodes, materials, animations } = useGLTF('/models/product.glb')
  return <primitive object={scene} />
}
useGLTF.preload('/models/product.glb')   // start the fetch before the component mounts
```
For anything beyond `<primitive object={scene} />` — swapping materials, reading named nodes, driving named animation clips — generate a typed component with `gltfjsx` rather than hand-writing node traversal:
```bash
npx gltfjsx public/models/product.glb -o src/components/Product.jsx -T -r public
```
`-T` transforms the file (applies `SkeletonUtils.clone` where needed for reused skinned meshes) and emits `useGLTF.preload`; `-r public` rewrites the asset path relative to the public root. Treat the generated file as a starting point to edit, not a black box — it names every node/material so a section only needs to reference the parts it actually uses.

**Reused models**: if the same glTF scene is instanced more than once (a forest of the same tree, a shelf of the same product), clone with `SkeletonUtils.clone` for skinned/animated meshes or Drei's `<Merged>`/`<Instances>` for static repeats — never load the same URL through `useGLTF` in a loop expecting independent instances; the loader caches by URL and hands back the same object graph.

## Suspense boundaries

Every async loader (`useGLTF`, `useTexture`, `useFBX`) suspends. Wrap loading sections in `Suspense` with a purpose-built fallback, and keep the boundary as close to the loading component as the design allows — one `Suspense` around the entire `<Canvas>` means the whole page waits on the slowest asset instead of revealing progressively:
```jsx
<Canvas>
  <Suspense fallback={<LoadingPlaceholder />}>
    <Hero />
  </Suspense>
  <Suspense fallback={null}>
    <BelowFoldModel />
  </Suspense>
</Canvas>
```
Pair with Drei's `<Html>`-based loader or `useProgress` for an HTML-side loading screen that reads real fetch progress rather than a fake timer.

## Color management and tone mapping

React Three Fiber sets sane sRGB output color space and ACES tone mapping by default in current versions — confirm this in `onCreated` rather than assuming, especially if the renderer was constructed manually or the Canvas config is inherited from an older template:
```jsx
<Canvas
  onCreated={({ gl }) => {
    gl.toneMapping = THREE.ACESFilmicToneMapping
    gl.toneMappingExposure = 1.1
    gl.outputColorSpace = THREE.SRGBColorSpace
  }}
/>
```
Textures that carry color data (albedo/base color maps) need `texture.colorSpace = THREE.SRGBColorSpace`; data textures (normal, roughness, metalness, AO) must stay linear — setting sRGB on a normal map visibly wrecks it. `useTexture` and `useGLTF` set this correctly for standard glTF material slots automatically; only hand-loaded textures need the explicit set.

## Resize and DPR

```jsx
<Canvas dpr={[1, 2]} resize={{ scroll: false, debounce: { scroll: 50, resize: 0 } }}>
```
`resize.scroll: false` stops the canvas from re-measuring on every scroll event, which is wasted work on a scroll-driven page and can itself cause jitter. Cap `dpr` per `performance.md` and `responsive-3d.md` rather than trusting the raw device value.

## SSR / Next.js

`Canvas` and anything touching `window`/WebGL must not render on the server:
```jsx
'use client'
import dynamic from 'next/dynamic'
const Experience = dynamic(() => import('./Experience'), { ssr: false })
```
Keep this boundary at the top of the 3D subtree, not scattered per-component — one dynamic import for the whole `<Experience />`, not one per mesh. Anything that must be server-rendered for SEO (headings, copy, nav) belongs in ordinary HTML outside this boundary; see `accessibility.md` for why critical content should never live only inside the canvas regardless of SSR.

## Useful Drei helpers, by job

| Need | Helper |
|---|---|
| Load a glTF | `useGLTF` |
| Load a texture | `useTexture` |
| Environment lighting / reflections | `Environment` |
| Contact/soft shadow under an object without full shadow maps | `ContactShadows`, `AccumulativeShadows` + `RandomizedLight` |
| Orbit camera for dev/debug or a genuinely free-look scene | `OrbitControls` (see `pitfalls.md` #6 before combining with a scripted camera) |
| HTML content anchored to a 3D point (hotspots, labels) | `Html` |
| Repeated static geometry | `Instances` / `Instance`, or raw `InstancedMesh` |
| Skinned-mesh animation playback | `useAnimations` (see `animation-system.md`) |
| Scroll-linked pages inside the canvas itself | `ScrollControls` + `useScroll` (an alternative to a DOM-driven GSAP/Lenis scroll — see `scroll-animation.md`) |
| Adaptive quality by measured frame time | `PerformanceMonitor`, `AdaptiveDpr`, `AdaptiveEvents` |
| Debug camera/scene inspection during development | `Stats`, `Perf` (`r3f-perf`) |

Reach for a Drei helper before hand-rolling the equivalent — it's already handled the edge cases (disposal, SSR safety, memoization) that a first-pass custom version usually misses.

## Instancing and LOD, implemented

```jsx
import { Instances, Instance } from '@react-three/drei'

function Forest({ positions }) {
  return (
    <Instances limit={positions.length} range={positions.length}>
      <coneGeometry args={[1, 2, 8]} />
      <meshStandardMaterial color="#2d5a3d" />
      {positions.map((p, i) => (
        <Instance key={i} position={p} />
      ))}
    </Instances>
  )
}
```
For distance-based detail reduction, Three.js's built-in `LOD` object swaps geometry by camera distance:
```jsx
function ProductLOD({ high, medium, low }) {
  const lod = useMemo(() => {
    const l = new THREE.LOD()
    l.addLevel(high, 0)
    l.addLevel(medium, 15)
    l.addLevel(low, 40)
    return l
  }, [high, medium, low])
  return <primitive object={lod} />
}
```

## Disposal

Covered in depth in `performance.md` — the summary: anything constructed by hand (`new THREE.BufferGeometry()`, `new THREE.ShaderMaterial()`, a manually created `WebGLRenderTarget`) needs an explicit `.dispose()` in a cleanup function. Drei's loader hooks manage their own cache/cleanup in the common case.

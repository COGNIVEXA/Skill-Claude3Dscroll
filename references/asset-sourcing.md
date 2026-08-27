# Real Assets and a Real Renderer Baseline

A page can have flawless scroll choreography and still look like a wireframe mockup if the 3D content itself is a hand-built primitive under flat lighting. This document covers where to pull free, commercial-use-safe assets, and the minimum renderer setup that makes even a simple scene read as an actual render instead of a programmer-art placeholder.

## The rule

**If a free, properly licensed asset already covers what the scene needs, use it instead of building it from primitives.** A phone, a bottle, a sneaker, a human figure — built from `BoxGeometry`/`CylinderGeometry`/`TorusGeometry` with a single flat `MeshStandardMaterial` color and default lighting — reads as a low-poly icon, not a product. Primitives are still the right call for a genuinely abstract or sculptural signature object (see `design-craft.md`), but even then they need real environment lighting and post-processing (below) to avoid looking flat.

## Where to get real assets (all free, all safe for commercial use)

- **3D models (glTF/GLB):**
  - [Poly Haven — Models](https://polyhaven.com/models) — CC0, no attribution required, photoscanned and studio-quality
  - [Khronos glTF-Sample-Assets](https://github.com/KhronosGroup/glTF-Sample-Assets) — the reference model set for glTF, permissively licensed, good for quick placeholders and testing PBR pipelines
  - [Quaternius](https://quaternius.com/) — CC0 low-poly/stylized packs, useful when the grammar calls for a stylized rather than photoreal look
  - [Sketchfab](https://sketchfab.com/) — filter downloads to CC0 or CC-BY explicitly; verify the license on each individual model before using it, since Sketchfab hosts mixed-license content

- **HDRI environment lighting:**
  - [Poly Haven — HDRIs](https://polyhaven.com/hdris) — CC0, wide range of studio and outdoor environments. Use one of these instead of (or in addition to) ambient/directional lights for anything meant to look like a real product render — reflections and ambient occlusion from a real HDRI are most of what separates a "photo" from a "render."

- **PBR textures:**
  - [Poly Haven — Textures](https://polyhaven.com/textures) — CC0
  - [ambientCG](https://ambientcg.com/) — CC0, large library, consistent naming for albedo/normal/roughness/AO map sets

- **Stock video (backgrounds, product footage, atmosphere):**
  - [Pexels Videos](https://www.pexels.com/videos/) — free, no attribution required, safe for commercial use
  - [Mixkit](https://mixkit.co/free-stock-video/) — free, no attribution required
  - [Coverr](https://coverr.co/) — free, check the specific clip's license terms (most are attribution-free)
  - Always **download and self-host** the file rather than hotlinking, and re-encode/compress it (e.g. with ffmpeg or HandBrake) to a web-appropriate bitrate before wiring it into scroll-scrubbing — an uncompressed source file will stall on-scroll seeking (see `pitfalls.md` and `qa-verification.md`).

- **Fonts:** [Google Fonts](https://fonts.google.com/) — free, open licenses, safe for commercial use.

None of the above require payment or attribution beyond what's noted, but always check the specific asset's license page before shipping — licenses on individual items can vary even within a "free" library.

## The renderer/post-processing baseline

This is what actually elevates a scene from flat to premium, independent of which specific asset is on screen.

**1. Light with a real environment, not just ambient + directional:**
```jsx
import { Environment } from '@react-three/drei'

// A bundled preset is a fast start...
<Environment preset="studio" />

// ...but a sourced Poly Haven HDRI reads as more specific/premium than a generic preset:
<Environment files="/hdri/studio_small_09_1k.hdr" background={false} />
```

**2. Load real geometry instead of building a product from primitives:**
```jsx
import { useGLTF } from '@react-three/drei'

function Product() {
  const { scene } = useGLTF('/models/product.glb')
  return <primitive object={scene} />
}
useGLTF.preload('/models/product.glb')
```

**3. Tone-map and grade the output — raw linear output is why a scene looks flat/plasticky:**
```jsx
<Canvas
  gl={{ antialias: true }}
  camera={{ position: [0, 0, 5], fov: 50 }}
  onCreated={({ gl }) => {
    gl.toneMapping = THREE.ACESFilmicToneMapping
    gl.toneMappingExposure = 1.1
    gl.outputColorSpace = THREE.SRGBColorSpace
  }}
>
```
(React Three Fiber sets sane sRGB/ACES defaults automatically in recent versions — confirm rather than assume, since an older Canvas config or a manually constructed `WebGLRenderer` may not.)

**4. Add a light post-processing pass — this is the single highest-leverage step for "does this look expensive":**
```jsx
import { EffectComposer, Bloom, Vignette, Noise } from '@react-three/postprocessing'

<EffectComposer>
  <Bloom intensity={0.4} luminanceThreshold={0.6} mipmapBlur />
  <Vignette eskil={false} offset={0.15} darkness={0.6} />
  <Noise opacity={0.02} />
</EffectComposer>
```
`@react-three/postprocessing` isn't in the default scaffold's dependencies — add it (`npm i @react-three/postprocessing postprocessing`) whenever a build needs this pass, which is effectively always for anything positioned as premium/HD.

**5. Shadows, if anything sits on a visible ground plane:**
```jsx
<Canvas shadows>
  <directionalLight castShadow position={[5, 8, 5]} shadow-mapSize={[2048, 2048]} />
  <mesh castShadow>...</mesh>
  <mesh receiveShadow>...</mesh>
</Canvas>
```

## Quick self-check before calling a hero scene done

- Is the object lit by a real HDRI or an environment preset — not only ambient + one directional light?
- Is anything meant to read as a real object built from a sourced model or real PBR textures, rather than flat-colored primitives?
- Does the final output pass through tone mapping and at least a light bloom/vignette pass, rather than the renderer's raw output?
- If the grammar calls for photography or footage, is it sourced from one of the libraries above (downloaded and compressed), rather than missing or a stand-in color block?

If any of these is "no" for a hero/product moment, the scene isn't at the bar yet — see `references/design-craft.md` for the rest of the standard it needs to clear.

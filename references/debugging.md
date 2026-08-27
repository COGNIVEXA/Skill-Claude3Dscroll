# Debugging — Systematic Diagnosis

`pitfalls.md` lists recurring mistakes to avoid proactively. This file is the reactive counterpart: when something is already broken, work through the relevant symptom below rather than guessing at fixes. Each entry gives the likely causes in the order worth checking, and how to confirm before changing code.

## Black or blank canvas

1. **Check the browser console first** — a thrown error during render (a bad prop, a missing texture the component doesn't guard against) can silently blank the canvas with no visible error banner in the page itself.
2. **Camera not looking at anything** — confirm `camera.position` isn't `[0,0,0]` coinciding with the scene origin, and that `camera.lookAt`/the default target actually points at content. Log `camera.position` and the target.
3. **Nothing in the scene yet** — if content loads via `useGLTF`/`useTexture` inside `Suspense`, confirm the `Suspense` fallback is actually rendering (not itself erroring) rather than assuming the model failed silently.
4. **`frameloop="demand"` with nothing ever calling `invalidate()`** — the canvas may be correctly composed but simply never told to paint a frame. See `performance.md` and `pitfalls.md` #7.
5. **WebGL context creation itself failed** — check `renderer.getContext()` isn't `null`; on some locked-down environments (certain corporate machines, some virtualized browsers) WebGL is disabled entirely. See `responsive-3d.md`'s fallback pattern.

## Missing model / 404

1. Confirm the path is relative to the `public/` root, not the source file's location — `useGLTF('/models/product.glb')` resolves against the served root, and a path copied from a component under `src/` is a common source of an off-by-one directory mistake.
2. Check the Network tab for the actual request URL and status code, not just "the model didn't appear" — a 404 vs. a CORS block vs. a slow/pending request each point to a different fix below.
3. Confirm the build actually includes the file — assets referenced only from JS strings (not imported) need to live in `public/` (Vite) or the framework's equivalent static-serving directory; a file sitting in `src/assets` referenced by a bare string path won't be copied to the build output.

## CORS failures (textures, HDRIs, fonts loaded from another origin)

1. If the asset is self-hosted, this shouldn't happen — move it into the project's own `public/` folder rather than fetching cross-origin, which sidesteps the problem entirely and is also better for load performance.
2. If it must stay cross-origin (a CDN, a headless CMS), confirm the remote server sends `Access-Control-Allow-Origin` for the requesting origin — this is server-side configuration on the asset host, not something fixable from the requesting page's code.
3. `crossOrigin` needs to be set on the loader before the load starts, not after: `useLoader(TextureLoader, url, (loader) => { loader.crossOrigin = 'anonymous' })`.

## Texture loading failure

1. Check the file actually decodes as the format its extension claims — a `.png` that's actually a `.webp` renamed, or a corrupted export, fails silently in some loaders rather than throwing.
2. Confirm color space is set appropriately (`threejs-r3f.md`) — a texture that "loads" but looks washed out or oversaturated is usually a color-space mismatch, not a load failure.
3. For KTX2/Basis-compressed textures, confirm the transcoder path is configured (`ktx2Loader.setTranscoderPath(...)`) and the corresponding WASM/JS transcoder files are actually served — a missing transcoder fails the texture load, not just degrades it.

## Animation clip missing / "no clip named X"

1. Log `animations.map(a => a.name)` from the loaded glTF/GLTF result and compare against the name used in `actions[name]` — Mixamo/Blender export names are easy to get subtly wrong (case sensitivity, a stray `Armature|` prefix Blender sometimes adds).
2. If the clip list is empty entirely, confirm the export actually included animations — a Blender glTF export with the wrong "Animation" checkbox state, or an FBX-to-GLB conversion step that dropped them, produces a model with a skeleton but zero clips.
3. See `animation-system.md`'s Mixamo pipeline for the export steps that most commonly go wrong (skin included in an animation-only download, mismatched skeletons across combined clips).

## Bone / skeleton problems (mesh deforms incorrectly, limbs stretch)

1. Usually a skeleton mismatch between a base mesh and an animation clip authored against a differently-proportioned rig — confirm every combined clip was retargeted against the *same* skeleton (`animation-system.md` step 2), not just visually similar ones.
2. Confirm `SkeletonUtils.clone` (not a plain object clone) was used for any duplicated skinned-mesh instance (`threejs-r3f.md`/`animation-system.md`) — a naive clone shares bone references, causing every instance to deform identically and incorrectly when only one plays a clip.

## Mixamo-specific animation problems

- Downloaded "with skin" for every clip instead of only the base character → produces multiple independent full meshes instead of one skeleton with multiple clips. Re-download animation-only clips ("without skin") and combine in Blender's NLA editor per `animation-system.md`.
- Root motion (the character sliding away from origin during Walk/Run) when the intended use is in-place looping → strip root bone translation on export, or handle it deliberately by driving the character's actual group position from the root bone's motion rather than fighting it.

## Scroll/`ScrollTrigger` desynchronization

Covered mechanically in `pitfalls.md` #4, #5, #7 and `scroll-animation.md`. Diagnosis order:
1. Did layout shift after `ScrollTrigger` measured the page (a late-loading image/font)? → confirm with `ScrollTrigger.refresh()` after load; if the desync disappears, that's the cause.
2. Is more than one scroll driver active (`scroll-animation.md`'s "one scroll source" rule)? → check for a second `onScroll` listener, a stray `ScrollControls`, or Lenis running without its `scroll` event wired to `ScrollTrigger.update`.
3. Did `React.StrictMode`'s double-invoke leave a duplicate trigger? → confirm cleanup uses `gsap.context().revert()` (`pitfalls.md` #4), and check `ScrollTrigger.getAll().length` for unexpected duplicates.

## Camera snapping / jitter

1. Confirm the camera is being damped/interpolated toward a target every frame, not set directly from a sampled scroll value (`scroll-animation.md`'s damping section) — a small dead zone in scroll-event granularity read straight into camera position is the most common cause.
2. Check for a second system also writing to `camera.position`/`camera.quaternion` in the same frame (`OrbitControls` left enabled alongside a scripted move — `pitfalls.md` #6).
3. Confirm delta-time-based damping, not a fixed-fraction lerp — a fixed `lerp(x, 0.1)` per frame produces visibly different apparent speed at different frame rates, which can look like stutter on a variable-refresh-rate display.

## Hydration errors / SSR problems (Next.js and similar)

1. Confirm the `<Canvas>` subtree is behind a `dynamic(..., { ssr: false })` boundary (`threejs-r3f.md`) — Three.js/WebGL code executing during server render (or during the client's hydration pass before the dynamic import resolves) is the near-universal cause of a 3D-related hydration mismatch.
2. Check for any `window`/`document`/`navigator` reference (device-tier detection, `matchMedia` for reduced motion) evaluated at module scope or during initial render rather than inside `useEffect`/inside the `ssr: false` boundary — these throw or mismatch during SSR even outside the Canvas itself.

## Excessive GPU usage / WebGL context loss

1. Check `renderer.info.render.calls` and `.triangles` (`performance.md`) — a draw-call count in the thousands on a scene that shouldn't need it usually means missing instancing or an accidental duplicate scene graph (a model added to the scene twice).
2. A context-loss event (`canvas.addEventListener('webglcontextlost', ...)`) firing on mobile usually means the page exceeded the device's available GPU memory — check total texture memory (`responsive-3d.md`'s texture-resolution tiers) before assuming it's a driver bug.
3. Handle context loss/restoration explicitly rather than leaving the canvas permanently blank after it happens:
```js
canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault() })
canvas.addEventListener('webglcontextrestored', () => { /* re-trigger scene setup */ })
```

## Shader compile errors (mesh renders black/magenta, no visible JS error)

1. Three.js logs GLSL compile errors to the console but easy to miss among other output — filter the console specifically for `THREE.WebGLProgram` or `INVALID` to find it.
2. A magenta/pink material is Three.js's fallback for a material that failed to compile — treat it as a signal to check the console, not a rendering bug in itself.
3. Common causes: a `varying` declared in one shader stage but not matched exactly (name/type) in the other, a `uniform` referenced but never registered in the material's `uniforms` object, or GLSL ES version mismatches when mixing `#version 300 es` syntax into an otherwise WebGL1-targeted pipeline.

## Z-fighting

Two coincident or near-coincident surfaces flickering between which renders on top. Fix by actually separating the surfaces (a tiny offset along the normal) rather than adjusting the camera's near/far planes as a first response — though a near plane set too close to zero (or a far plane far larger than the scene needs) does reduce depth-buffer precision and can make z-fighting worse across the whole scene, so check that too if a small manual offset alone doesn't fully resolve it.

## Incorrect normals (lighting looks inverted or flat on curved surfaces)

1. Check the source model was exported with normals included, and that any custom geometry built by hand called `.computeVertexNormals()` after modifying vertex positions.
2. Inverted normals on an imported model (faces lit as if from behind) usually trace back to the DCC tool's export settings (a "flip normals" step in Blender, or an FBX-to-glTF conversion that mishandled winding order) — fix at the source file, not by hacking the material to double-side render, which hides the problem rather than fixing it.

## Transparent material sorting problems (wrong object shows through another)

Three.js doesn't depth-sort transparent triangles perfectly by default — for a small number of transparent objects, set an explicit `renderOrder` on each; for genuinely complex overlapping transparency (particle systems, layered glass), consider whether the effect can be restructured (fewer overlapping transparent surfaces, or a dedicated order-independent-transparency technique) rather than fighting the default sort indefinitely.

## Memory leaks (frame rate degrades the longer the page stays open)

1. Confirm every manually created geometry/material/render target is disposed on unmount (`performance.md`) — this is the most common cause.
2. Confirm every GSAP tween/timeline and `ScrollTrigger` is killed on unmount/route change (`pitfalls.md` #3, #4) — a leaked infinite-repeat tween keeps running against a detached object indefinitely.
3. Watch `renderer.info.memory.geometries`/`.textures` over time in the console (or `r3f-perf`) while navigating the page — a number that keeps climbing and never comes back down on section/route change confirms a leak and roughly where in the flow it's introduced.

# Responsive 3D — Device Tiers

A scroll-driven 3D page needs a genuinely different rendering plan per device class, not just a resized layout. `performance.md` covers the individual techniques (DPR cap, instancing, disposal); this file covers how to tier them into a coherent policy and apply it in one place rather than scattering device checks through every component.

## Define tiers once

```js
// src/utils/deviceTier.js
export function getDeviceTier() {
  const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
  const cores = navigator.hardwareConcurrency || 4
  const mem = navigator.deviceMemory || 4   // GB; not supported in every browser, defaults conservatively
  const coarsePointer = window.matchMedia('(pointer: coarse)').matches

  if (isMobile && (cores <= 4 || mem <= 4)) return 'low'
  if (isMobile || coarsePointer) return 'medium'
  return 'high'
}
```
`navigator.deviceMemory` isn't available in every browser (notably Safari) — treat its absence as "unknown, assume mid-tier" rather than crashing, and combine it with `hardwareConcurrency` and a UA/pointer check rather than relying on one signal alone.

## What each tier controls

| Setting | Low | Medium | High |
|---|---|---|---|
| `dpr` | `1` (fixed) | `[1, 1.5]` | `[1, 2]` |
| Shadow maps | Off (fake with `ContactShadows` or a baked texture) | Low-res (`1024`) | Full (`2048`+) |
| Postprocessing | Off, or a single cheap pass | Bloom only | Full stack (Bloom, DoF, vignette, noise) |
| Particle count | 10–20% of authored count | ~50% | 100% |
| Model detail | Low-poly LOD level | Medium LOD | Full detail |
| Texture resolution | 512–1024px | 1024–2048px | 2048px+ / native |
| Number of animated characters on screen | 1 | 2–3 | Full authored count |
| `antialias` | Off (or FXAA in composer instead of MSAA) | On | On |
| Animation density (secondary/idle motion layers) | Primary motion only | Primary + one secondary layer | Full authored layering |

Apply this as one config object read at scene setup, not as `if (isMobile)` checks sprinkled through individual components:
```jsx
const TIER_CONFIG = {
  low:    { dpr: 1,          shadows: false, postprocessing: 'none',  particles: 0.15, textureRes: 1024 },
  medium: { dpr: [1, 1.5],   shadows: 'low',  postprocessing: 'bloom', particles: 0.5,  textureRes: 1024 },
  high:   { dpr: [1, 2],     shadows: 'full', postprocessing: 'full',  particles: 1,    textureRes: 2048 },
}
const tier = TIER_CONFIG[getDeviceTier()]
```

## Adaptive quality at runtime, not just at load

A static UA-based tier is a reasonable starting point but doesn't catch a mid-tier device that's actually struggling once the scene gets heavy. Layer Drei's runtime adaptive tools on top:
```jsx
import { PerformanceMonitor, AdaptiveDpr, AdaptiveEvents } from '@react-three/drei'

function Experience() {
  const [quality, setQuality] = useState('high')
  return (
    <Canvas dpr={tier.dpr}>
      <PerformanceMonitor
        onDecline={() => setQuality((q) => (q === 'high' ? 'medium' : 'low'))}
        onIncline={() => setQuality((q) => (q === 'low' ? 'medium' : 'high'))}
      />
      <AdaptiveDpr pixelated />
      <AdaptiveEvents />
      <Scene quality={quality} />
    </Canvas>
  )
}
```
`PerformanceMonitor` samples actual measured frame time and calls `onDecline`/`onIncline` as it drifts — this catches thermal throttling and background-tab recovery that a load-time-only check can't.

## Responsive camera and layout, not just quality

Scroll-driven camera choreography authored against a desktop viewport often doesn't translate directly to a portrait mobile aspect ratio — a wide establishing shot that reads correctly at 16:9 can crop out the actual subject at 9:16. Options, roughly in order of effort:
```jsx
const { viewport } = useThree()
const isPortrait = viewport.aspect < 1

const fov = isPortrait ? 65 : 50            // wider FOV compensates for a narrower frame
const cameraDistance = isPortrait ? 6 : 4.5  // pull back further so the subject still fits
```
For anything more than a FOV/distance adjustment — an entirely different camera path per breakpoint — author it as a second, simpler path rather than trying to make one path work everywhere; see `scroll-animation.md`'s reduced-motion note, which often overlaps with the mobile-simplified path.

## Resize handling

```jsx
<Canvas resize={{ scroll: false, debounce: { resize: 100 } }}>
```
Debounce resize handling (orientation change, browser chrome show/hide on mobile scroll, a resizable window) — recomputing the full scene layout on every intermediate resize event during a drag-resize or an animated mobile URL-bar collapse is wasted work and can itself cause visible jank.

## Fallback for WebGL-unsupported or too-low-power devices

Detect and degrade gracefully rather than showing a blank canvas or a console error:
```jsx
function useWebGLSupport() {
  return useMemo(() => {
    try {
      const canvas = document.createElement('canvas')
      return !!(canvas.getContext('webgl2') || canvas.getContext('webgl'))
    } catch {
      return false
    }
  }, [])
}

function Experience() {
  const supported = useWebGLSupport()
  if (!supported) return <StaticFallbackHero />   // a real designed static/video hero, not an error message
  return <Canvas>...</Canvas>
}
```
See `accessibility.md` for why this fallback needs to carry the same essential content and messaging as the 3D version, not just a "please use a different browser" notice.

## Testing across tiers

`qa-verification.md`'s script supports a `--viewport` flag — run it at both a desktop and a mobile viewport size per build (the doc recommends this explicitly). Pair that with actually throttling CPU in Chrome DevTools (Performance panel → CPU: 4x/6x slowdown) to approximate the "low" tier during development, since a desktop dev machine will otherwise never surface what a genuinely underpowered device experiences.

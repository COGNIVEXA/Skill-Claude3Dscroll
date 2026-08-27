# Shaders — When and How

GLSL is a last resort, not a default. `MeshStandardMaterial`/`MeshPhysicalMaterial` plus real HDRI lighting (`asset-sourcing.md`) already covers the large majority of what makes a scene look premium. Reach for a custom shader only when the effect genuinely can't be built from standard materials — a specific reveal/dissolve transition, a stylized non-physical surface, a portal/hologram effect, animated water, or a particle field driven by a vertex shader for performance reasons.

## Decision check before writing GLSL

- Does a standard material + real lighting + postprocessing already achieve this? → don't write a shader.
- Is this a one-off visual flourish that could instead be a Drei helper (`MeshTransmissionMaterial`, `MeshDistortMaterial`, `MeshWobbleMaterial`, `MeshRefractionMaterial`) already covering the effect? → use the helper.
- Is the actual need "many repeated objects need per-instance variation cheaply" rather than a visual effect at all? → that's instancing (`threejs-r3f.md`), not a shader.
- Only write custom GLSL when the answer to all of the above is no.

## `ShaderMaterial` skeleton

```jsx
import { shaderMaterial } from '@react-three/drei'
import { extend } from '@react-three/fiber'
import * as THREE from 'three'

const DissolveMaterial = shaderMaterial(
  { uProgress: 0, uEdgeColor: new THREE.Color('#ff6b35'), uEdgeWidth: 0.08, uNoiseScale: 4 },
  /* glsl */ `
    varying vec2 vUv;
    varying vec3 vPosition;
    void main() {
      vUv = uv;
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  /* glsl */ `
    uniform float uProgress;
    uniform vec3 uEdgeColor;
    uniform float uEdgeWidth;
    uniform float uNoiseScale;
    varying vec2 vUv;
    varying vec3 vPosition;

    // simple hash-based noise — swap for a proper simplex/perlin import if the effect needs smoother detail
    float hash(vec3 p) { return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453); }

    void main() {
      float n = hash(floor(vPosition * uNoiseScale));
      if (n < uProgress) discard;
      float edge = smoothstep(uProgress, uProgress + uEdgeWidth, n);
      vec3 color = mix(uEdgeColor, vec3(0.9), edge);
      gl_FragColor = vec4(color, 1.0);
    }
  `
)
extend({ DissolveMaterial })

function DissolvingModel({ progress }) {
  const ref = useRef()
  useFrame(() => { ref.current.uProgress = progress })
  return (
    <mesh geometry={geometry}>
      <dissolveMaterial ref={ref} uProgress={0} transparent />
    </mesh>
  )
}
```
`shaderMaterial` (Drei) registers a JSX-usable material from uniforms + vertex/fragment strings, and `extend` makes it available as a lowercase JSX tag — this is the standard way to author a custom material in R3F rather than manually constructing `THREE.ShaderMaterial` and passing it via `<primitive>`.

## Fresnel (rim light / energy-shield look)

```glsl
// vertex
varying vec3 vNormal;
varying vec3 vViewDir;
void main() {
  vNormal = normalize(normalMatrix * normal);
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vViewDir = normalize(-mvPosition.xyz);
  gl_Position = projectionMatrix * mvPosition;
}

// fragment
uniform vec3 uColor;
uniform float uPower;
varying vec3 vNormal;
varying vec3 vViewDir;
void main() {
  float fresnel = pow(1.0 - max(dot(vNormal, vViewDir), 0.0), uPower);
  gl_FragColor = vec4(uColor * fresnel, fresnel);
}
```
Higher `uPower` (3–6) narrows the rim to the silhouette edge; lower (1–2) spreads it across more of the visible surface.

## Vertex displacement (organic surface motion, animated terrain)

```glsl
// vertex
uniform float uTime;
uniform float uAmplitude;
varying vec3 vNormal;

// classic simplex/perlin noise function assumed included above (glsl-noise or similar)
void main() {
  vNormal = normal;
  vec3 pos = position;
  float displacement = snoise(pos * 0.5 + uTime * 0.2) * uAmplitude;
  pos += normal * displacement;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
```
Don't hand-write a noise function from scratch — import a well-tested one (`glsl-noise`'s simplex implementation, or Three.js's own `SimplexNoise` sampled on the CPU and passed as a texture for very cheap lookups) rather than reinventing it per project.

## Portal / holographic scan-line effect

```glsl
uniform float uTime;
uniform vec3 uColor;
varying vec2 vUv;

void main() {
  float scanline = sin(vUv.y * 200.0 - uTime * 4.0) * 0.5 + 0.5;
  float edge = smoothstep(0.0, 0.05, vUv.y) * smoothstep(1.0, 0.95, vUv.y);
  float alpha = (0.3 + scanline * 0.4) * edge;
  gl_FragColor = vec4(uColor, alpha);
}
```
Layer this as a separate transparent plane/shell over the portal geometry rather than trying to fold it into the same material as the portal's "contents" — keeps the effect composable and cheap to toggle independently.

## Transition masks between two scenes

For a scroll-driven cross-fade or dissolve between two full-screen render passes, drive a mask in a postprocessing pass rather than per-object shaders when the whole scene is transitioning at once:
```glsl
// fragment (postprocessing custom effect)
uniform sampler2D uSceneA;
uniform sampler2D uSceneB;
uniform sampler2D uMask;   // a noise or gradient texture
uniform float uProgress;
varying vec2 vUv;

void main() {
  float m = texture2D(uMask, vUv).r;
  float threshold = smoothstep(uProgress - 0.05, uProgress + 0.05, m);
  vec4 a = texture2D(uSceneA, vUv);
  vec4 b = texture2D(uSceneB, vUv);
  gl_FragColor = mix(a, b, threshold);
}
```
See `scroll-animation.md`'s cross-scene transition section for when a simple opacity lerp is enough and this level of effort isn't warranted.

## Performance notes specific to shaders

- Every uniform update from JS (`material.uniforms.uProgress.value = x`) is cheap; avoid recompiling the shader (changing `#define`s or the source string itself) at runtime — that stalls the frame it happens on.
- Prefer doing per-vertex work in the vertex shader and only the minimum in the fragment shader — the fragment shader runs once per pixel, the vertex shader once per vertex, and a hero object is usually far more pixels than vertices.
- Test shader-heavy sections against `responsive-3d.md`'s device tiers specifically — a shader that holds 60fps on desktop can be the single biggest cost on a low-power mobile GPU; have a plan to swap it for a cheaper material/precomputed texture on the lowest tier.
- Watch for shader compile errors surfacing as a silently black mesh rather than a thrown JS error — `debugging.md` covers how to actually see the GLSL compiler's error message.

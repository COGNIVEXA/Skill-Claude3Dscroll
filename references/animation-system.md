# Character & Object Animation, and Camera Choreography

Covers keyframe/skeletal animation playback (Mixamo characters, animated glTF props) and the vocabulary for authoring camera moves as deliberate shots. `scroll-animation.md` covers *what drives* the timeline (scroll progress); this file covers *what plays* once it's driven — animation clips and camera grammar.

## Mixamo characters, end to end

1. **Rig** a character in Mixamo (or use one of its pre-rigged characters) and download animations (Idle, Walk, Run, Wave, Sit, Talk, Point, etc.) **without skin**, in FBX, at 30fps, targeting the same character so bone names match across clips.
2. **Combine in Blender**: import the base character FBX with skin once, then import each animation-only FBX and use the NLA (Non-Linear Animation) editor or an Action per clip, so the final export carries one skeleton with multiple named animation clips rather than one file per action.
3. **Export GLB** with animations included, Draco-compressed (`gltf-transform` or Blender's own glTF exporter compression option — see `performance.md`/`threejs-r3f.md`).
4. Confirm each clip name survives the export (`Idle`, `Walk`, `Run` — Mixamo's raw names, e.g. `mixamo.com`, are worth renaming before export so the code isn't full of meaningless clip names).

Licensing note: Mixamo characters/animations are free to use, including commercially, under Adobe's Mixamo terms, but confirm current terms before shipping a commercial build — see `asset-licensing.md`.

## Playing clips with `useAnimations`

```jsx
import { useGLTF, useAnimations } from '@react-three/drei'
import { useEffect, useRef } from 'react'

function Character({ animation = 'Idle', ...props }) {
  const group = useRef()
  const { scene, animations } = useGLTF('/models/student.glb')
  const { actions, mixer } = useAnimations(animations, group)

  useEffect(() => {
    const action = actions[animation]
    if (!action) return
    action.reset().fadeIn(0.35).play()
    return () => { action.fadeOut(0.35) }
  }, [animation, actions])

  return (
    <group ref={group} {...props}>
      <primitive object={scene} />
    </group>
  )
}
useGLTF.preload('/models/student.glb')
```
`fadeIn`/`fadeOut` on the action (backed by `AnimationMixer.crossFadeTo` internally when both actions are running) gives a soft blend between states instead of an instant pop — always cross-fade rather than hard-cutting `action.play()`/`action.stop()` when swapping between Idle/Walk/Run.

## One-shot vs looping actions

```jsx
const action = actions['Wave']
action.setLoop(THREE.LoopOnce, 1)
action.clampWhenFinished = true   // hold the last frame instead of snapping back to bind pose
action.reset().fadeIn(0.2).play()

mixer.addEventListener('finished', (e) => {
  if (e.action === action) setAnimation('Idle')   // return to a looping state when the one-shot ends
})
```
Looping states (`Idle`, `Walk`, `Run`) use the default `THREE.LoopRepeat`; gestures (`Wave`, `Point`, `Sit` transition-in) are one-shots that hand control back to a looping state on `finished`.

## A minimal animation state machine

For more than two or three states, don't manage transitions with ad hoc `if` chains scattered across effects — centralize:
```jsx
function useCharacterState(initial = 'Idle') {
  const [state, setState] = useState(initial)
  const transitions = {
    Idle: ['Walk', 'Wave', 'Sit'],
    Walk: ['Idle', 'Run'],
    Run: ['Walk'],
    Wave: ['Idle'],
    Sit: ['Idle'],
  }
  const transitionTo = (next) => {
    if (transitions[state]?.includes(next)) setState(next)
  }
  return [state, transitionTo]
}
```
This keeps illegal transitions (Run → Sit with no Idle in between, which would pop rather than blend cleanly) from ever reaching the animation layer.

## Multiple instances of the same animated character

`useGLTF`'s cache returns the same object graph for a repeated URL — cloning a skinned mesh needs `SkeletonUtils`, not a plain object spread, or every instance will share (and fight over) one skeleton:
```jsx
import { clone as cloneSkeleton } from 'three/examples/jsm/utils/SkeletonUtils.js'

function useClonedScene(url) {
  const { scene } = useGLTF(url)
  return useMemo(() => cloneSkeleton(scene), [scene])
}
```
Each cloned instance still needs its own `useAnimations`/mixer against its own cloned scene graph.

## Driving animation from scroll or state, not just autoplay

An animated character/prop in a scroll-driven page usually shouldn't just loop freely — tie the active clip (or the mixer's `time`) to scroll progress or section state so the character's action matches the story beat:
```jsx
useEffect(() => {
  if (chapter === 2) transitionTo('Walk')
  if (chapter === 3) transitionTo('Wave')
}, [chapter])
```
For a fully scroll-scrubbed (not looping) clip — e.g. a product assembling itself as the visitor scrolls — drive the mixer's time directly instead of playing/pausing:
```jsx
useFrame(() => {
  const clipDuration = actions['Assemble'].getClip().duration
  mixer.setTime(scrollProgress.current * clipDuration)
})
```
Don't call `action.play()` at all in this mode — `setTime` on the mixer scrubs the clip like a video, which is what a scroll-scrubbed assembly/transformation sequence needs.

## Camera choreography as cinematography

Treat every camera move as an authored shot, not a free parametric drift. Useful vocabulary, matched to what each communicates:

| Shot | Use it for | Notes |
|---|---|---|
| Establishing shot | Opening frame, sets scale/context | Wide FOV, camera mostly static or very slow drift |
| Approach / push-in | Building anticipation toward a subject | Ease toward the target, don't arrive at constant velocity |
| Reveal | Uncovering something previously off-frame or occluded | Often paired with a pan or a rise, timed to land exactly as content appears |
| Orbit | Showing a product/subject from multiple angles | Constrain to an arc, not a full 360 unless that's genuinely the point — a full spin reads as a stock product-viewer trope |
| Dolly | Lateral or forward/back translation past a scene | Keep the look-at target moving too, or the framing drifts oddly |
| Fly-through | Continuous-world pages, moving through connected spaces | Needs a real authored path (a spline), not just interpolating between two points |
| Room/section transition | Chaptered pages, moving from one space to the next | Cut, whip-pan, or a fast dolly + cross-fade — pick one per project, don't mix transition styles between chapters |
| Subject focus / rack focus | Directing attention to one element among several | Pair with depth of field (`shaders.md`/postprocessing) if the budget allows it |
| Pull-back | Closing a chapter, restoring context after a close focus | Often the inverse curve of the approach that opened the chapter |
| Ending frame | Final scroll position | Should read as a deliberate resting composition, not wherever the last tween happens to land |

## Rules that prevent the common camera failures

- **Never snap orientation.** Always `slerp`/damp quaternions (`scroll-animation.md` has the damping formula) — a hard-cut rotation reads as a bug even at 1 frame.
- **Cap angular velocity.** Even damped, a camera that has to cover 150° in one scroll-trigger's span will look like it's spinning out of control. Split it into two shots with a beat between them instead.
- **Author paths, don't just lerp between keyframes on a straight line**, when the path crosses geometry — use a `THREE.CatmullRomCurve3` through control points and sample position/tangent along it so the camera doesn't clip through a wall it's supposed to be flying past.
- **Check for clipping at every keyframe**, not just start/end — a straight-line interpolation between two valid camera positions can still pass through geometry at the midpoint.
- **Provide a reduced-motion alternative** for any shot that covers significant distance or rotation — see `accessibility.md`. A fly-through can become a hard cut with no interpolation; an orbit can become a static three-quarter view.
- **Match FOV to intent.** A narrower FOV (30–40°) compresses depth and reads as more "telephoto/cinematic" for a hero product shot; a wider FOV (60–75°) suits an establishing or fly-through shot where spatial context matters more than compression.

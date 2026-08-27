# Integration Recipes

Patterns that come up regardless of which architecture from `architecture-patterns.md` a build is using.

## 1. Camera movement tied to scroll

**Three.js + GSAP** — an explicit multi-point camera path inside a pinned section:
```javascript
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)

const cameraPath = [
  { x: 0, y: 2, z: 5, lookAt: { x: 0, y: 0, z: 0 } },
  { x: 5, y: 3, z: 10, lookAt: { x: 0, y: 0, z: 0 } },
  { x: -3, y: 1, z: 8, lookAt: { x: 0, y: 0, z: 0 } },
]

const tl = gsap.timeline({
  scrollTrigger: { trigger: '#container', start: 'top top', end: 'bottom bottom', scrub: 1, pin: true },
})

cameraPath.forEach((point, i) => {
  tl.to(camera.position, {
    x: point.x, y: point.y, z: point.z, duration: 1,
    onUpdate: () => camera.lookAt(point.lookAt.x, point.lookAt.y, point.lookAt.z),
  }, i)
})
```

**R3F with Drei's `ScrollControls`:**
```jsx
import { ScrollControls, Scroll, useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'

function CameraRig() {
  const scroll = useScroll()
  useFrame((state) => {
    const offset = scroll.offset
    state.camera.position.x = Math.sin(offset * Math.PI * 2) * 5
    state.camera.position.z = Math.cos(offset * Math.PI * 2) * 5
    state.camera.lookAt(0, 0, 0)
  })
  return null
}

export function App() {
  return (
    <Canvas>
      <ScrollControls pages={3} damping={0.5}>
        <CameraRig />
        <Scroll><Scene /></Scroll>
      </ScrollControls>
    </Canvas>
  )
}
```

Keep the scrub/damping value above zero for any camera work tied to scroll — a raw 1:1 scrub reads as jittery under a trackpad or a high-polling-rate mouse.

## 2. Pointer-driven manipulation of 3D objects

**R3F + Motion (`framer-motion-3d`):**
```jsx
import { motion } from 'framer-motion-3d'

function DraggableObject() {
  return (
    <motion.mesh
      drag
      dragElastic={0.1}
      dragConstraints={{ left: -5, right: 5, top: 5, bottom: -5 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      animate={{ rotateY: [0, Math.PI * 2], transition: { repeat: Infinity, duration: 4, ease: 'linear' } }}
    >
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="hotpink" />
    </motion.mesh>
  )
}
```

## 3. Keeping animation in sync with app state (R3F + Zustand + GSAP)

```javascript
// store.js
import { create } from 'zustand'

export const useStore = create((set) => ({
  selectedObject: null,
  cameraMode: 'orbit',
  setSelectedObject: (obj) => set({ selectedObject: obj }),
  setCameraMode: (mode) => set({ cameraMode: mode }),
}))
```

```jsx
// components/InteractiveObject.jsx
import { useRef, useEffect } from 'react'
import { useStore } from '../store'
import gsap from 'gsap'

export function InteractiveObject({ id }) {
  const meshRef = useRef()
  const selectedObject = useStore((s) => s.selectedObject)
  const setSelectedObject = useStore((s) => s.setSelectedObject)
  const isSelected = selectedObject === id

  useEffect(() => {
    const scaleTo = isSelected ? 1.2 : 1
    const emissiveTo = isSelected ? 0.5 : 0
    const scaleTween = gsap.to(meshRef.current.scale, { x: scaleTo, y: scaleTo, z: scaleTo, duration: 0.3, ease: isSelected ? 'back.out' : 'power2.inOut' })
    const emissiveTween = gsap.to(meshRef.current.material, { emissiveIntensity: emissiveTo, duration: 0.3 })
    return () => { scaleTween.kill(); emissiveTween.kill() }
  }, [isSelected])

  return (
    <mesh ref={meshRef} onClick={() => setSelectedObject(isSelected ? null : id)}>
      <boxGeometry />
      <meshStandardMaterial color="cyan" emissive="cyan" />
    </mesh>
  )
}
```

Notice the cleanup: any tween created inside an effect has to be killed before the next run or on unmount — see `pitfalls.md` for why this bites harder in R3F than in a plain React component.

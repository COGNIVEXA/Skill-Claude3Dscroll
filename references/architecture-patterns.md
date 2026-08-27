# Integration Architectures

Four ways to wire 3D and animation libraries together. Commit to one per build, matched to the page grammar (`design-craft.md`) and stack (`decision-matrix.md`) — mixing patterns inside a single build is how state ownership gets confused.

---

## Architecture 1: Split-Layer (Three.js + GSAP + a React shell)

**Fits:** scroll-driven 3D sequences, timeline choreography, cinematic single-take pages, continuous-world pages where the whole viewport is one persistent 3D stage.

**Shape:**
```
├── 3D layer (Three.js)        scene graph, camera, render loop
├── Timing layer (GSAP)        ScrollTrigger driving 3D properties, sequencing
└── UI layer (React)           HTML content laid over the canvas, interaction state
```

**React root:**
```jsx
// App.jsx
import { useEffect, useRef } from 'react'
import { initThreeScene } from './three/scene'
import { initScrollAnimations } from './animations/scroll'

function App() {
  const canvasRef = useRef()
  const sceneRef = useRef()

  useEffect(() => {
    sceneRef.current = initThreeScene(canvasRef.current)
    initScrollAnimations(sceneRef.current)
    return () => sceneRef.current.dispose()
  }, [])

  return (
    <div className="app">
      <canvas ref={canvasRef} />
      <div className="overlay">
        <section className="hero"><h1>3D Experience</h1></section>
        <section className="content">{/* scrollable content */}</section>
      </div>
    </div>
  )
}
```

**Three.js setup:**
```javascript
// three/scene.js
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

export function initThreeScene(canvas) {
  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(75, innerWidth / innerHeight, 0.1, 1000)
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true })
  renderer.setSize(innerWidth, innerHeight)
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2))

  const controls = new OrbitControls(camera, canvas)
  controls.enableDamping = true

  const cube = new THREE.Mesh(
    new THREE.BoxGeometry(2, 2, 2),
    new THREE.MeshStandardMaterial({ color: 0x00ff00 })
  )
  scene.add(cube)
  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  const dir = new THREE.DirectionalLight(0xffffff, 1)
  dir.position.set(5, 10, 7.5)
  scene.add(dir)
  camera.position.set(0, 2, 5)

  function animate() {
    requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }
  animate()

  addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(innerWidth, innerHeight)
  })

  return {
    scene, camera, renderer, cube,
    dispose: () => { renderer.dispose(); controls.dispose() },
  }
}
```

**GSAP driving the scene on scroll:**
```javascript
// animations/scroll.js
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)

export function initScrollAnimations({ camera, cube }) {
  gsap.to(camera.position, {
    x: 5, y: 3, z: 10,
    scrollTrigger: { trigger: '.content', start: 'top top', end: 'bottom center', scrub: 1 },
    onUpdate: () => camera.lookAt(cube.position),
  })

  gsap.to(cube.rotation, {
    y: Math.PI * 2, x: Math.PI,
    scrollTrigger: { trigger: '.content', start: 'top bottom', end: 'bottom top', scrub: true },
  })

  gsap.to(cube.material, {
    opacity: 0.3,
    scrollTrigger: { trigger: '.content', start: 'top center', end: 'center center', scrub: 1 },
  })
}
```

**Strengths:** cleanly separated concerns, straightforward data flow, each layer can be tuned or tested independently.
**Costs:** more boilerplate than a unified approach, and synchronization across the three layers has to be handled by hand.

---

## Architecture 2: All-React Composition (React Three Fiber + Motion)

**Fits:** a React-first codebase, declarative 3D content, product viewers, galleries, dual-pane stages.

```jsx
// App.jsx
import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import { Scene } from './components/Scene'
import { Loader } from './components/Loader'

function App() {
  return (
    <div className="app">
      <Canvas camera={{ position: [0, 2, 5], fov: 75 }} dpr={[1, 2]} shadows>
        <Suspense fallback={<Loader />}>
          <Scene />
        </Suspense>
      </Canvas>
      <div className="ui-overlay"><h1>React-First 3D Experience</h1></div>
    </div>
  )
}
```

```jsx
// components/Scene.jsx
import { useState } from 'react'
import { OrbitControls, Environment } from '@react-three/drei'
import { motion } from 'framer-motion-3d'

export function Scene() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 7.5]} castShadow />
      <AnimatedCube />
      <Floor />
      <OrbitControls enableDamping dampingFactor={0.05} />
      <Environment preset="sunset" />
    </>
  )
}

function AnimatedCube() {
  const [hovered, setHovered] = useState(false)
  const [active, setActive] = useState(false)
  return (
    <motion.mesh
      scale={active ? 1.5 : 1}
      onClick={() => setActive(!active)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      animate={{ rotateY: hovered ? Math.PI * 2 : 0 }}
      transition={{ type: 'spring', stiffness: 200, damping: 20 }}
    >
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </motion.mesh>
  )
}

function Floor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]} receiveShadow>
      <planeGeometry args={[100, 100]} />
      <meshStandardMaterial color="#222" />
    </mesh>
  )
}
```

**Strengths:** declarative, one state model for the whole tree, components are reusable and testable with normal React tooling.
**Costs:** R3F has its own learning curve, the render loop is less directly controllable, and unnecessary React re-renders can quietly drive unwanted work in the 3D tree.

---

## Architecture 3: Blended Timeline Control (R3F + GSAP timelines)

**Fits:** carefully paced multi-step sequences living inside a React component tree — chaptered narratives, hard-cut sequences.

```jsx
// components/AnimatedScene.jsx
import { useRef, useEffect } from 'react'
import gsap from 'gsap'

export function AnimatedScene() {
  const groupRef = useRef()

  useEffect(() => {
    const tl = gsap.timeline({ repeat: -1, yoyo: true })
    tl.to(groupRef.current.position, { y: 2, duration: 1, ease: 'power2.inOut' })
      .to(groupRef.current.rotation, { y: Math.PI * 2, duration: 2, ease: 'none' }, 0)
    return () => tl.kill()
  }, [])

  return (
    <group ref={groupRef}>
      <mesh><boxGeometry /><meshStandardMaterial color="cyan" /></mesh>
    </group>
  )
}
```

Kill the timeline in the effect's cleanup every time — a repeating GSAP timeline left running against an R3F node after it unmounts is the most common leak this pattern produces (see `pitfalls.md`).

---

## Architecture 4: Physics-Flavored Interaction (R3F + React Spring)

**Fits:** interaction that should feel handled — drag, hover feedback, a signature move built to feel alive rather than merely eased.

```jsx
// components/PhysicsCube.jsx
import { useSpring, animated, config } from '@react-spring/three'

const AnimatedMesh = animated('mesh')

export function PhysicsCube() {
  const [springs, api] = useSpring(() => ({
    scale: 1, position: [0, 0, 0], config: config.wobbly,
  }), [])

  const handleClick = () => {
    api.start({ scale: 1.5, position: [0, 2, 0] })
    setTimeout(() => api.start({ scale: 1, position: [0, 0, 0] }), 1000)
  }

  return (
    <AnimatedMesh scale={springs.scale} position={springs.position} onClick={handleClick}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </AnimatedMesh>
  )
}
```

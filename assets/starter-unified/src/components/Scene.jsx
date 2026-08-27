import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Environment } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import { useSceneStore } from '../store/scene'

// This icosahedron is a placeholder abstract/sculptural object, not a stand-in
// for a real product. If this scene needs to represent an actual product,
// character, or prop, replace it with a sourced glTF model instead of
// building the real thing out of primitives — see the parent skill's
// references/asset-sourcing.md for free, commercial-use sources and for the
// useGLTF loading pattern. The environment lighting and post-processing pass
// below apply either way; they're what keep even this placeholder from
// looking flat.
export function Scene() {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 8, 5]} intensity={1.2} />
      <HeroObject />
      <Environment preset="studio" />
      <EffectComposer>
        <Bloom intensity={0.4} luminanceThreshold={0.6} mipmapBlur />
        <Vignette eskil={false} offset={0.15} darkness={0.6} />
      </EffectComposer>
    </>
  )
}

function HeroObject() {
  const meshRef = useRef()
  const scrollProgress = useSceneStore((s) => s.scrollProgress)

  useFrame((_, delta) => {
    if (!meshRef.current) return
    meshRef.current.rotation.y += delta * 0.15
    // Scroll-driven property: GSAP owns the timeline that writes
    // scrollProgress into the store; this frame loop reacts to it.
    meshRef.current.position.y = -1 + scrollProgress * 2
  })

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[1.4, 1]} />
      <meshStandardMaterial color="#ff6b35" roughness={0.3} metalness={0.4} />
    </mesh>
  )
}

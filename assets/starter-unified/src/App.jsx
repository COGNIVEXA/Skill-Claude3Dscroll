import { Canvas } from '@react-three/fiber'
import { Suspense, useEffect } from 'react'
import { Scene } from './components/Scene'
import { Loader } from './components/Loader'
import { initScrollAnimations } from './animations/scroll'

export default function App() {
  useEffect(() => {
    const cleanup = initScrollAnimations()
    return cleanup
  }, [])

  return (
    <div className="app">
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }} dpr={[1, 2]}>
        <Suspense fallback={<Loader />}>
          <Scene />
        </Suspense>
      </Canvas>

      <div className="overlay acts">
        <section className="act">
          <h1 data-qa-track>starter-unified</h1>
          <p data-qa-track>
            Replace this starter copy. Scroll drives the object above via
            GSAP ScrollTrigger writing into a shared Zustand store that the
            R3F scene reads in its frame loop.
          </p>
        </section>
        <section className="act">
          <h2 data-qa-track>Act two</h2>
          <p data-qa-track>
            Each act fades its [data-qa-track] elements in on scroll and
            marks itself active in the store: read this from a nav or
            progress indicator if you need one.
          </p>
        </section>
        <section className="act">
          <h2 data-qa-track>Act three</h2>
          <p data-qa-track>
            This is scaffolding, not a finished page. Apply the design
            standard in references/design-craft.md before shipping.
          </p>
        </section>
      </div>
    </div>
  )
}

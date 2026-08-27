#!/usr/bin/env python3
"""
scaffold_project.py

Part of the claude3Dscroll skill (by Cognivexa).

Builds a working starter project on Vite + React + React Three Fiber +
GSAP ScrollTrigger + Motion + Zustand — the "blended timeline control"
architecture: an R3F scene, GSAP timelines driving it, a shared Zustand
store, and an HTML overlay on top.

Usage:
    python scaffold_project.py <project-name> [--dir ./target] [--accent "#ff6b35"]

Once it's done:
    cd <target>
    npm install
    npm run dev

Note: file contents are filled in with plain string.replace() against
__TOKEN__ placeholders rather than str.format() — the templates are JS/
JSX/CSS/JSON source, so they're full of literal { } braces that
str.format() would try to parse as fields and choke on.
"""

import argparse
import sys
from pathlib import Path

PACKAGE_JSON = """{
  "name": "__NAME__",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "three": "^0.169.0",
    "@react-three/fiber": "^8.17.10",
    "@react-three/drei": "^9.114.3",
    "gsap": "^3.12.5",
    "motion": "^11.11.17",
    "@react-spring/three": "^9.7.5",
    "@react-three/postprocessing": "^2.16.3",
    "postprocessing": "^6.36.4",
    "zustand": "^5.0.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.3",
    "vite": "^5.4.10"
  }
}
"""

VITE_CONFIG = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { host: true },
})
"""

INDEX_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>__TITLE__</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

MAIN_JSX = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

INDEX_CSS = """:root {
  --bg: #0a0a0c;
  --surface: #16161a;
  --text: #f2f1ee;
  --text-secondary: #a6a3ab;
  --border: #2a2a30;
  --accent: __ACCENT__;
  --space-1: 4px;
  --space-2: 8px;
  --space-4: 16px;
  --space-8: 32px;
  --space-16: 64px;
  --space-24: 96px;
  --space-40: 160px;
}

* { box-sizing: border-box; }

html, body, #root {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
  overflow-x: hidden;
}

.app { position: relative; }

canvas { position: fixed; inset: 0; z-index: 0; }

.overlay {
  position: relative;
  z-index: 1;
  pointer-events: none;
}

.overlay a, .overlay button { pointer-events: auto; }

section {
  min-height: 100vh;
  padding: var(--space-24) clamp(20px, 6vw, var(--space-40));
  display: flex;
  flex-direction: column;
  justify-content: center;
}

h1, h2, h3 {
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.05;
  margin: 0 0 var(--space-4);
}

h1 { font-size: clamp(40px, 8vw, 96px); }
h2 { font-size: clamp(28px, 4vw, 48px); }

p {
  max-width: 65ch;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: clamp(16px, 1.4vw, 19px);
  margin: 0;
}

[data-qa-track] { will-change: opacity, transform; }
"""

STORE_JS = """import { create } from 'zustand'

export const useSceneStore = create((set) => ({
  scrollProgress: 0,
  activeAct: 0,
  isReady: false,

  setScrollProgress: (scrollProgress) => set({ scrollProgress }),
  setActiveAct: (activeAct) => set({ activeAct }),
  setReady: (isReady) => set({ isReady }),
}))
"""

SCENE_JSX = """import { useRef } from 'react'
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
      <meshStandardMaterial color="__ACCENT__" roughness={0.3} metalness={0.4} />
    </mesh>
  )
}
"""

LOADER_JSX = """export function Loader() {
  return (
    <mesh>
      <boxGeometry args={[0.4, 0.4, 0.4]} />
      <meshBasicMaterial color="white" wireframe />
    </mesh>
  )
}
"""

SCROLL_JS = """import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useSceneStore } from '../store/scene'

gsap.registerPlugin(ScrollTrigger)

export function initScrollAnimations(containerSelector = '.acts') {
  const ctx = gsap.context(() => {
    const setScrollProgress = useSceneStore.getState().setScrollProgress
    const setActiveAct = useSceneStore.getState().setActiveAct

    ScrollTrigger.create({
      trigger: containerSelector,
      start: 'top top',
      end: 'bottom bottom',
      scrub: 1,
      onUpdate: (self) => setScrollProgress(self.progress),
    })

    gsap.utils.toArray('.act').forEach((act, i) => {
      ScrollTrigger.create({
        trigger: act,
        start: 'top center',
        end: 'bottom center',
        onEnter: () => setActiveAct(i),
        onEnterBack: () => setActiveAct(i),
      })

      gsap.fromTo(
        act.querySelectorAll('[data-qa-track]'),
        { opacity: 0, y: 24 },
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: 'power2.out',
          scrollTrigger: { trigger: act, start: 'top 75%', end: 'top 40%', scrub: false, toggleActions: 'play none none reverse' },
        }
      )
    })
  })

  return () => ctx.revert()
}
"""

APP_JSX = """import { Canvas } from '@react-three/fiber'
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
          <h1 data-qa-track>__TITLE__</h1>
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
"""

README = """# __NAME__

Generated by the claude3Dscroll skill (by Cognivexa) — blended timeline
control: React Three Fiber for the scene, GSAP ScrollTrigger for the
sequencing, Zustand tying them to an HTML overlay.

## Run it

```bash
npm install
npm run dev
```

## Layout

- `src/store/scene.js` - the one shared source of truth between the R3F
  scene and the scroll-driven GSAP timelines. Don't let two systems write
  the same property - see the skill's `references/pitfalls.md`.
- `src/animations/scroll.js` - ScrollTrigger setup, scoped with
  `gsap.context()` so unmount cleanup doesn't leave duplicate triggers
  behind (matters under React StrictMode).
- `src/components/Scene.jsx` - the R3F scene; reads `scrollProgress` from
  the store inside its `useFrame` loop instead of being driven directly by
  GSAP, so ownership of that property stays unambiguous.

## Where to take it from here

1. Settle on a page grammar and sketch a feeling arc before adding more
   acts - see the skill's `references/design-craft.md`.
2. Swap the placeholder copy, object, and palette (`--accent` in
   `src/index.css`) for the real content.
3. If the scene needs to represent a real product, character, or prop,
   replace the placeholder icosahedron with a sourced glTF model instead
   of building it from primitives - see the skill's
   `references/asset-sourcing.md` for free, commercial-use sources (models,
   HDRIs, textures, stock video) and the loading pattern.
4. Design in your signature interaction.
5. Once the page has real content, run the skill's
   `scripts/verify_scroll_page.mjs` against `http://localhost:5173` and
   fix whatever it flags before calling the build done.
"""

GITIGNORE = """node_modules
dist
.DS_Store
"""


def substitute(template: str, name: str, title: str, accent: str) -> str:
    return (
        template
        .replace("__NAME__", name)
        .replace("__TITLE__", title)
        .replace("__ACCENT__", accent)
    )


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path}")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a claude3Dscroll starter project.")
    parser.add_argument("name", help="Project name (used in package.json and page title)")
    parser.add_argument("--dir", default=None, help="Target directory (default: ./<name>)")
    parser.add_argument("--accent", default="#ff6b35", help="Accent color hex (default: #ff6b35)")
    args = parser.parse_args()

    target = Path(args.dir) if args.dir else Path(".") / args.name
    if target.exists() and any(target.iterdir()):
        print(f"Error: {target} already exists and is not empty.", file=sys.stderr)
        sys.exit(1)

    print(f"Scaffolding '{args.name}' into {target.resolve()} ...")

    def sub(t: str) -> str:
        return substitute(t, args.name, args.name, args.accent)

    write(target / "package.json", sub(PACKAGE_JSON))
    write(target / "vite.config.js", VITE_CONFIG)
    write(target / "index.html", sub(INDEX_HTML))
    write(target / ".gitignore", GITIGNORE)
    write(target / "README.md", sub(README))

    src = target / "src"
    write(src / "main.jsx", MAIN_JSX)
    write(src / "App.jsx", sub(APP_JSX))
    write(src / "index.css", sub(INDEX_CSS))
    write(src / "store" / "scene.js", STORE_JS)
    write(src / "components" / "Scene.jsx", sub(SCENE_JSX))
    write(src / "components" / "Loader.jsx", LOADER_JSX)
    write(src / "animations" / "scroll.js", SCROLL_JS)

    print(f"\nDone. Next:\n  cd {target}\n  npm install\n  npm run dev\n")


if __name__ == "__main__":
    main()

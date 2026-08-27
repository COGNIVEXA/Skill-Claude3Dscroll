# Shared State Across Layers

The 3D layer, the timing/animation layer, and the DOM/UI layer all need to agree on certain values. Give each piece of state exactly one owner — never let two libraries both be responsible for writing the same property.

## Zustand as the shared store

Best for anything both the R3F scene and the surrounding page need to read: the current selection, which camera mode is active, the current chapter/act index, whether an intro sequence has finished playing.

```javascript
// store/scene.js
import { create } from 'zustand'

export const useSceneStore = create((set) => ({
  camera: { position: [0, 2, 5], target: [0, 0, 0] },
  objects: {},
  selectedId: null,
  isAnimating: false,

  updateCamera: (updates) => set((state) => ({ camera: { ...state.camera, ...updates } })),
  addObject: (id, object) => set((state) => ({ objects: { ...state.objects, [id]: object } })),
  selectObject: (id) => set({ selectedId: id }),
  setAnimating: (isAnimating) => set({ isAnimating }),
}))
```

Reading it from inside R3F:
```jsx
import { useSceneStore } from '../store/scene'

function Object3D({ id }) {
  const selectedId = useSceneStore((s) => s.selectedId)
  const selectObject = useSceneStore((s) => s.selectObject)
  const isSelected = selectedId === id
  return (
    <mesh onClick={() => selectObject(id)}>
      <boxGeometry />
      <meshStandardMaterial color={isSelected ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
```

The same read works identically from a plain HTML component outside the Canvas — that's the whole point of routing shared state through Zustand: it doesn't matter whether the reader lives inside the R3F tree or outside it.

## Ownership rules

1. **One writer per property.** If GSAP is tweening `mesh.position`, nothing else — not React Spring, not a `useFrame` callback, not Motion — should also be writing to `mesh.position` in that same window of time. If two systems genuinely need to affect the same object, split the properties between them (GSAP takes position, React Spring takes scale).
2. **Direct mutation of a Three.js object doesn't notify React.** Setting `mesh.position.x = 5` imperatively leaves React's world unaware. If that value also needs to show up in HTML (a readout, a progress bar), push it into the store explicitly right after the mutation, or drive the value from the store to begin with.
3. **Derive values instead of duplicating them.** If several parts of the UI need to know "is the intro still playing", store that boolean once and read it from everywhere, rather than letting each consumer keep its own copy that can drift.
4. **Scroll position / act index belongs in the store, not scattered across component-local state.** Nav indicators, a progress bar, and the 3D scene itself should all read the same store field, written once by whatever is actually driving scroll (a ScrollTrigger `onUpdate`, or Drei's `useScroll().offset`).

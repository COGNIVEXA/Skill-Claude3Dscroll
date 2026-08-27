import { create } from 'zustand'

export const useSceneStore = create((set) => ({
  scrollProgress: 0,
  activeAct: 0,
  isReady: false,

  setScrollProgress: (scrollProgress) => set({ scrollProgress }),
  setActiveAct: (activeAct) => set({ activeAct }),
  setReady: (isReady) => set({ isReady }),
}))

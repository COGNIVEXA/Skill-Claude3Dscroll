import gsap from 'gsap'
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

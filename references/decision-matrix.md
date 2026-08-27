# Choosing a Combination

| Situation | Combination to reach for | Why |
|---|---|---|
| Marketing/landing page, scroll-driven 3D, cinematic single-take | Three.js + GSAP + a React UI shell | GSAP is built for scroll choreography; imperative Three.js keeps full control over camera and materials |
| React app with an interactive 3D product viewer | R3F + Motion | Declarative and state-driven — matches how product UI is usually already modeled |
| Precisely timed multi-step sequences (chaptered narrative) | R3F + GSAP timelines | GSAP's timeline control layered onto an R3F component tree |
| Interaction that should feel physically handled (drag, momentum, a signature move) | R3F + React Spring | Spring physics reads as natural for gesture-driven response |
| Heavy particle systems / continuous-world backdrops | Three.js + GSAP | Imperative control plus `InstancedMesh` keeps per-frame overhead low |
| Fast prototyping, quick iteration | R3F + Drei + Motion | High-level helpers get to a working first pass fastest |
| Game-like experience with real physics | R3F + React Spring + a physics engine (Rapier/Cannon) | The physics engine handles simulation; springs handle UI-facing feedback |

## Grammar-to-stack starting point

Full grammar definitions live in `design-craft.md`. As a starting lean, not a rule:

| Grammar | Typical combination |
|---|---|
| Cinematic single-take | Three.js + GSAP (Architecture 1) |
| Chaptered narrative | R3F + GSAP timelines (Architecture 3) |
| Live reactive surface | R3F + React Spring (Architecture 4), pointer-reactive |
| Continuous 3D world | Three.js + GSAP (Architecture 1), one persistent stage |
| Type-led poster | R3F or plain DOM + Motion — 3D is often a light accent here, not the lead |
| Curated gallery | R3F + Motion (Architecture 2) |
| Dual-pane stage | R3F + Motion (Architecture 2), two panes kept in sync |
| Hard-cut sequence | R3F + GSAP timelines (Architecture 3), deliberate section cuts |

The real driver is what the signature interaction needs — treat this table as a default, not a constraint.

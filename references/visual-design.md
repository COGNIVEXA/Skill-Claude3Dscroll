# Visual Design for the 3D Scene Itself

`design-craft.md` sets the page-level design bar — grammar, typography, color roles, spacing, the "don't ship this" list. This file is narrower: it's about directing the **3D scene as a shot**, the way a cinematographer or technical art director would, independent of the HTML layer around it. Read this specifically when composing a hero scene, a product shot, or any moment where the 3D content itself is the focal point.

## Think in shots, not scenes

Before placing a single object, decide what the camera actually frames at the key moments (hero load, the top of each chapter, the ending frame — `animation-system.md` has the shot vocabulary). A scene built by adding objects until it "looks full," then pointing a camera at it, tends to produce cluttered, undirected compositions. Build toward the frame instead: place the camera (or its first keyframe) early, and add geometry to serve what that frame needs.

## Composition

- **Rule of thirds, in 3D.** Position the subject's visual weight off-center in the frame — dead-center framing reads as a product-catalog thumbnail, not a directed shot, unless perfect symmetry is the deliberate point (an architectural facade, a formal portrait moment).
- **Leave negative space with a job.** Empty frame area isn't wasted if it's where a headline or UI element will sit in the HTML layer above it — compose the 3D shot with that overlay in mind, not as if the canvas were the entire deliverable.
- **Depth staging.** A flat-feeling scene usually has everything at roughly the same distance from camera. Stage in three rough layers — near (slightly out of focus or cropped, adds immediacy), mid (the actual subject, in focus), far (environment/backdrop, softer, less detailed) — even a simple product shot benefits from *something* in the background layer rather than a flat void or a single-color background.
- **One focal point per frame.** If two objects compete for attention at the same moment, the shot doesn't have a point. Use focus (depth of field), light, or motion to make it unambiguous which element the visitor's eye should land on first.

## Light as the primary compositional tool

Light does more to sell "premium" than geometry detail does — see `asset-sourcing.md`'s renderer baseline for the mechanical setup (real HDRI, tone mapping, post-processing). On top of that mechanical floor:
- **Key light direction defines the read of a surface.** A light from directly behind the camera flattens form; a light from the side or above-and-behind reveals surface detail through shadow.
- **Use light to guide the eye to the focal point**, not just to make the scene visible — a rim/fresnel highlight (`shaders.md`) or a brighter key on the subject with a dimmer environment does more compositional work than uniform even lighting.
- **Let some of the frame go dark.** A scene lit evenly everywhere has no hierarchy — real depth and drama come from contrast between lit and unlit areas, not from maximizing visibility of every surface.

## Camera lens language

Covered in choreography terms in `animation-system.md`; as a compositional choice specifically:
- Narrow FOV (30–40°) compresses depth, flattens the background toward the subject, reads as deliberate/telephoto/premium — good for a hero product or portrait-style character shot.
- Wide FOV (60–75°) exaggerates depth and scale, suits establishing shots and fly-throughs where spatial context is the point, but can distort a close subject unflatteringly if used for a tight product shot.
- Depth of field (a shallow focus with the subject sharp and background/foreground soft) is one of the highest-leverage single additions for making a 3D render read as an actual photograph rather than a rendered scene — use it deliberately on hero/focal moments, not uniformly across every shot (it costs render budget and, applied everywhere, stops meaning anything).

## Color in the 3D scene

Cross-reference `design-craft.md`'s six-roles-plus-accent system for the page overall — the 3D scene's own palette should read as part of that system, not as an independent decision:
- The environment/HDRI choice sets ambient color temperature for the whole scene — a warm studio HDRI vs a cool overcast one shifts everything downstream, including how accurately materials read. Pick the HDRI to match the page's established palette, not by default.
- Reserve the page's accent color for the one element that should carry it in the 3D scene too (a rim light, a single glowing element, a material accent) — an accent color smeared across many objects in the scene stops functioning as an accent.
- Material roughness/metalness affects perceived color as much as the base color does — a highly reflective surface picks up the environment's colors more than its own albedo; account for this rather than fighting it by over-saturating the base color.

## Avoiding generic "AI 3D" clichés

A list of defaults that read as generic/templated specifically in the 3D-scene context (`design-craft.md`'s "don't ship this" list covers the page-level equivalents):
- A giant glowing/wireframe sphere as a default hero centerpiece with no connection to the actual subject matter.
- Excessive floating particles with no compositional or narrative reason for them to be there.
- Pure black void backgrounds as a default rather than a deliberate choice — an actual environment (even a subtle gradient/HDRI) almost always reads as more considered.
- A default `OrbitControls` free-spin with no authored camera path — a visitor left to "look around" a scene with no direction rarely lands on a good frame on their own.
- Uniform, shadowless, flat lighting on every object at the same brightness — the fastest way to make a scene look like an early WebGL demo rather than a render.
- Stock low-poly primitives standing in for a real product/subject (see `asset-sourcing.md`'s rule on sourcing real assets instead).

None of these are permanently banned — a deliberately minimal/abstract grammar can use a sculptural primitive-based centerpiece on purpose (`design-craft.md` covers when that's the right call). The distinction is whether the choice serves the specific brief or is just the path of least resistance.

## A quick self-check before calling a hero frame directed

- Does the eye land on one clear focal point within the first second of seeing this frame?
- Is there a near/mid/far depth read, or does everything sit at roughly the same distance from camera?
- Does the lighting create real contrast (lit vs. unlit areas), or is the scene evenly lit everywhere?
- Does the 3D scene's color temperature/accent usage match the page's established palette from `design-craft.md`, rather than being decided independently?
- If a person were shown only this one frame with no context, would it read as a deliberate shot — or as "a 3D model on a webpage"?

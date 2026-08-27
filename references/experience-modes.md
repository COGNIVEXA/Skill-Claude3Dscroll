# Specialized Experience Modes

Domain-specific scene/interaction vocabulary for three recurring project types. These aren't separate architectures — they still run on the combinations in `decision-matrix.md`/`architecture-patterns.md` and the same scroll/camera/animation systems (`scroll-animation.md`, `animation-system.md`); this file is the domain checklist of what such a build typically needs to plan for, so nothing common to the category gets missed. Treat every list here as a menu to select from against the actual brief, not a required feature set — a small school site doesn't need every room in the campus list.

## Virtual campus / school / university tours

**Common scenes:** exterior/campus establishing shot, entrance, reception, classrooms, science lab, computer lab, library, cafeteria, playground/sports ground, auditorium, art room, transport/bus area.

**Common interactions:**
- Guided campus tour — an authored camera path (`animation-system.md`'s fly-through shot) through the scenes above, paced by scroll or by a chapter-select UI.
- Building/room hotspots that jump the camera to a specific interior (`accessibility.md` covers making these keyboard-reachable).
- Animated students/teachers as ambient life in the scene (`animation-system.md`'s Idle/Walk loops) — keep the count device-tiered (`responsive-3d.md`), ambient characters are usually the first thing to cut on low-power devices.
- A campus map (2D or a simplified 3D overview) as a navigation aid and a non-spatial way to jump between areas — this doubles as the alternate interaction path `accessibility.md` asks for.
- Admissions/enrollment call-to-action woven into the tour rather than only at the end — the HTML layer should carry this, not the 3D scene alone (`accessibility.md`'s critical-content rule).
- Faculty cards, event listings, facility descriptions — real HTML content anchored to or triggered by tour position, not baked into the 3D scene as unreadable in-world text.

**Planning notes:**
- A full multi-building interior tour is a large asset/scope commitment — confirm with the requester whether the brief actually needs interior room modeling or whether an exterior campus + hotspot-triggered photo/video panels per facility meets the goal at a fraction of the asset budget. Don't default to the largest interpretation.
- Scale and pacing matter more than density here — a tour that rushes through every room reads worse than one that lingers on fewer, better-composed spaces.

## Product showcase

**Common interactions:**
- Product rotation (either free-drag via a spring-driven control, `architecture-patterns.md`'s Architecture 4, or scroll-driven auto-rotate).
- Component/part highlighting — a hotspot per feature, camera pushing in slightly and a callout appearing in the HTML layer.
- Exploded view — parts separating along their own axis as a scroll-scrubbed or drag-driven sequence; drive with normalized progress (`scroll-animation.md`) rather than raw scroll pixels so the assembly/disassembly always completes at a predictable point.
- Material/color variant switching — swap `material.color`/a texture map on click rather than swapping the whole model, to keep it instant and cheap.
- Close-up camera sequences on specific features, paired with real macro-detail textures (`asset-sourcing.md`) — a close-up on a low-resolution texture is the fastest way to break the illusion on exactly the shot meant to sell the product.
- Product comparison — two instances side by side or a slider/wipe transition between them; keep camera framing identical across compared variants so the comparison itself is the variable, not the shot.

**Planning notes:**
- This is the mode where sourcing (or commissioning) an accurate, well-textured model matters most — see `asset-sourcing.md`'s rule against building a real product from primitives. A product showcase is usually the worst place to compromise on asset quality even if other parts of the site can.
- Depth of field and a narrower FOV (`visual-design.md`) do disproportionate work here — a product shot benefits from photographic camera language more than most other page types.

## Architectural / real-estate walkthroughs

**Common scenes:** exterior approach, entry, room-by-room interior sequence, a rooftop/aerial overview, floor-plan-linked navigation.

**Common interactions:**
- Full walkthrough — an authored path through connected interior spaces (`animation-system.md`'s fly-through/room-transition shots), scroll- or button-paced.
- Floor switching — swap which level's geometry is visible/active, usually with a cross-fade or a vertical camera transition rather than an instant cut.
- Room hotspots that jump to and orient the camera within a specific space.
- Material/finish selectors — swap surface materials (flooring, cabinetry, paint) live, the architectural equivalent of the product showcase's variant switching.
- Section/cutaway reveals — a scroll- or toggle-driven clipping plane or an animated wall/roof removal exposing the interior structure; the shader transition-mask pattern in `shaders.md` is one way to implement a dissolve-style reveal, though a simple animated visibility/position toggle is often enough.
- A floor-plan overlay (2D, in the HTML layer) synced to the current 3D camera position — orients the visitor and, again, doubles as a non-spatial navigation path for accessibility.

**Planning notes:**
- Lighting is the single highest-leverage element for architectural realism — real HDRI environment lighting plus baked/contact shadows under furniture reads dramatically more convincing than real-time shadows alone at typical web performance budgets (`asset-sourcing.md`, `performance.md`).
- Scale accuracy matters more here than almost any other mode — a walkthrough where door heights, ceiling heights, or furniture proportions are visibly off breaks the sense of a real, inhabitable space immediately. Confirm real-world dimensions from source CAD/Blender files rather than eyeballing scale at export.
- Confirm early whether the brief needs true photorealism (closer to `asset-sourcing.md`'s full renderer/post-processing baseline, heavier asset budget) or a stylized/schematic walkthrough (lower asset cost, faster to build, often equally or more effective for an early-stage concept pitch) — this decision should happen in Phase 1, not be discovered mid-build.

# claude3Dscroll

**A Claude Code skill for building scroll-driven, animated 3D websites — by [Cognivexa](https://github.com/Cognivexa).**

![License](https://img.shields.io/github/license/Cognivexa/Skill-Claude3Dscroll?style=flat-square&color=444)
![Last Commit](https://img.shields.io/github/last-commit/Cognivexa/Skill-Claude3Dscroll?style=flat-square&color=444)
![Made for Claude Code](https://img.shields.io/badge/Made%20for-Claude%20Code-D97757?style=flat-square)

It teaches Claude how to combine Three.js, GSAP ScrollTrigger, React Three Fiber, Motion, and React Spring into one working build, holds the result to a concrete design bar (page grammar, typography, color, depth, a required signature interaction), sources real HD assets instead of flat placeholder shapes, and checks its own scroll behavior in a headless browser instead of just asserting the page works. Full detail lives in [`SKILL.md`](SKILL.md) — this document covers installing and running it.

## Built on

<p>
  <a href="https://threejs.org/"><img alt="Three.js" src="https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=three.js&logoColor=white"></a>
  <a href="https://gsap.com/"><img alt="GSAP" src="https://img.shields.io/badge/GSAP-88CE02?style=for-the-badge&logo=greensock&logoColor=white"></a>
  <a href="https://docs.pmnd.rs/react-three-fiber"><img alt="React Three Fiber" src="https://img.shields.io/badge/React%20Three%20Fiber-61DAFB?style=for-the-badge&logo=react&logoColor=black"></a>
  <a href="https://motion.dev/"><img alt="Motion" src="https://img.shields.io/badge/Motion-0055FF?style=for-the-badge&logo=framer&logoColor=white"></a>
  <a href="https://www.react-spring.dev/"><img alt="React Spring" src="https://img.shields.io/badge/React%20Spring-FF4154?style=for-the-badge&logoColor=white"></a>
</p>

## Generated projects run on

<p>
  <a href="https://vitejs.dev/"><img alt="Vite" src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white"></a>
  <a href="https://react.dev/"><img alt="React" src="https://img.shields.io/badge/React-149ECA?style=for-the-badge&logo=react&logoColor=white"></a>
  <a href="https://zustand-demo.pmnd.rs/"><img alt="Zustand" src="https://img.shields.io/badge/Zustand-433E38?style=for-the-badge&logoColor=white"></a>
  <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"></a>
  <a href="https://nodejs.org/"><img alt="Node.js" src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white"></a>
</p>

## Tooling

<p>
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://playwright.dev/"><img alt="Playwright" src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white"></a>
  <a href="https://www.npmjs.com/"><img alt="npm" src="https://img.shields.io/badge/npm-CB3837?style=for-the-badge&logo=npm&logoColor=white"></a>
  <a href="https://git-scm.com/"><img alt="Git" src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"></a>
</p>

## What's in this repository

```
.
├── SKILL.md                  the instructions Claude Code loads
├── references/
│   ├── architecture-patterns.md    four integration architectures, with code
│   ├── integration-recipes.md      scroll cameras, gesture handling, state sync
│   ├── state-management.md         Zustand as the shared 3D/DOM state layer
│   ├── performance.md              render-loop discipline, disposal, budgets
│   ├── pitfalls.md                 recurring mistakes and how to avoid them
│   ├── decision-matrix.md          which combination fits which use case
│   ├── design-craft.md             the design bar — grammar, type, color, depth,
│   │                                 the "don't ship this" list, differentiation check
│   ├── qa-verification.md          reading and acting on the verification report
│   ├── asset-sourcing.md           free, commercial-use 3D models, HDRIs, textures,
│   │                                 and video, plus the renderer/post-processing
│   │                                 baseline that keeps a scene from looking flat
│   ├── threejs-r3f.md              core Three.js/R3F engineering patterns
│   ├── scroll-animation.md         the scroll-driver system: one scroll source,
│   │                                 damped camera, section timelines
│   ├── animation-system.md         Mixamo/character animation, camera choreography
│   ├── asset-licensing.md          deep per-source licensing rules + manifest format
│   ├── shaders.md                  when GLSL is justified, plus effect recipes
│   ├── responsive-3d.md            device-tier policy, adaptive quality, fallback
│   ├── accessibility.md            reduced motion, keyboard, semantic HTML, ARIA
│   ├── visual-design.md            directing the 3D scene itself as a shot
│   ├── debugging.md                systematic symptom-first troubleshooting
│   ├── quality-checklist.md        the consolidated pre-ship checklist
│   └── experience-modes.md         campus/school tours, product showcases,
│                                     architectural walkthroughs
├── scripts/
│   ├── scaffold_project.py         generates a working starter project
│   ├── verify_scroll_page.mjs      headless-browser scroll verification (Playwright)
│   └── audit_assets.py             scans asset sizes, flags oversized files,
│                                     can emit a starter ASSET_LICENSES.md
└── assets/
    └── starter-unified/            a checked-in copy of what the scaffold produces
```

## Requirements

- [Claude Code](https://claude.com/claude-code) — CLI, Desktop app (Mac/Windows), or IDE extension
- Python 3.9+ (used by `scaffold_project.py`)
- Node.js 18+ and npm (used by every generated project, and by `verify_scroll_page.mjs`)
- Git (for the clone-based install method below)

## Installing the skill

Claude Code — CLI, Desktop app, and IDE extensions alike — loads skills from the same two locations on disk. The install steps are identical across all of them; only the shell commands differ by OS. The skill folder must sit **directly** inside `skills/` — `skills/claude3Dscroll/SKILL.md`, not nested inside an extra wrapping folder.

| Location | Scope |
|---|---|
| `<project>/.claude/skills/claude3Dscroll/` | Available only inside that one project |
| `~/.claude/skills/claude3Dscroll/` (`%USERPROFILE%\.claude\skills\` on Windows) | Available in every project on your machine |

### Claude Code — terminal / CLI

**Windows (PowerShell), project-scoped:**
```powershell
cd "<your-project-root>"
New-Item -ItemType Directory -Force -Path ".claude\skills" | Out-Null
git clone https://github.com/Cognivexa/Skill-Claude3Dscroll ".claude\skills\claude3Dscroll"
```

**Windows (PowerShell), global — every project:**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
git clone https://github.com/Cognivexa/Skill-Claude3Dscroll "$env:USERPROFILE\.claude\skills\claude3Dscroll"
```

**macOS / Linux, project-scoped:**
```bash
cd "<your-project-root>"
mkdir -p .claude/skills
git clone https://github.com/Cognivexa/Skill-Claude3Dscroll .claude/skills/claude3Dscroll
```

**macOS / Linux, global — every project:**
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Cognivexa/Skill-Claude3Dscroll ~/.claude/skills/claude3Dscroll
```

Then, in the same terminal, start (or restart) a session in your project:
```bash
cd "<your-project-root>"
claude
```

### Claude Code — Desktop app (Mac / Windows)

The Desktop app reads skills from the exact same `.claude/skills` locations as the CLI — it doesn't have a separate install mechanism. Run the same clone command as above in Terminal (Mac) or PowerShell (Windows), then:

1. Open the target project as a workspace in the Claude Code Desktop app (or, if it's already open, close and reopen it — like the CLI, the skill list loads once per session).
2. Confirm it loaded: open the chat and type `/` — `claude3Dscroll` should appear in the list.

### No git? Download a ZIP instead

1. On this repo's GitHub page, use **Code → Download ZIP**.
2. Extract it, and rename the extracted folder (likely `Skill-Claude3Dscroll-main`) to `claude3Dscroll`.
3. Move that folder into `.claude/skills/` — project-scoped or global, per the table above — in Finder, File Explorer, or your terminal of choice.

### Verify the install

```bash
ls .claude/skills/claude3Dscroll
```
You should see `SKILL.md`, `references`, `scripts`, and `assets` listed directly.

## Using it

Two ways to invoke it, in the CLI or the Desktop app alike:
- **Explicitly:** `/claude3Dscroll build a scroll-driven 3D landing page for <your idea>`
- **Implicitly:** describe the task in plain language — e.g. "build me an animated 3D product landing page with scroll effects." The skill's description is written to match that kind of request on its own.

Once it's running, Claude works through the process `SKILL.md` defines: scope the request and match effort to it (a quick ask gets a lean pass, not the full process every time), pick one page grammar and library combination, scaffold a real project, build content against the chosen integration architecture, source real assets rather than hand-building products out of primitives, hold the result to the design bar, verify it in a headless browser, and pass on performance/correctness — reporting what's left rather than looping indefinitely if something doesn't come out clean.

## Trying the tooling without Claude Code

Both scripts work standalone, so the skill's tooling can be sanity-checked before ever invoking it through Claude:

```bash
cd claude3Dscroll/scripts
python scaffold_project.py demo-site --dir ../../demo-site --accent "#d98a4b"
cd ../../demo-site
npm install
npm run dev
```

With the dev server running, in another terminal:
```bash
npm install -D playwright
npx playwright install chromium
cp ../claude3Dscroll/scripts/verify_scroll_page.mjs .
node verify_scroll_page.mjs http://localhost:5173 --steps 20 --out qa-report
```
Open `qa-report/report.html` in a browser for the scroll contact sheet and anything it flagged.

## License

See [`LICENSE`](LICENSE).

---

<sub>Developed by <a href="https://github.com/Cognivexa">Cognivexa</a>.</sub>

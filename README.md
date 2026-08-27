# claude3Dscroll

A Claude Code skill for building scroll-driven, animated 3D websites, developed by **Cognivexa**.

It teaches Claude how to combine Three.js, GSAP ScrollTrigger, React Three Fiber, Motion (Framer Motion), and React Spring into a working build — and holds the result to a concrete design bar (page grammar, type, color, depth, a required signature interaction) instead of settling for a generic scroll-animation demo. Full detail lives in [`SKILL.md`](SKILL.md); this document only covers getting it installed and running.

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
│   └── asset-sourcing.md           free, commercial-use 3D models, HDRIs, textures,
│                                     and video, plus the renderer/post-processing
│                                     baseline that keeps a scene from looking flat
├── scripts/
│   ├── scaffold_project.py         generates a working starter project
│   └── verify_scroll_page.mjs      headless-browser scroll verification (Playwright)
└── assets/
    └── starter-unified/            a checked-in copy of what the scaffold produces
```

## Requirements

- [Claude Code](https://claude.com/claude-code) installed and working
- Python 3.9+ (used by `scaffold_project.py`)
- Node.js 18+ and npm (used by every generated project, and by `verify_scroll_page.mjs`)

## Installing

Claude Code only auto-loads skills placed in one of two locations, and the skill folder must sit **directly** inside `skills\` — `skills\claude3Dscroll\SKILL.md`, not nested inside an extra wrapping folder.

| Location | Scope |
|---|---|
| `<project>\.claude\skills\claude3Dscroll\` | Available only inside that one project |
| `%USERPROFILE%\.claude\skills\claude3Dscroll\` | Available in every project on your machine |

### Clone directly into place

Cloning into a folder named `claude3Dscroll` gets the layout right in one step — PowerShell, for a single project:
```powershell
cd "<your-project-root>"
New-Item -ItemType Directory -Force -Path ".claude\skills" | Out-Null
git clone https://github.com/Cognivexa/Skill-Claude3Dscroll ".claude\skills\claude3Dscroll"
```

Or globally, for every project on your machine:
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
git clone https://github.com/Cognivexa/Skill-Claude3Dscroll "$env:USERPROFILE\.claude\skills\claude3Dscroll"
```

### Or download a ZIP instead of using git

1. On this repo's GitHub page, use **Code → Download ZIP**.
2. Extract it, and rename the extracted folder (likely `Skill-Claude3Dscroll-main`) to `claude3Dscroll`.
3. Move that folder into `.claude\skills\` — project-scoped or global, per the table above.

Verify the layout afterward:
```powershell
dir ".claude\skills\claude3Dscroll"
```
You should see `SKILL.md`, `references`, `scripts`, and `assets` listed directly.

## Loading it into Claude Code

Claude Code reads the skill list once, at session start — installing the skill while a session is already running won't make it appear in that same session.

1. Start (or restart) a Claude Code session with the target project as the working directory:
   ```powershell
   cd "<your-project-root>"
   claude
   ```
2. Confirm it loaded — type `/` and look for `claude3Dscroll` in the list, or ask "what skills do you have available?"

## Using it

Two ways to invoke it:
- **Explicitly:** `/claude3Dscroll build a scroll-driven 3D landing page for <your idea>`
- **Implicitly:** describe the task in plain language — e.g. "build me an animated 3D product landing page with scroll effects." The skill's description is written to match that kind of request on its own.

Once it's running, Claude works through the process `SKILL.md` defines: scope the request (and match effort to it — a quick ask gets a lean pass, not the full process every time), pick one page grammar and library combination, scaffold a real project, build content against the chosen integration architecture, source real assets rather than hand-building products out of primitives, hold the result to the design bar, verify it in a headless browser, and pass on performance/correctness — reporting what's left rather than looping indefinitely if something doesn't come out clean.

## Trying the tooling without Claude Code

Both scripts work standalone, so the skill's tooling can be sanity-checked before ever invoking it through Claude:

```powershell
cd claude3Dscroll\scripts
python scaffold_project.py demo-site --dir ..\..\demo-site --accent "#d98a4b"
cd ..\..\demo-site
npm install
npm run dev
```

With the dev server running, in another terminal:
```powershell
npm install -D playwright
npx playwright install chromium
copy <path-to>\claude3Dscroll\scripts\verify_scroll_page.mjs .
node verify_scroll_page.mjs http://localhost:5173 --steps 20 --out qa-report
```
Open `qa-report\report.html` in a browser for the scroll contact sheet and anything it flagged.

## License

See [`LICENSE`](LICENSE).

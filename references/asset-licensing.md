# Asset Licensing — the Deep Reference

`asset-sourcing.md` covers *where* to find real, commercial-safe assets fast and lists the always-safe defaults. This file covers licensing in depth: per-source rules, red flags, the manifest format, and how to handle a source that isn't uniformly safe. Read this whenever a project pulls from a source beyond the always-CC0 defaults, or whenever "is this actually okay to ship commercially" needs a real answer instead of an assumption.

## The rule Claude should never break

**Do not guess.** If an asset's license can't be confirmed as covering the intended use, don't use it — substitute a confirmed-safe alternative from `asset-sourcing.md`, generate a primitive-based placeholder and say so explicitly, or ask the requester. "Free to download" is not the same claim as "free for commercial use," "no attribution required," or "free to modify" — a source can be free on one axis and restricted on another.

## License types, in plain terms

| License | Commercial use | Attribution | Modification | Notes |
|---|---|---|---|---|
| CC0 / Public Domain | Yes | No | Yes | The only license that needs zero bookkeeping. Prefer it whenever an equally good CC0 option exists. |
| CC-BY | Yes | **Yes, required** | Yes | Attribution has to actually ship somewhere (credits page/footer/about) — "we'll add it later" is how this gets missed. |
| CC-BY-SA | Yes | Yes | Yes, but derivative must carry the same license | Rarely appropriate for a client site's bundled assets — the share-alike clause can be read as extending to the derivative work. Avoid unless the specific use is well understood. |
| CC-BY-NC | **No** | — | — | Non-commercial only. Do not use on any site built for a business, product, or paid engagement, including portfolio pieces built for a paying client. |
| "Royalty-free" (stock sites) | Usually, within the platform's specific terms | Platform-dependent | Platform-dependent | Not a license name by itself — read the specific platform's license page; "royalty-free" only means no per-use royalty, not unrestricted use. |
| "Free for personal use" | **No** | — | — | A common trap on font/asset sites. If a license says "personal use" anywhere, treat it as blocked for any commercial or client build. |
| Platform-specific EULA (Mixamo, Sketchfab per-model, BlenderKit per-asset) | Varies per asset | Varies per asset | Varies per asset | Read the specific asset's page — these platforms host mixed licensing, sometimes within the same category. |

## Per-source guidance

- **Poly Haven** (models, HDRIs, textures) — everything is CC0. No per-asset check needed; this is the always-safe default.
- **ambientCG** (PBR textures) — CC0 throughout, same as Poly Haven.
- **Quaternius** — CC0 low-poly/stylized packs. Some packs ask for an optional (not required) attribution/support link — check the specific pack's readme, but commercial use itself is unrestricted.
- **Khronos glTF-Sample-Assets** — permissively licensed per-model (mostly CC0/Apache/CC-BY); good for prototyping and PBR-pipeline testing, but confirm the specific model's license file before it ends up in a shipped build rather than assuming it's identical to Poly Haven's blanket CC0.
- **Adobe Mixamo** — free to use, including commercially, under Adobe's Mixamo/Creative Cloud terms, for characters and animations exported from the service. Confirm current terms on Adobe's site before a commercial ship, since terms are Adobe's to change; this reference is not a substitute for reading them at the time of use.
- **Sketchfab** — **mixed licensing, always check the individual model.** Filter search to CC0 or CC-BY explicitly, then open the specific model's license tab before downloading — Sketchfab hosts everything from CC0 to fully proprietary "Standard" (all rights reserved, download for reference only, not for redistribution or use in a shipped product) on the same search results page.
- **BlenderKit** — mixed; the marketplace has both free-tier assets with specific per-asset commercial terms and paid assets. Check the individual asset's license before use — do not assume free-tier implies unrestricted commercial use.
- **Pexels (photos/video)** — free, no attribution required, commercial use permitted under the Pexels license; still avoid using an identifiable person's likeness in a way that implies endorsement without a model release.
- **Mixkit (video)** — free, no attribution required, per Mixkit's license.
- **Coverr (video)** — mostly attribution-free, but check the specific clip's license note; Coverr has had mixed terms across its catalog historically.
- **Pixabay** — check the current license terms at time of use; Pixabay's license terms have changed over time and some categories carry additional restrictions.
- **LottieFiles** — mixed; many community-uploaded animations are free for commercial use, some carry attribution requirements or are restricted to LottieFiles' own preview/non-commercial use. Check the individual file's license before embedding it in a shipped build.
- **Google Fonts** — open licenses (mostly OFL, some Apache), safe for commercial use, no per-font check typically needed, but the font's own `OFL.txt` in its Google Fonts repo entry is the source of truth if a specific font's terms matter for the project (e.g. embedding vs. just linking).

## Red flags — reject rather than guess

- A license page that's missing, broken, or only in a language the check can't confirm.
- Terms that mention "personal," "non-commercial," "educational," or "evaluation" use anywhere, with no separate commercial license offered.
- A marketplace listing with no visible license at all (common on aggregator sites that re-host content without preserving the original license).
- Any asset carrying a real person's identifiable likeness, voice, or name without a clear release — this applies independent of the platform's stated license, since likeness rights are separate from copyright licensing.
- A "free" asset bundled inside a paid pack/plugin where only the pack as a whole is licensed, not the individual asset in isolation.

If any of the above applies, substitute a confirmed-safe asset (`asset-sourcing.md`'s always-CC0 list) rather than proceeding on an assumption.

## The asset manifest

For any commercial project pulling in external assets, keep `ASSET_LICENSES.md` at the project root, updated as assets are added — not written once at the end from memory:

```markdown
# Asset Manifest

| Asset | Source | URL | Creator | License | Commercial Use | Attribution Required | Modified | Notes |
|---|---|---|---|---|---|---|---|---|
| Hero sneaker model | Poly Haven | https://polyhaven.com/a/... | Poly Haven | CC0 | Yes | No | Retextured accent color | — |
| Campus building HDRI | Poly Haven | https://polyhaven.com/a/... | Poly Haven | CC0 | Yes | No | No | — |
| Idle/Walk/Run clips | Mixamo | mixamo.com | Adobe Mixamo | Mixamo license | Yes | No | Combined into one GLB | Confirm current Adobe terms before ship |
| Lobby ambience clip | Pexels Videos | https://pexels.com/video/... | (creator name) | Pexels License | Yes | No | Compressed to WebM | — |
```
`scripts/audit_assets.py` can scan a project's asset folders and emit a starter version of this table (empty License/Source columns to fill in) alongside its size report — see the script's own `--manifest` flag.

## When the requester supplies their own assets

If the project brief includes assets the requester already owns or has licensed (a brand's own product scans, stock footage they've purchased, a font from their brand kit), those override this document entirely — record them in the manifest as "requester-supplied, license held by client" and don't re-research licensing for them. The one thing worth confirming is scope: a license purchased for print or for a single prior campaign doesn't automatically cover a new web build; ask if it's ambiguous rather than assuming.

# Reading the Verification Report

`scripts/verify_scroll_page.mjs` drives a real headless Chromium browser through a page's full scroll range and reports on what actually happens, rather than trusting that the code should work. This is the mechanism that lets a build check its own output instead of simply asserting the page is good.

## Running it

Needs Node.js and Playwright (`npm i -D playwright` somewhere convenient, then `npx playwright install chromium` once).

```bash
node scripts/verify_scroll_page.mjs http://localhost:5173 --steps 48 --out ./qa-report
```

Flags:
- `--steps N` — number of scroll positions sampled across the full scrollable height (default 40; raise it for very long pages)
- `--out DIR` — where to write the contact sheet and JSON report (default `./qa-report`)
- `--viewport WxH` — viewport to test, e.g. `1440x900` (default) or `390x844` for a mobile pass
- `--wait MS` — settle time after each scroll jump before sampling (default 350ms; raise it if the report is catching animations or video mid-transition)

Run it at least twice per build — once desktop, once mobile. Contrast and dead-scroll problems that don't show up at desktop width often surface once fluid spacing and type collapse down.

## What gets checked

1. **Dead scroll.** At every sampled position, the page is fingerprinted (inline transform/opacity/background-color on tracked elements, plus any video `currentTime`). A run of consecutive positions with an identical fingerprint gets reported as a dead stretch — scroll distance where nothing observable changes. A small dead range right at the very top or bottom (before the first trigger fires, after the last one finishes) is normal; a large one in the middle of the page is not.

2. **Reveals that never fully appear.** Elements meant to fade in (tagged with `data-qa-track`, or matched by common animation patterns) are checked for whether they ever reach `opacity: 1` at any sampled point. If an element's highest observed opacity across the whole pass stays meaningfully below 1, a visitor can never actually see it clearly — flagged as a stuck reveal.

3. **Contrast, computed per line, at the frame it's actually shown against.** For each visible text-bearing element, the script reads the computed foreground color and the effective background behind it (the nearest ancestor with a resolved background, at the sampled frame) and computes the WCAG relative-luminance ratio. It grades against 4.5:1 for normal text and 3:1 for large text (≥24px, or ≥19px bold), reporting the exact frame/scroll position where a failure occurred — a line can pass contrast at one point in a color transition and fail at another.

4. **Frozen scroll-linked video.** Any `<video data-qa-scrub>` element is tracked across the pass: if `scrollY` moved substantially but `video.currentTime` never did, that's flagged as a frozen playhead — visually indistinguishable from a stalled clip, and one of the easiest scroll-video bugs to miss just by watching.

## Reading the output

- `qa-report/report.html` — a contact sheet: a grid of screenshots from every sampled position, with failures annotated at the frame they occurred. Scan it like a film strip — the point is seeing the whole journey at once, not just the hero shot.
- `qa-report/report.json` — the same findings, machine-readable (`deadScrollRanges`, `stuckCues`, `contrastFailures`, `stuckVideo`), useful for a quick pass/fail gate or feeding a follow-up fix pass.

## Responding to findings

- **Dead scroll range** → either give that stretch a job (add motion) or shorten the scroll distance allotted to it (the ScrollTrigger's `end` value, or fewer `pages` in `ScrollControls`).
- **Stuck reveal** → confirm the animation's end state actually targets `opacity: 1` (not a leftover `0.9`), and check that a later trigger isn't overwriting the same property before the first one finishes.
- **Contrast failure** → don't just darken or lighten the text globally; look at the specific reported frame — the failure is often confined to a transition moment (text crossing a lighter patch of a gradient background with no scrim under it). Strengthening or adding an overlay under the text usually beats recoloring it if the background itself has to stay as-is.
- **Frozen video** → confirm `preload="auto"` is set and enough of the file is buffered before scrubbing starts, and that writes to `currentTime` wait for `readyState >= 2` (or the `loadeddata` event) instead of firing before the browser can seek.

Re-run after every fix. A build isn't done until a pass comes back clean, aside from the small expected dead ranges at the very top and bottom.

## Wiring in `data-qa-*` attributes

The script works with no attributes at all — it falls back to sampling headings/paragraphs for contrast and elements with an inline `opacity`/`transform` for the dead-scroll fingerprint — but tagging explicitly sharpens the results:

```html
<h1 data-qa-track>Headline that fades in</h1>
<video data-qa-scrub src="/hero.mp4"></video>
```

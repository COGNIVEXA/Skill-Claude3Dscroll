#!/usr/bin/env node
/**
 * verify_scroll_page.mjs
 *
 * Part of the claude3Dscroll skill (by Cognivexa).
 *
 * Walks a page's entire scroll range in a headless Chromium browser and
 * reports back: stretches of dead scroll, elements that fade in but never
 * reach full opacity, per-line contrast failures computed at the exact
 * frame they occur, and scroll-linked video elements whose playhead never
 * actually advances.
 *
 * Usage:
 *   node verify_scroll_page.mjs <url> [--steps 40] [--out ./qa-report] [--viewport 1440x900] [--wait 350]
 *
 * Requires Playwright: npm i -D playwright && npx playwright install chromium
 */

import { chromium } from 'playwright'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

function parseArgs(argv) {
  const args = { url: null, steps: 40, out: './qa-report', viewport: '1440x900', wait: 350 }
  const rest = []
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--steps') args.steps = parseInt(argv[++i], 10)
    else if (a === '--out') args.out = argv[++i]
    else if (a === '--viewport') args.viewport = argv[++i]
    else if (a === '--wait') args.wait = parseInt(argv[++i], 10)
    else rest.push(a)
  }
  args.url = rest[0]
  return args
}

function relativeLuminance([r, g, b]) {
  const channel = (c) => {
    const s = c / 255
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
  }
  const [rl, gl, bl] = [channel(r), channel(g), channel(b)]
  return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl
}

function contrastRatio(rgbA, rgbB) {
  const lA = relativeLuminance(rgbA)
  const lB = relativeLuminance(rgbB)
  const [lighter, darker] = lA > lB ? [lA, lB] : [lB, lA]
  return (lighter + 0.05) / (darker + 0.05)
}

function parseRgb(str) {
  if (!str) return null
  const m = str.match(/rgba?\(([^)]+)\)/)
  if (!m) return null
  const parts = m[1].split(',').map((s) => parseFloat(s.trim()))
  const [r, g, b, a = 1] = parts
  if (Number.isNaN(r) || Number.isNaN(g) || Number.isNaN(b)) return null
  return { rgb: [r, g, b], a }
}

function pageSampler() {
  function isVisible(el) {
    const rect = el.getBoundingClientRect()
    if (rect.width === 0 || rect.height === 0) return false
    const style = getComputedStyle(el)
    if (style.visibility === 'hidden' || style.display === 'none') return false
    if (parseFloat(style.opacity) <= 0.01) return false
    return rect.bottom > 0 && rect.top < innerHeight && rect.right > 0 && rect.left < innerWidth
  }

  function effectiveBackground(el) {
    let node = el
    while (node && node !== document.documentElement.parentElement) {
      const style = getComputedStyle(node)
      const bg = style.backgroundColor
      if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') return bg
      node = node.parentElement
    }
    return 'rgb(255, 255, 255)'
  }

  // 1. Dead-scroll fingerprint: tracked elements' transform/opacity, plus video currentTime
  const tracked = Array.from(document.querySelectorAll('[data-qa-track], [style*="opacity"], [style*="transform"]'))
  const fingerprint = tracked.slice(0, 200).map((el) => {
    const style = getComputedStyle(el)
    return style.opacity + '|' + style.transform
  }).join(';')

  const videos = Array.from(document.querySelectorAll('video[data-qa-scrub], video')).map((v, i) => ({
    index: i,
    currentTime: v.currentTime,
    hasAttr: v.hasAttribute('data-qa-scrub'),
    readyState: v.readyState,
  }))

  // 2. Cue opacity peaks: elements explicitly marked as tracked
  const cues = Array.from(document.querySelectorAll('[data-qa-track]')).map((el, i) => ({
    index: i,
    id: el.id || el.getAttribute('data-qa-track') || ('cue-' + i),
    opacity: parseFloat(getComputedStyle(el).opacity),
  }))

  // 3. Contrast: visible headings/paragraphs/spans with text content
  const textEls = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, a, li, blockquote'))
    .filter((el) => el.textContent && el.textContent.trim().length > 1 && isVisible(el) && el.children.length <= 2)

  const contrastSamples = textEls.slice(0, 150).map((el) => {
    const style = getComputedStyle(el)
    const rect = el.getBoundingClientRect()
    return {
      text: el.textContent.trim().slice(0, 60),
      selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').filter(Boolean).slice(0, 2).join('.') : ''),
      color: style.color,
      background: effectiveBackground(el),
      fontSize: parseFloat(style.fontSize),
      fontWeight: style.fontWeight,
      top: Math.round(rect.top),
    }
  })

  return { fingerprint, videos, cues, contrastSamples, scrollY: window.scrollY, scrollHeight: document.documentElement.scrollHeight }
}

async function run() {
  const args = parseArgs(process.argv.slice(2))
  if (!args.url) {
    console.error('Usage: node verify_scroll_page.mjs <url> [--steps 40] [--out ./qa-report] [--viewport 1440x900] [--wait 350]')
    process.exit(1)
  }
  const [vw, vh] = args.viewport.split('x').map(Number)
  await mkdir(args.out, { recursive: true })
  const framesDir = path.join(args.out, 'frames')
  await mkdir(framesDir, { recursive: true })

  console.log(`Launching Chromium, viewport ${vw}x${vh} ...`)
  const browser = await chromium.launch()
  const page = await browser.newPage({ viewport: { width: vw, height: vh } })
  await page.goto(args.url, { waitUntil: 'networkidle' })

  const scrollHeight = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)
  const steps = Math.max(2, args.steps)

  const samples = []
  const screenshots = []

  for (let i = 0; i < steps; i++) {
    const y = Math.round((scrollHeight * i) / (steps - 1))
    await page.evaluate((y) => window.scrollTo(0, y), y)
    await page.waitForTimeout(args.wait)

    const data = await page.evaluate(pageSampler)
    const frameName = `frame-${String(i).padStart(3, '0')}.png`
    await page.screenshot({ path: path.join(framesDir, frameName) })
    screenshots.push(frameName)
    samples.push({ step: i, targetY: y, ...data })
    process.stdout.write(`  sampled ${i + 1}/${steps}\r`)
  }
  console.log(`\nSampled ${steps} scroll positions.`)

  await browser.close()

  // --- Analysis ---

  // Dead scroll ranges: consecutive identical fingerprints
  const deadScrollRanges = []
  let rangeStart = null
  for (let i = 1; i < samples.length; i++) {
    const same = samples[i].fingerprint === samples[i - 1].fingerprint
    if (same && rangeStart === null) rangeStart = i - 1
    if (!same && rangeStart !== null) {
      deadScrollRanges.push({ fromStep: rangeStart, toStep: i - 1, fromPct: pct(rangeStart), toPct: pct(i - 1) })
      rangeStart = null
    }
  }
  if (rangeStart !== null) {
    deadScrollRanges.push({ fromStep: rangeStart, toStep: samples.length - 1, fromPct: pct(rangeStart), toPct: pct(samples.length - 1) })
  }
  function pct(step) { return Math.round((step / (steps - 1)) * 100) }

  // Stuck cues: peak opacity across all samples, per cue id
  const cuePeaks = new Map()
  for (const s of samples) {
    for (const cue of s.cues) {
      const prev = cuePeaks.get(cue.id) ?? 0
      cuePeaks.set(cue.id, Math.max(prev, cue.opacity))
    }
  }
  const stuckCues = Array.from(cuePeaks.entries())
    .filter(([, peak]) => peak < 0.98)
    .map(([id, peak]) => ({ id, peakOpacity: Math.round(peak * 100) / 100 }))

  // Stuck video: currentTime never changes despite scrollY changing a lot
  const videoTraces = new Map()
  for (const s of samples) {
    for (const v of s.videos) {
      if (!videoTraces.has(v.index)) videoTraces.set(v.index, [])
      videoTraces.get(v.index).push(v.currentTime)
    }
  }
  const stuckVideo = []
  for (const [index, times] of videoTraces.entries()) {
    const distinct = new Set(times.map((t) => Math.round(t * 10)))
    if (distinct.size <= 1 && scrollHeight > 200) {
      stuckVideo.push({ index, observedTimes: distinct.size, note: 'currentTime never changed across the full scroll traversal' })
    }
  }

  // Contrast failures: worst ratio observed per selector+text, graded per WCAG size thresholds
  const worstBySelector = new Map()
  for (const s of samples) {
    for (const t of s.contrastSamples) {
      const fg = parseRgb(t.color)
      const bg = parseRgb(t.background)
      if (!fg || !bg) continue
      const ratio = contrastRatio(fg.rgb, bg.rgb)
      const isLarge = t.fontSize >= 24 || (t.fontSize >= 19 && (t.fontWeight === 'bold' || parseInt(t.fontWeight, 10) >= 700))
      const threshold = isLarge ? 3.0 : 4.5
      const key = t.selector + '::' + t.text
      const existing = worstBySelector.get(key)
      if (!existing || ratio < existing.ratio) {
        worstBySelector.set(key, { selector: t.selector, text: t.text, ratio: Math.round(ratio * 100) / 100, threshold, isLarge, step: s.step, scrollPct: pct(s.step) })
      }
    }
  }
  const contrastFailures = Array.from(worstBySelector.values()).filter((c) => c.ratio < c.threshold)

  const report = {
    url: args.url,
    viewport: { width: vw, height: vh },
    steps,
    scrollHeight,
    deadScrollRanges,
    stuckCues,
    stuckVideo,
    contrastFailures,
    summary: {
      deadScrollRangeCount: deadScrollRanges.length,
      stuckCueCount: stuckCues.length,
      stuckVideoCount: stuckVideo.length,
      contrastFailureCount: contrastFailures.length,
    },
  }

  await writeFile(path.join(args.out, 'report.json'), JSON.stringify(report, null, 2))
  await writeFile(path.join(args.out, 'report.html'), renderHtmlReport(report, screenshots))

  console.log('\n--- QA Summary ---')
  console.log(`Dead scroll ranges: ${deadScrollRanges.length}`)
  console.log(`Stuck cues (never reach full opacity): ${stuckCues.length}`)
  console.log(`Stuck video playheads: ${stuckVideo.length}`)
  console.log(`Contrast failures: ${contrastFailures.length}`)
  console.log(`\nFull report: ${path.join(args.out, 'report.html')}`)
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}

function renderHtmlReport(report, screenshots) {
  const issueBadge = (n) => n === 0 ? '<span style="color:#2a8f4a">0</span>' : `<span style="color:#c0392b;font-weight:600">${n}</span>`
  return `<!doctype html>
<html><head><meta charset="utf-8"><title>Scroll QA Report</title>
<style>
  body { font-family: -apple-system, Segoe UI, sans-serif; background:#111; color:#eee; margin:0; padding:32px; }
  h1 { font-size: 20px; margin-bottom: 4px; }
  .meta { color:#999; font-size: 13px; margin-bottom: 24px; }
  .summary { display:flex; gap:24px; margin-bottom:32px; }
  .summary div { background:#1c1c1c; padding:12px 20px; border-radius:8px; }
  .summary .label { font-size:11px; color:#999; text-transform:uppercase; letter-spacing:0.05em; }
  .summary .value { font-size:24px; font-weight:600; }
  section { margin-bottom:32px; }
  section h2 { font-size:15px; border-bottom:1px solid #333; padding-bottom:8px; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  td, th { text-align:left; padding:6px 8px; border-bottom:1px solid #262626; }
  .strip { display:grid; grid-template-columns: repeat(auto-fill, minmax(140px,1fr)); gap:8px; }
  .strip img { width:100%; border-radius:4px; border:1px solid #333; display:block; }
  .strip .step { font-size:10px; color:#888; margin-top:2px; }
  code { background:#1c1c1c; padding:1px 4px; border-radius:3px; }
</style></head>
<body>
  <h1>Scroll QA Report</h1>
  <div class="meta">${esc(report.url)} — ${report.viewport.width}x${report.viewport.height} — ${report.steps} sampled positions</div>
  <div class="summary">
    <div><div class="label">Dead scroll ranges</div><div class="value">${issueBadge(report.summary.deadScrollRangeCount)}</div></div>
    <div><div class="label">Stuck cues</div><div class="value">${issueBadge(report.summary.stuckCueCount)}</div></div>
    <div><div class="label">Stuck video</div><div class="value">${issueBadge(report.summary.stuckVideoCount)}</div></div>
    <div><div class="label">Contrast failures</div><div class="value">${issueBadge(report.summary.contrastFailureCount)}</div></div>
  </div>

  <section><h2>Dead scroll ranges</h2>
  ${report.deadScrollRanges.length === 0 ? '<p>None.</p>' : `<table><tr><th>From</th><th>To</th></tr>${report.deadScrollRanges.map(r => `<tr><td>${r.fromPct}%</td><td>${r.toPct}%</td></tr>`).join('')}</table>`}
  </section>

  <section><h2>Stuck cues (never reach full opacity)</h2>
  ${report.stuckCues.length === 0 ? '<p>None.</p>' : `<table><tr><th>Element</th><th>Peak opacity</th></tr>${report.stuckCues.map(c => `<tr><td><code>${esc(c.id)}</code></td><td>${c.peakOpacity}</td></tr>`).join('')}</table>`}
  </section>

  <section><h2>Stuck video playheads</h2>
  ${report.stuckVideo.length === 0 ? '<p>None.</p>' : `<table><tr><th>Video index</th><th>Note</th></tr>${report.stuckVideo.map(v => `<tr><td>${v.index}</td><td>${esc(v.note)}</td></tr>`).join('')}</table>`}
  </section>

  <section><h2>Contrast failures</h2>
  ${report.contrastFailures.length === 0 ? '<p>None.</p>' : `<table><tr><th>Text</th><th>Selector</th><th>Ratio</th><th>Threshold</th><th>At scroll</th></tr>${report.contrastFailures.map(c => `<tr><td>${esc(c.text)}</td><td><code>${esc(c.selector)}</code></td><td>${c.ratio}:1</td><td>${c.threshold}:1</td><td>${c.scrollPct}%</td></tr>`).join('')}</table>`}
  </section>

  <section><h2>Contact sheet</h2>
  <div class="strip">
    ${screenshots.map((f, i) => `<div><img src="frames/${f}" loading="lazy"><div class="step">${i}</div></div>`).join('')}
  </div>
  </section>
</body></html>`
}

run().catch((err) => {
  console.error(err)
  process.exit(1)
})

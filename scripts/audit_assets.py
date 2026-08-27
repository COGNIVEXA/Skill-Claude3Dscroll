#!/usr/bin/env python3
"""
audit_assets.py

Part of the claude3Dscroll skill (by Cognivexa).

Walks a project directory (typically its `public/` or `static/` asset
root) and reports on 3D/media assets that commonly cause performance or
licensing problems in a scroll-driven 3D web build: oversized GLB/glTF
models, large texture/image files, large video files, and (optionally)
a starter ASSET_LICENSES.md manifest listing every external asset found
so it can be filled in against `references/asset-licensing.md`.

This is a size/inventory audit only — it does not inspect polygon
counts, texture dimensions, or draw calls, which require a real WebGL
context or a 3D-file-parsing dependency. Use `renderer.info` in the
browser (see references/performance.md) for those.

Usage:
    python audit_assets.py <path> [options]

    <path>                  Directory to scan (e.g. ./public, ./my-project)

Options:
    --glb-limit-mb N        Flag .glb/.gltf files over N MB (default: 5)
    --texture-limit-mb N    Flag image/texture files over N MB (default: 2)
    --video-limit-mb N      Flag video files over N MB (default: 15)
    --out FILE              Write the full report to FILE as Markdown
                             (in addition to printing a summary to stdout)
    --manifest FILE         Write a starter ASSET_LICENSES.md manifest
                             table listing every asset found, with blank
                             Source/License/Attribution columns to fill in
    --json FILE             Write the raw findings as JSON to FILE

Exit code is non-zero if any file exceeded its size limit, so this can
be wired into a CI/build-gate step if desired (it is not required by
the skill's own workflow, which treats this as an on-demand check).
"""

import argparse
import json
import sys
from pathlib import Path

MODEL_EXTS = {".glb", ".gltf"}
TEXTURE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".ktx2", ".basis", ".hdr", ".exr", ".tga"}
VIDEO_EXTS = {".mp4", ".webm", ".mov"}
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a"}
FONT_EXTS = {".woff", ".woff2", ".ttf", ".otf"}

CATEGORY_BY_EXT = {}
for ext in MODEL_EXTS:
    CATEGORY_BY_EXT[ext] = "model"
for ext in TEXTURE_EXTS:
    CATEGORY_BY_EXT[ext] = "texture"
for ext in VIDEO_EXTS:
    CATEGORY_BY_EXT[ext] = "video"
for ext in AUDIO_EXTS:
    CATEGORY_BY_EXT[ext] = "audio"
for ext in FONT_EXTS:
    CATEGORY_BY_EXT[ext] = "font"

SKIP_DIR_NAMES = {"node_modules", ".git", "dist", "build", ".next", ".vite", ".cache"}


def human_mb(num_bytes):
    return num_bytes / (1024 * 1024)


def scan(root: Path):
    found = {"model": [], "texture": [], "video": [], "audio": [], "font": []}
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in SKIP_DIR_NAMES:
                # rglob doesn't support pruning directly; skip files under it via continue below
                continue
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        ext = path.suffix.lower()
        category = CATEGORY_BY_EXT.get(ext)
        if category is None:
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        found[category].append({"path": str(path.relative_to(root)), "size_bytes": size})
    for category in found:
        found[category].sort(key=lambda e: e["size_bytes"], reverse=True)
    return found


def build_report(found, limits):
    lines = []
    total_bytes = sum(e["size_bytes"] for cat in found.values() for e in cat)
    lines.append("# Asset Audit Report\n")
    lines.append(f"Total tracked asset size: **{human_mb(total_bytes):.2f} MB** across "
                  f"{sum(len(v) for v in found.values())} files.\n")

    flagged = []
    limit_map = {"model": limits["glb"], "texture": limits["texture"], "video": limits["video"]}

    for category, label in [("model", "3D Models (.glb/.gltf)"),
                             ("texture", "Textures / Images"),
                             ("video", "Video"),
                             ("audio", "Audio"),
                             ("font", "Fonts")]:
        entries = found[category]
        if not entries:
            continue
        cat_total = sum(e["size_bytes"] for e in entries)
        lines.append(f"## {label} — {len(entries)} file(s), {human_mb(cat_total):.2f} MB total\n")
        lines.append("| File | Size (MB) | Flag |")
        lines.append("|---|---|---|")
        limit_mb = limit_map.get(category)
        for e in entries:
            size_mb = human_mb(e["size_bytes"])
            flag = ""
            if limit_mb is not None and size_mb > limit_mb:
                flag = f"⚠ over {limit_mb} MB limit"
                flagged.append({**e, "category": category, "limit_mb": limit_mb})
            lines.append(f"| {e['path']} | {size_mb:.2f} | {flag} |")
        lines.append("")

    if flagged:
        lines.append("## Flagged files\n")
        lines.append("These exceed the configured size limit and are worth a deliberate "
                      "decision (compress, reduce, or accept and document why) — see "
                      "`references/performance.md` and `references/responsive-3d.md`.\n")
        for e in flagged:
            lines.append(f"- `{e['path']}` — {human_mb(e['size_bytes']):.2f} MB "
                          f"(limit: {e['limit_mb']} MB, category: {e['category']})")
    else:
        lines.append("No files exceeded their configured size limits.\n")

    return "\n".join(lines), flagged


def build_manifest(found):
    lines = [
        "# Asset Manifest\n",
        "Starter manifest generated by `scripts/audit_assets.py`. Fill in Source/Creator/",
        "License/Attribution/Commercial Use for every row before shipping — see",
        "`references/asset-licensing.md` for what each column means and how to verify it.",
        "Delete rows for assets authored in-house (no external license to track).\n",
        "| Asset | Source | URL | Creator | License | Commercial Use | Attribution Required | Notes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for category in ("model", "texture", "video", "audio", "font"):
        for e in found[category]:
            lines.append(f"| {e['path']} | | | | | | | |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Audit 3D/media asset sizes for a claude3Dscroll build.")
    parser.add_argument("path", type=str, help="Directory to scan")
    parser.add_argument("--glb-limit-mb", type=float, default=5.0)
    parser.add_argument("--texture-limit-mb", type=float, default=2.0)
    parser.add_argument("--video-limit-mb", type=float, default=15.0)
    parser.add_argument("--out", type=str, default=None, help="Write full Markdown report to this file")
    parser.add_argument("--manifest", type=str, default=None, help="Write a starter ASSET_LICENSES.md to this file")
    parser.add_argument("--json", type=str, default=None, help="Write raw findings as JSON to this file")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists() or not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        sys.exit(2)

    found = scan(root)
    limits = {"glb": args.glb_limit_mb, "texture": args.texture_limit_mb, "video": args.video_limit_mb}
    report_text, flagged = build_report(found, limits)

    print(report_text)

    if args.out:
        Path(args.out).write_text(report_text, encoding="utf-8")
        print(f"\nFull report written to {args.out}", file=sys.stderr)

    if args.manifest:
        Path(args.manifest).write_text(build_manifest(found), encoding="utf-8")
        print(f"Starter manifest written to {args.manifest}", file=sys.stderr)

    if args.json:
        Path(args.json).write_text(json.dumps(found, indent=2), encoding="utf-8")
        print(f"Raw JSON findings written to {args.json}", file=sys.stderr)

    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()

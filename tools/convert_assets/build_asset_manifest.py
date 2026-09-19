#!/usr/bin/env python3
"""Build a generated-asset-centric Unity-to-ESP32 RGB565 manifest."""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    from PIL import Image
except ImportError as exc:
    print(f"ERROR: missing dependency: {exc}")
    sys.exit(1)


MATCHED = "ASSET_MATCHED"
AMBIGUOUS = "AMBIGUOUS"
UNMATCHED = "UNMATCHED"
RAW_DISCOVERED = "RAW_DISCOVERED"
UNRESOLVED = "UNRESOLVED"


def rgb888_to_rgb565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def parse_cpp_header(path):
    text = Path(path).read_text(encoding="utf-8")
    match = re.search(
        r"static\s+const\s+uint16_t\s+(\w+)\s*\[\s*(\d+)\s*\]\s*=\s*\{([^}]+)\}",
        text,
        re.DOTALL,
    )
    if not match:
        return None
    values = tuple(int(token.strip(), 0) for token in match.group(3).split(",") if token.strip())
    size = int(match.group(2))
    if len(values) != size:
        return None
    return {"symbol": match.group(1), "size": size, "values": values}


def scan_generated_assets(assets_dir):
    assets_dir = Path(assets_dir)
    result = {"characters": [], "animations": []}
    for directory, prefix, key, asset_type in (
        (assets_dir / "characters", "characters_", "characters", "character"),
        (assets_dir / "animations", "animations_", "animations", "animation"),
    ):
        for path in sorted(directory.glob(f"{prefix}*.h")):
            parsed = parse_cpp_header(path)
            if parsed is None:
                continue
            parsed.update({
                "file": str(path.relative_to(assets_dir)),
                "asset_type": asset_type,
            })
            result[key].append(parsed)
    return result


def parse_meta_file(meta_path):
    data = yaml.safe_load(Path(meta_path).read_text(encoding="utf-8").replace("!u!", "!!")) or {}
    importer = data.get("TextureImporter", {})
    sprites = importer.get("spriteSheet", {}).get("sprites", []) or []
    result = []
    for sprite in sprites:
        rect = sprite.get("rect") or {}
        fields = {key: rect.get(key) for key in ("x", "y", "width", "height")}
        if any(value is None for value in fields.values()):
            continue
        pivot = sprite.get("pivot") or None
        result.append({
            "sprite_name": sprite.get("name"),
            "rect": fields,
            "pivot": ({"x": pivot.get("x"), "y": pivot.get("y")} if pivot else None),
        })
    return result


def sheet_asset_type(relative_png):
    name = Path(relative_png).name.lower()
    if name == "characters.png":
        return "character"
    if name == "animations.png":
        return "animation"
    return None


def scan_unity_spritesheets(unity_root):
    root = Path(unity_root)
    sheets = []
    seen = set()
    for pattern in ("**/characters.png", "**/animations.png"):
        for png in root.glob(pattern):
            relative_png = str(png.relative_to(root))
            if relative_png in seen:
                continue
            seen.add(relative_png)
            meta = png.with_suffix(".png.meta")
            if not meta.exists():
                continue
            asset_type = sheet_asset_type(relative_png)
            if asset_type is None:
                continue
            sheets.append({
                "png_path": relative_png,
                "meta_path": str(meta.relative_to(root)),
                "asset_type": asset_type,
                "sprites": parse_meta_file(meta),
            })
    return sheets


def extract_rgb565(png_path, rect):
    image = Image.open(png_path).convert("RGB")
    x, y, width, height = rect["x"], rect["y"], rect["width"], rect["height"]
    y_pil = image.height - y - height
    if x < 0 or y_pil < 0 or x + width > image.width or y_pil + height > image.height:
        return None
    crop = image.crop((x, y_pil, x + width, y_pil + height))
    return tuple(rgb888_to_rgb565(*crop.getpixel((px, py))) for py in range(height) for px in range(width))


def source_record(sheet, sprite):
    return {
        "png": sheet["png_path"],
        "meta": sheet["meta_path"],
        "sprite_name": sprite["sprite_name"],
        "rect": sprite["rect"],
        "pivot": sprite["pivot"],
    }


def build_manifest(unity_root, assets_dir, unity_revision="unknown"):
    generated = scan_generated_assets(assets_dir)
    sheets = scan_unity_spritesheets(unity_root)
    all_assets = generated["characters"] + generated["animations"]

    # The final mapping is generated-centric: one mutable source list per header.
    candidates = {
        asset["symbol"]: {"asset": asset, "sources": []}
        for asset in all_assets
    }
    lookup = {
        "character": defaultdict(list),
        "animation": defaultdict(list),
    }
    for asset in all_assets:
        lookup[asset["asset_type"]][asset["values"]].append(asset["symbol"])

    raw_discovered = 0
    missing_metadata = 0
    for sheet in sheets:
        png = Path(unity_root) / sheet["png_path"]
        for sprite in sheet["sprites"]:
            expected = extract_rgb565(png, sprite["rect"])
            if expected is None:
                missing_metadata += 1
                continue
            raw_discovered += 1
            for symbol in lookup[sheet["asset_type"]].get(expected, []):
                candidates[symbol]["sources"].append(source_record(sheet, sprite))

    mapping = []
    statistics = {
        "total_generated": len(all_assets),
        "character_generated": len(generated["characters"]),
        "animation_generated": len(generated["animations"]),
        "raw_discovered": raw_discovered,
        "missing_metadata": missing_metadata,
        "asset_matched": 0,
        "ambiguous": 0,
        "unmatched": 0,
        "semantically_mapped": 0,
        "character_matched": 0,
        "character_unmatched": 0,
        "animation_matched": 0,
        "animation_unmatched": 0,
    }

    for asset in all_assets:
        sources = candidates[asset["symbol"]]["sources"]
        identity = {
            "asset_match": UNMATCHED,
            "character": None,
            "animation": None,
            "semantic_status": UNRESOLVED,
        }
        entry = {
            "generated_symbol": asset["symbol"],
            "generated_file": asset["file"],
            "asset_type": asset["asset_type"],
            "source": None,
            "identity": identity,
        }
        if len(sources) == 1:
            entry["source"] = sources[0]
            identity["asset_match"] = MATCHED
            identity["semantic_status"] = RAW_DISCOVERED
            statistics["asset_matched"] += 1
            statistics[f"{asset['asset_type']}_matched"] += 1
        elif len(sources) > 1:
            entry["sources"] = sources
            identity["asset_match"] = AMBIGUOUS
            identity["semantic_status"] = RAW_DISCOVERED
            statistics["ambiguous"] += 1
        else:
            statistics["unmatched"] += 1
            statistics[f"{asset['asset_type']}_unmatched"] += 1
        mapping.append(entry)

    assert len(mapping) == statistics["total_generated"]
    assert statistics["asset_matched"] + statistics["ambiguous"] + statistics["unmatched"] == statistics["total_generated"]

    return {
        "source_repository": "cerudn/Digivice_D-tector-V2_Unity-",
        "unity_revision": unity_revision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "spritesheets": sheets,
        "generated_assets": {
            "characters": [{key: item[key] for key in ("symbol", "file", "size")} for item in generated["characters"]],
            "animations": [{key: item[key] for key in ("symbol", "file", "size")} for item in generated["animations"]],
        },
        "mapping": mapping,
        "statistics": statistics,
    }


def generate_report(manifest, report_path):
    stats = manifest["statistics"]
    lines = [
        "# Asset Mapping Report", "",
        f"Unity repository: `{manifest['source_repository']}`", 
        f"Unity revision: `{manifest['unity_revision']}`", "",
        "## Model", "",
        "`mapping` is generated-asset-centric: exactly one entry exists for every generated header.",
        "A generated asset has zero sources (`UNMATCHED`), one source (`ASSET_MATCHED`), or multiple sources (`AMBIGUOUS`).", "",
        "## Statistics", "",
    ]
    for key in ("total_generated", "character_generated", "animation_generated", "raw_discovered", "asset_matched", "ambiguous", "unmatched", "semantically_mapped", "missing_metadata", "character_matched", "character_unmatched", "animation_matched", "animation_unmatched"):
        lines.append(f"- {key.upper()}: {stats[key]}")
    lines.extend(["", "## Sample mappings", "", "| Generated | Type | Unity source(s) | Status |", "|---|---|---|---|"])
    for entry in manifest["mapping"][:20]:
        sources = entry.get("sources") or ([entry["source"]] if entry.get("source") else [])
        names = ", ".join((source.get("sprite_name") or "unnamed") for source in sources) or "NONE"
        lines.append(f"| {entry['generated_symbol']} | {entry['asset_type']} | {names} | {entry['identity']['asset_match']} |")
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Build generated-asset Unity mapping")
    parser.add_argument("--unity-root", required=True)
    parser.add_argument("--assets-dir", required=True)
    parser.add_argument("--unity-revision", default="unknown")
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    manifest = build_manifest(args.unity_root, args.assets_dir, args.unity_revision)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    generate_report(manifest, args.report)
    for key, value in manifest["statistics"].items():
        print(f"{key.upper()}: {value}")


if __name__ == "__main__":
    main()

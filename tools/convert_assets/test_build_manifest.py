#!/usr/bin/env python3
"""Unit tests for generated-asset-centric RGB565 mapping."""

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from build_asset_manifest import AMBIGUOUS, MATCHED, UNMATCHED, build_manifest, rgb888_to_rgb565

RED, GREEN, BLUE, WHITE, BLACK = (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (0, 0, 0)


def write_header(path, symbol, pixels):
    values = ", ".join(f"0x{rgb888_to_rgb565(*pixel):04X}" for pixel in pixels)
    path.write_text(f"static const uint16_t {symbol}[{len(pixels)}] = {{ {values} }};\n", encoding="utf-8")


def write_png_and_meta(sprite_dir, name, width, height, pixels, sprites):
    png = sprite_dir / name
    image = Image.new("RGB", (width, height))
    image.putdata(pixels)
    image.save(png)
    lines = ["FileFormatVersion: 2", "TextureImporter:", "  spriteSheet:", "    sprites:"]
    for sprite_name, x, y, w, h in sprites:
        lines.extend([f"    - name: {sprite_name}", "      rect:", f"        x: {x}", f"        y: {y}", f"        width: {w}", f"        height: {h}", "      pivot:", "        x: 0.5", "        y: 0.5"])
    png.with_suffix(".png.meta").write_text("\n".join(lines) + "\n", encoding="utf-8")


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.assets = self.root / "assets"
        self.characters = self.assets / "characters"
        self.animations = self.assets / "animations"
        self.sprites = self.root / "Assets" / "Sprites"
        self.characters.mkdir(parents=True)
        self.animations.mkdir(parents=True)
        self.sprites.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()


class TestGeneratedCentricManifest(Fixture):
    def test_unique_match_has_two_mapping_entries_for_two_headers(self):
        write_png_and_meta(self.sprites, "characters.png", 2, 2, [RED, BLUE, GREEN, WHITE], [("a", 0, 0, 1, 2), ("b", 1, 0, 1, 2)])
        write_header(self.characters / "characters_0.h", "characters_0", [RED, GREEN])
        write_header(self.characters / "characters_1.h", "characters_1", [BLUE, WHITE])
        manifest = build_manifest(self.root, self.assets, "abc123")
        self.assertEqual(len(manifest["mapping"]), 2)
        self.assertEqual(manifest["statistics"]["asset_matched"], 2)
        self.assertEqual({item["generated_symbol"] for item in manifest["mapping"]}, {"characters_0", "characters_1"})

    def test_unmatched_generated_header_still_has_one_entry(self):
        write_png_and_meta(self.sprites, "characters.png", 2, 2, [RED, BLUE, GREEN, WHITE], [("a", 0, 0, 1, 2), ("b", 1, 0, 1, 2)])
        write_header(self.characters / "characters_0.h", "characters_0", [RED, GREEN])
        write_header(self.characters / "characters_1.h", "characters_1", [BLUE, WHITE])
        write_header(self.characters / "characters_2.h", "characters_2", [BLACK, BLACK])
        manifest = build_manifest(self.root, self.assets)
        entries = {item["generated_symbol"]: item for item in manifest["mapping"]}
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries["characters_2"]["source"], None)
        self.assertEqual(entries["characters_2"]["identity"]["asset_match"], UNMATCHED)
        self.assertEqual(manifest["statistics"]["unmatched"], 1)

    def test_ambiguous_header_has_multiple_sources_but_one_entry(self):
        write_png_and_meta(self.sprites, "characters.png", 2, 2, [RED, RED, GREEN, GREEN], [("a", 0, 0, 1, 2), ("b", 1, 0, 1, 2)])
        write_header(self.characters / "characters_0.h", "characters_0", [RED, GREEN])
        manifest = build_manifest(self.root, self.assets)
        self.assertEqual(len(manifest["mapping"]), 1)
        entry = manifest["mapping"][0]
        self.assertEqual(entry["identity"]["asset_match"], AMBIGUOUS)
        self.assertEqual(len(entry["sources"]), 2)
        self.assertEqual(manifest["statistics"]["ambiguous"], 1)

    def test_animation_never_cross_matches_character_header(self):
        write_png_and_meta(self.sprites, "animations.png", 1, 2, [BLUE, WHITE], [("anim", 0, 0, 1, 2)])
        write_header(self.characters / "characters_0.h", "characters_0", [BLUE, WHITE])
        write_header(self.animations / "animations_0.h", "animations_0", [BLACK, BLACK])
        manifest = build_manifest(self.root, self.assets)
        entries = {item["generated_symbol"]: item for item in manifest["mapping"]}
        self.assertEqual(entries["animations_0"]["identity"]["asset_match"], UNMATCHED)
        self.assertEqual(entries["characters_0"]["identity"]["asset_match"], UNMATCHED)

    def test_mapping_has_exactly_generated_symbols_once(self):
        write_header(self.characters / "characters_0.h", "characters_0", [RED])
        write_header(self.animations / "animations_0.h", "animations_0", [BLUE])
        manifest = build_manifest(self.root, self.assets)
        generated = {item["symbol"] for group in manifest["generated_assets"].values() for item in group}
        mapped = [item["generated_symbol"] for item in manifest["mapping"]]
        self.assertEqual(set(mapped), generated)
        self.assertEqual(len(mapped), len(set(mapped)))
        self.assertEqual(len(mapped), manifest["statistics"]["total_generated"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

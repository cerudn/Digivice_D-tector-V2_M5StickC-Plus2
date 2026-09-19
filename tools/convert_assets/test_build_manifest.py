#!/usr/bin/env python3
"""Tests for build_asset_manifest.py RGB565 content matching."""

import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from build_asset_manifest import (
    MatchStatus,
    build_manifest,
    rgb888_to_rgb565,
    scan_unity_spritesheets,
)


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def rgb565_pixels(pixels):
    return [rgb888_to_rgb565(*pixel) for pixel in pixels]


def write_header(path, symbol, pixels):
    values = ', '.join(f'0x{value:04X}' for value in rgb565_pixels(pixels))
    path.write_text(
        f'static const uint16_t {symbol}[{len(pixels)}] = {{\n'
        f'    {values}\n'
        f'}};\n',
        encoding='utf-8',
    )


def write_png(path, width, height, pixels):
    image = Image.new('RGB', (width, height))
    image.putdata(pixels)
    image.save(path)


def write_meta(path, sprites):
    lines = [
        'FileFormatVersion: 2',
        'TextureImporter:',
        '  spriteSheet:',
        '    sprites:',
    ]
    for name, x, y, width, height in sprites:
        lines.extend([
            f'    - name: {name}',
            '      rect:',
            f'        x: {x}',
            f'        y: {y}',
            f'        width: {width}',
            f'        height: {height}',
            '      pivot:',
            '        x: 0.5',
            '        y: 0.5',
        ])
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


class MappingFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.assets = self.root / 'assets'
        self.characters = self.assets / 'characters'
        self.animations = self.assets / 'animations'
        self.sprites = self.root / 'Assets' / 'Sprites'
        self.characters.mkdir(parents=True)
        self.animations.mkdir(parents=True)
        self.sprites.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def create_sheet(self, basename, width, height, pixels, sprites):
        png = self.sprites / basename
        write_png(png, width, height, pixels)
        write_meta(png.with_suffix('.png.meta'), sprites)
        return png


class TestContentMatching(MappingFixture):
    def test_character_headers_match_real_rgb565_content(self):
        # Unity y=0, h=2 on a 2-pixel-high PNG converts to PIL y=0.
        # Each 1x2 vertical rect therefore reads pixels in top-to-bottom order.
        sprite_a = [RED, GREEN]
        sprite_b = [BLUE, WHITE]
        self.create_sheet(
            'characters.png', 2, 2,
            [RED, BLUE, GREEN, WHITE],
            [('sprite_a', 0, 0, 1, 2), ('sprite_b', 1, 0, 1, 2)],
        )
        write_header(self.characters / 'characters_0.h', 'characters_0', sprite_a)
        write_header(self.characters / 'characters_1.h', 'characters_1', sprite_b)
        write_header(self.characters / 'characters_2.h', 'characters_2', [BLACK, BLACK])

        manifest = build_manifest(self.root, self.assets, unity_revision='abc123')
        stats = manifest['statistics']

        self.assertEqual(stats['total_generated'], 3)
        self.assertEqual(stats['character_generated'], 3)
        self.assertEqual(stats['asset_matched'], 2)
        self.assertEqual(stats['character_matched'], 2)
        self.assertEqual(stats['semantically_mapped'], 0)

        matched = [entry for entry in manifest['mapping'] if entry['identity']['asset_match'] == MatchStatus.ASSET_MATCHED.value]
        self.assertEqual({entry['generated_symbol'] for entry in matched}, {'characters_0', 'characters_1'})

    def test_semantic_status_is_raw_discovered_without_semantic_evidence(self):
        pixels = [RED, GREEN]
        # Unity y=0, h=2 on a 2-pixel-high PNG converts to PIL y=0.
        self.create_sheet(
            'characters.png', 1, 2, pixels,
            [('sprite_a', 0, 0, 1, 2)],
        )
        write_header(self.characters / 'characters_0.h', 'characters_0', pixels)

        manifest = build_manifest(self.root, self.assets, unity_revision='abc123')
        entry = next(entry for entry in manifest['mapping'] if entry['generated_symbol'] == 'characters_0')

        self.assertEqual(entry['identity']['asset_match'], MatchStatus.ASSET_MATCHED.value)
        self.assertEqual(entry['identity']['semantic_status'], MatchStatus.RAW_DISCOVERED.value)
        self.assertIsNone(entry['identity']['character'])
        self.assertIsNone(entry['identity']['animation'])

    def test_animations_use_animation_lookup(self):
        pixels = [BLUE, WHITE]
        # Unity y=0, h=2 on a 2-pixel-high PNG converts to PIL y=0.
        self.create_sheet(
            'animations.png', 1, 2, pixels,
            [('animation_a', 0, 0, 1, 2)],
        )
        write_header(self.animations / 'animations_0.h', 'animations_0', pixels)
        write_header(self.characters / 'characters_0.h', 'characters_0', [RED, GREEN])

        manifest = build_manifest(self.root, self.assets, unity_revision='abc123')
        entry = next(entry for entry in manifest['mapping'] if entry.get('source') and entry['source']['sprite_name'] == 'animation_a')

        self.assertEqual(entry['asset_type'], 'animation')
        self.assertEqual(entry['generated_symbol'], 'animations_0')
        self.assertEqual(entry['identity']['asset_match'], MatchStatus.ASSET_MATCHED.value)
        self.assertEqual(manifest['statistics']['animation_matched'], 1)

    def test_animation_does_not_cross_match_character_header(self):
        pixels = [BLUE, WHITE]
        # Unity y=0, h=2 on a 2-pixel-high PNG converts to PIL y=0.
        self.create_sheet(
            'animations.png', 1, 2, pixels,
            [('animation_a', 0, 0, 1, 2)],
        )
        write_header(self.characters / 'characters_0.h', 'characters_0', pixels)

        manifest = build_manifest(self.root, self.assets, unity_revision='abc123')
        entry = next(entry for entry in manifest['mapping'] if entry.get('source') and entry['source']['sprite_name'] == 'animation_a')

        self.assertEqual(entry['asset_type'], 'animation')
        self.assertEqual(entry['identity']['asset_match'], MatchStatus.UNMATCHED.value)
        self.assertIsNone(entry['generated_symbol'])
        self.assertEqual(manifest['statistics']['animation_matched'], 0)

    def test_duplicate_headers_are_ambiguous(self):
        pixels = [RED, GREEN]
        # Unity y=0, h=2 on a 2-pixel-high PNG converts to PIL y=0.
        self.create_sheet(
            'characters.png', 1, 2, pixels,
            [('sprite_a', 0, 0, 1, 2)],
        )
        write_header(self.characters / 'characters_0.h', 'characters_0', pixels)
        write_header(self.characters / 'characters_1.h', 'characters_1', pixels)

        manifest = build_manifest(self.root, self.assets)
        entry = next(entry for entry in manifest['mapping'] if entry.get('source'))

        self.assertEqual(entry['identity']['asset_match'], MatchStatus.AMBIGUOUS.value)
        self.assertEqual(set(entry['identity']['ambiguous_matches']), {'characters_0', 'characters_1'})
        self.assertEqual(manifest['statistics']['ambiguous'], 1)


class TestDiscoveryAndMetadata(MappingFixture):
    def test_spritesheet_paths_are_deduplicated(self):
        pixels = [RED]
        # Unity y=0, h=1 on a 1-pixel-high PNG converts to PIL y=0.
        self.create_sheet('characters.png', 1, 1, pixels, [('sprite_a', 0, 0, 1, 1)])

        sheets = scan_unity_spritesheets(self.root)

        self.assertEqual(len(sheets), 1)
        self.assertEqual(sheets[0]['png_path'], 'Assets/Sprites/characters.png')

    def test_unity_revision_is_preserved(self):
        manifest = build_manifest(self.root, self.assets, unity_revision='abc123')
        self.assertEqual(manifest['unity_revision'], 'abc123')

    def test_generated_at_is_iso_timestamp_not_filesystem_path(self):
        manifest = build_manifest(self.root, self.assets, unity_revision='abc123')
        generated_at = manifest['generated_at']

        self.assertNotIn(str(self.root), generated_at)
        self.assertNotIn('/home/runner/work/', generated_at)
        self.assertIsNotNone(datetime.fromisoformat(generated_at))


if __name__ == '__main__':
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""
Tests for build_asset_manifest.py
"""

import unittest
import tempfile
import os
import json
from pathlib import Path


class TestMatchStatus(unittest.TestCase):
    """Test match status enum."""
    
    def test_status_levels(self):
        """Verify all match status levels exist."""
        from build_asset_manifest import MatchStatus
        
        self.assertEqual(MatchStatus.RAW_DISCOVERED.value, "RAW_DISCOVERED")
        self.assertEqual(MatchStatus.ASSET_MATCHED.value, "ASSET_MATCHED")
        self.assertEqual(MatchStatus.SEMANTICALLY_MAPPED.value, "SEMANTICALLY_MAPPED")
        self.assertEqual(MatchStatus.UNMATCHED.value, "UNMATCHED")
        self.assertEqual(MatchStatus.AMBIGUOUS.value, "AMBIGUOUS")
        self.assertEqual(MatchStatus.MISSING_METADATA.value, "MISSING_METADATA")


class TestMetaParser(unittest.TestCase):
    """Test .meta file parsing."""
    
    def test_missing_rect_rejected(self):
        """Verify sprites without rect are rejected."""
        from build_asset_manifest import parse_meta_file
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
            f.write("""FileFormatVersion: 2
TextureImporter:
  spriteSheet:
    sprites:
    - name: test_sprite
      rect: {}
""")
            f.flush()
            
            sprites = parse_meta_file(f.name)
            self.assertEqual(len(sprites), 0)
        
        os.unlink(f.name)
    
    def test_valid_rect_accepted(self):
        """Verify sprites with valid rect are accepted."""
        from build_asset_manifest import parse_meta_file
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
            f.write("""FileFormatVersion: 2
TextureImporter:
  spriteSheet:
    sprites:
    - name: test_sprite
      rect:
        serializedVersion: 2
        x: 0
        y: 0
        width: 32
        height: 32
""")
            f.flush()
            
            sprites = parse_meta_file(f.name)
            self.assertEqual(len(sprites), 1)
            self.assertEqual(sprites[0]['rect']['width'], 32)
        
        os.unlink(f.name)


class TestManifestStatistics(unittest.TestCase):
    """Test manifest statistics are honest."""
    
    def test_unmatched_counted_separately(self):
        """Verify unmatched assets are counted separately from matched."""
        from build_asset_manifest import build_manifest, MatchStatus
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create more generated assets than Unity sprites
            chars_dir = Path(tmpdir) / 'characters'
            chars_dir.mkdir()
            (chars_dir / 'characters_0.h').touch()
            (chars_dir / 'characters_1.h').touch()
            (chars_dir / 'characters_2.h').touch()  # Extra - no Unity sprite
            
            # Create mock Unity metadata with only 2 sprites
            sprites_dir = Path(tmpdir) / 'Sprites'
            sprites_dir.mkdir()
            (sprites_dir / 'characters.png').touch()
            with open(sprites_dir / 'characters.png.meta', 'w') as f:
                f.write("""FileFormatVersion: 2
TextureImporter:
  spriteSheet:
    sprites:
    - name: sprite_0
      rect:
        x: 0
        y: 0
        width: 32
        height: 32
    - name: sprite_1
      rect:
        x: 32
        y: 0
        width: 32
        height: 32
""")
            
            manifest = build_manifest(tmpdir, tmpdir)
            stats = manifest['statistics']
            
            # Should have 3 generated, 2 raw discovered, 2 matched, 1 unmatched
            self.assertEqual(stats['total_generated'], 3)
            self.assertEqual(stats['raw_discovered'], 2)
            self.assertEqual(stats['asset_matched'], 2)
            self.assertEqual(stats['unmatched'], 1)


class TestIdentityLevels(unittest.TestCase):
    """Test identity level separation."""
    
    def test_semantic_status_defaults_to_raw_discovered(self):
        """Verify semantic status is RAW_DISCOVERED when no semantic data."""
        from build_asset_manifest import build_manifest, MatchStatus
        
        with tempfile.TemporaryDirectory() as tmpdir:
            chars_dir = Path(tmpdir) / 'characters'
            chars_dir.mkdir()
            (chars_dir / 'characters_0.h').touch()
            
            sprites_dir = Path(tmpdir) / 'Sprites'
            sprites_dir.mkdir()
            (sprites_dir / 'characters.png').touch()
            with open(sprites_dir / 'characters.png.meta', 'w') as f:
                f.write("""FileFormatVersion: 2
TextureImporter:
  spriteSheet:
    sprites:
    - name: sprite_0
      rect:
        x: 0
        y: 0
        width: 32
        height: 32
""")
            
            manifest = build_manifest(tmpdir, tmpdir)
            
            # Should have asset match but no semantic mapping
            entry = manifest['mapping'][0]
            self.assertEqual(entry['identity']['asset_match'], MatchStatus.ASSET_MATCHED.value)
            self.assertEqual(entry['identity']['semantic_status'], MatchStatus.RAW_DISCOVERED.value)
            self.assertIsNone(entry['identity']['character'])
            self.assertIsNone(entry['identity']['animation'])


if __name__ == '__main__':
    unittest.main()

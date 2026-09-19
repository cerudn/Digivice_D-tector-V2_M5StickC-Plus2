#!/usr/bin/env python3
"""
Tests for build_asset_manifest.py
"""

import unittest
import tempfile
import os
from pathlib import Path


class TestMetaParser(unittest.TestCase):
    """Test .meta file parsing."""
    
    def test_meta_file_exists(self):
        """Verify meta parser can be imported."""
        try:
            from build_asset_manifest import parse_meta_file
            self.assertTrue(True)
        except ImportError:
            self.fail("Could not import build_asset_manifest")


class TestAssetScanning(unittest.TestCase):
    """Test asset scanning functions."""
    
    def test_scan_generated_assets(self):
        """Test scanning of generated character/animation headers."""
        from build_asset_manifest import scan_generated_assets
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock asset structure
            chars_dir = Path(tmpdir) / 'characters'
            chars_dir.mkdir()
            (chars_dir / 'characters_0.h').touch()
            (chars_dir / 'characters_1.h').touch()
            
            anims_dir = Path(tmpdir) / 'animations'
            anims_dir.mkdir()
            (anims_dir / 'animations_0.h').touch()
            
            characters, animations = scan_generated_assets(tmpdir)
            
            self.assertEqual(len(characters), 2)
            self.assertEqual(len(animations), 1)
            self.assertEqual(characters[0]['index'], 0)
            self.assertEqual(animations[0]['index'], 0)


class TestManifestStructure(unittest.TestCase):
    """Test manifest structure."""
    
    def test_manifest_has_required_fields(self):
        """Verify manifest contains required fields."""
        from build_asset_manifest import build_manifest
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal asset structure
            chars_dir = Path(tmpdir) / 'characters'
            chars_dir.mkdir()
            (chars_dir / 'characters_0.h').touch()
            
            anims_dir = Path(tmpdir) / 'animations'
            anims_dir.mkdir()
            (anims_dir / 'animations_0.h').touch()
            
            manifest = build_manifest(tmpdir, tmpdir)
            
            # Check required fields
            self.assertIn('source_repository', manifest)
            self.assertIn('spritesheets', manifest)
            self.assertIn('generated_assets', manifest)
            self.assertIn('mapping', manifest)
            self.assertIn('statistics', manifest)
            
            # Check statistics
            stats = manifest['statistics']
            self.assertIn('total_character_frames', stats)
            self.assertIn('total_animation_frames', stats)
            self.assertIn('mapped_frames', stats)


if __name__ == '__main__':
    unittest.main()

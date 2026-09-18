#!/usr/bin/env python3
"""Validate generated assets and manifest."""

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Validate generated assets')
    parser.add_argument('--assets-dir', required=True, help='Path to assets directory')
    parser.add_argument('--manifest', required=True, help='Path to asset_manifest.json')
    
    args = parser.parse_args()
    
    assets_dir = Path(args.assets_dir).resolve()
    manifest_path = Path(args.manifest).resolve()
    
    errors = []
    
    # Load manifest
    if not manifest_path.exists():
        print(f'ERROR: Manifest not found: {manifest_path}', file=sys.stderr)
        sys.exit(1)
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Validate structure
    required_keys = ['source', 'sprite_name', 'character', 'animation', 'x', 'y', 'width', 'height', 'pivot', 'frame_index', 'output_file', 'output_symbol']
    
    for i, entry in enumerate(manifest):
        for key in required_keys:
            if key not in entry:
                errors.append(f'Entry {i}: missing key "{key}"')
        
        # Check output file exists
        if 'output_file' in entry:
            output_path = Path(entry['output_file'])
            if not output_path.is_absolute():
                output_path = assets_dir.parent / output_path
            if not output_path.exists():
                errors.append(f'Entry {i}: output file not found: {entry["output_file"]}')
    
    if errors:
        print('VALIDATION ERRORS:')
        for err in errors:
            print(f'  - {err}')
        sys.exit(1)
    
    print(f'Validation passed: {len(manifest)} assets in manifest')
    print(f'Assets directory structure:')
    for root, dirs, files in os.walk(assets_dir):
        level = root.replace(str(assets_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files[:10]:  # Limit output
            print(f'{subindent}{file}')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

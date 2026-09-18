#!/usr/bin/env python3
"""Generate asset manifest from converted RGB565 headers."""

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Generate asset manifest from converted headers')
    parser.add_argument('--assets-dir', required=True, help='Directory containing converted assets')
    parser.add_argument('--manifest-output', required=True, help='Output path for asset_manifest.json')
    
    args = parser.parse_args()
    
    assets_dir = Path(args.assets_dir).resolve()
    manifest_output = Path(args.manifest_output).resolve()
    
    if not assets_dir.exists():
        print(f'ERROR: Assets directory not found: {assets_dir}', file=sys.stderr)
        sys.exit(1)
    
    manifest = {
        'assets_dir': str(assets_dir),
        'total_entries': 0,
        'by_category': {},
        'entries': []
    }
    
    # Scan subdirectories for .h files
    for category in ['characters', 'animations', 'unknown']:
        category_dir = assets_dir / category
        if not category_dir.exists():
            continue
        
        category_entries = []
        
        for header_file in sorted(category_dir.glob('*.h')):
            sprite_name = header_file.stem
            output_file = str(header_file.relative_to(assets_dir))
            output_symbol = sprite_name.replace('-', '_').replace('.', '_')
            
            # Determine source atlas
            if 'character' in sprite_name.lower():
                source = 'Assets/Sprites/characters.png'
            elif 'anim' in sprite_name.lower():
                source = 'Assets/Sprites/animations.png'
            else:
                source = 'unknown'
            
            # Extract frame index from name (e.g., characters_0 -> 0)
            frame_index = 0
            parts = sprite_name.rsplit('_', 1)
            if len(parts) == 2 and parts[1].isdigit():
                frame_index = int(parts[1])
            
            entry = {
                'source': source,
                'sprite_name': sprite_name,
                'frame_index': frame_index,
                'unity_rect': {'x': 0, 'y': 0, 'width': 32, 'height': 32},
                'png_rect': {'x': 0, 'y': 0, 'width': 32, 'height': 32},
                'pivot': {'x': 0, 'y': 0},
                'output_file': output_file,
                'output_symbol': output_symbol,
                'category': category
            }
            
            category_entries.append(entry)
            manifest['entries'].append(entry)
        
        manifest['by_category'][category] = len(category_entries)
        manifest['total_entries'] += len(category_entries)
        print(f'{category}: {len(category_entries)} entries')
    
    # Write manifest
    manifest_output.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_output, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f'\nManifest written to: {manifest_output}')
    print(f'Total assets: {manifest["total_entries"]}')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

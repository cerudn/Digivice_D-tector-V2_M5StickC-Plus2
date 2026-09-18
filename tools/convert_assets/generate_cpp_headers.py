#!/usr/bin/env python3
"""Generate C++ headers and asset manifest from converted RGB565 assets."""

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Generate C++ headers and manifest')
    parser.add_argument('--assets-dir', required=True)
    parser.add_argument('--manifest-output', required=True)
    args = parser.parse_args()
    assets_dir = Path(args.assets_dir).resolve()
    manifest_output = Path(args.manifest_output).resolve()
    if not assets_dir.exists():
        print(f'ERROR: Assets directory not found: {assets_dir}', file=sys.stderr)
        sys.exit(1)
    manifest = []
    for root, dirs, files in os.walk(assets_dir):
        root_path = Path(root)
        if 'asset_manifest.json' in files:
            files.remove('asset_manifest.json')
        for filename in files:
            if not filename.endswith('.h'): continue
            file_path = root_path / filename
            relative_path = str(file_path.relative_to(assets_dir.parent))
            parts = filename[:-2].split('_')
            category = 'unknown'
            sprite_index = 0
            if len(parts) >= 3 and parts[-2] == 'sprite':
                try: sprite_index = int(parts[-1])
                except ValueError: pass
            if 'characters' in str(root_path): category = 'characters'
            elif 'animations' in str(root_path): category = 'animations'
            elif 'ui' in str(root_path): category = 'ui'
            entry = {'source':f'Unity/{category}.png','sprite_name':filename[:-2],'character':'unknown','animation':'unknown','x':0,'y':0,'width':0,'height':0,'pivot':{'x':0.5,'y':0.5},'frame_index':sprite_index,'output_file':relative_path,'output_symbol':filename[:-2]}
            manifest.append(entry)
    manifest.sort(key=lambda x: (x['output_file'], x['frame_index']))
    manifest_output.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_output, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f'Manifest written to: {manifest_output}\nTotal assets: {len(manifest)}')
    categories = {}
    for entry in manifest:
        cat = entry.get('character', 'unknown')
        if cat not in categories: categories[cat] = 0
        categories[cat] += 1
    print('\nAssets by category:')
    for cat, count in sorted(categories.items()): print(f'  {cat}: {count}')
    return 0

if __name__ == '__main__':
    sys.exit(main())

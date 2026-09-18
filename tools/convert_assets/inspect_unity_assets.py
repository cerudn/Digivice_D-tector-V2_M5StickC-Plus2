#!/usr/bin/env python3
"""Inspect Unity PNG and .meta files to extract real sprite slicing information."""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from PIL import Image


def parse_unity_meta(meta_path: str) -> dict:
    result = {
        'fileType': None, 'guid': None, 'spriteMode': None,
        'pixelsPerUnit': None, 'filterMode': None, 'compression': None,
        'spriteRects': [], 'spritePivots': [], 'raw_content': None, 'error': None
    }
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            content = f.read()
            result['raw_content'] = content
        match = re.search(r'fileID:\s*(\d+)', content)
        if match: result['fileType'] = match.group(1)
        match = re.search(r'guid:\s*([a-f0-9]+)', content)
        if match: result['guid'] = match.group(1)
        match = re.search(r'spriteMode:\s*(\d+)', content)
        if match:
            mode_val = int(match.group(1))
            result['spriteMode'] = 'Tight' if mode_val == 0 else 'Rectangle'
        match = re.search(r'pixelsPerUnit:\s*(\d+)', content)
        if match: result['pixelsPerUnit'] = int(match.group(1))
        match = re.search(r'filterMode:\s*(\d+)', content)
        if match:
            filter_val = int(match.group(1))
            result['filterMode'] = {0:'Point',1:'Bilinear',2:'Trilinear'}.get(filter_val, f'Unknown({filter_val})')
        match = re.search(r'compression:\s*(\d+)', content)
        if match:
            comp_val = int(match.group(1))
            result['compression'] = {0:'Uncompressed',1:'Low',2:'Normal',3:'High'}.get(comp_val, f'Unknown({comp_val})')
        rect_pattern = r'first:\s*\{x:\s*(\d+),\s*y:\s*(\d+),\s*width:\s*(\d+),\s*height:\s*(\d+)\}'
        for match in re.finditer(rect_pattern, content):
            result['spriteRects'].append({'x':int(match.group(1)),'y':int(match.group(2)),'width':int(match.group(3)),'height':int(match.group(4))})
        pivot_pattern = r'pivot:\s*\{x:\s*([\d.]+),\s*y:\s*([\d.]+)\}'
        for match in re.finditer(pivot_pattern, content):
            result['spritePivots'].append({'x':float(match.group(1)),'y':float(match.group(2))})
    except Exception as e:
        result['error'] = str(e)
    return result


def inspect_png(png_path: str) -> dict:
    result = {'filename':os.path.basename(png_path),'width':None,'height':None,'mode':None,'has_alpha':False,'format':None,'error':None}
    try:
        with Image.open(png_path) as img:
            result['width'] = img.width
            result['height'] = img.height
            result['mode'] = img.mode
            result['has_alpha'] = img.mode in ('RGBA','LA','P') and 'transparency' in img.info
            result['format'] = img.format
    except Exception as e:
        result['error'] = str(e)
    return result


def main():
    parser = argparse.ArgumentParser(description='Inspect Unity PNG and .meta files')
    parser.add_argument('--unity-root', required=True, help='Path to Unity repository root')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--assets', nargs='+', default=['Assets/Sprites/characters.png','Assets/Sprites/animations.png'])
    args = parser.parse_args()
    unity_root = Path(args.unity_root).resolve()
    output_path = Path(args.output).resolve()
    if not unity_root.exists():
        print(f'ERROR: Unity root not found: {unity_root}', file=sys.stderr)
        sys.exit(1)
    report = {'unity_root':str(unity_root),'assets':[]}
    for asset_rel_path in args.assets:
        asset_path = unity_root / asset_rel_path
        meta_path = unity_root / f'{asset_rel_path}.meta'
        asset_info = {'relative_path':asset_rel_path,'absolute_path':str(asset_path),'png_info':None,'meta_info':None,'status':'pending'}
        if not asset_path.exists():
            asset_info['status'] = 'error'
            asset_info['error'] = f'PNG file not found: {asset_path}'
            report['assets'].append(asset_info)
            continue
        if not meta_path.exists():
            asset_info['status'] = 'warning'
            asset_info['warning'] = f'.meta file not found: {meta_path}'
        asset_info['png_info'] = inspect_png(str(asset_path))
        if meta_path.exists():
            asset_info['meta_info'] = parse_unity_meta(str(meta_path))
            asset_info['status'] = 'ok'
        else:
            asset_info['status'] = 'partial'
        report['assets'].append(asset_info)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f'Asset report written to: {output_path}')
    print('\n=== ASSET INSPECTION SUMMARY ===')
    for asset in report['assets']:
        print(f"\n{asset['relative_path']}:")
        print(f"  Status: {asset['status']}")
        if asset['png_info']:
            png = asset['png_info']
            print(f"  PNG: {png['width']}x{png['height']}, mode={png['mode']}, alpha={png['has_alpha']}")
        if asset['meta_info']:
            meta = asset['meta_info']
            print(f"  Meta: spriteMode={meta.get('spriteMode')}, pixelsPerUnit={meta.get('pixelsPerUnit')}, filterMode={meta.get('filterMode')}")
            print(f"  Sprite rects: {len(meta.get('spriteRects', []))}")
            if meta.get('spriteRects'):
                for i, rect in enumerate(meta['spriteRects'][:5]):
                    print(f"    [{i}] x={rect['x']}, y={rect['y']}, w={rect['width']}, h={rect['height']}")
    has_errors = any(a['status']=='error' for a in report['assets'])
    if has_errors:
        print('\nERROR: Some assets failed inspection', file=sys.stderr)
        sys.exit(1)
    return 0

if __name__ == '__main__':
    sys.exit(main())

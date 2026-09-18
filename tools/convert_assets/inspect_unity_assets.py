#!/usr/bin/env python3
"""Inspect Unity PNG and .meta files to extract real sprite slicing information."""

import argparse
import json
import os
import sys
from pathlib import Path
from PIL import Image


def parse_yaml_like_meta(content: str) -> dict:
    """Parse Unity .meta file YAML-like format."""
    result = {}
    lines = content.split('\n')
    stack = [(result, -1)]
    current_list = None
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        content_part = stripped
        while len(stack) > 1 and stack[-1][1] >= indent:
            stack.pop()
            current_list = None
        current_dict = stack[-1][0]
        if content_part.startswith('- '):
            item_content = content_part[2:].strip()
            if current_list is not None:
                if ':' in item_content:
                    key, val = item_content.split(':', 1)
                    key = key.strip()
                    val = val.strip()
                    new_item = {key: parse_value(val) if val else {}}
                    current_list.append(new_item)
                    if not val:
                        stack.append((new_item[key], indent + 2))
                else:
                    current_list.append(parse_value(item_content))
            i += 1
            continue
        if ':' in content_part:
            colon_idx = content_part.index(':')
            key = content_part[:colon_idx].strip()
            value = content_part[colon_idx + 1:].strip()
            if value:
                current_dict[key] = parse_value(value)
                current_list = None
            else:
                next_i = i + 1
                while next_i < len(lines) and not lines[next_i].strip():
                    next_i += 1
                if next_i < len(lines):
                    next_line = lines[next_i]
                    next_stripped = next_line.strip()
                    if next_stripped.startswith('- '):
                        current_dict[key] = []
                        current_list = current_dict[key]
                    else:
                        current_dict[key] = {}
                        stack.append((current_dict[key], indent))
                        current_list = None
                else:
                    current_dict[key] = {}
        i += 1
    return result


def parse_value(value_str: str):
    if not value_str:
        return None
    if (value_str.startswith('"') and value_str.endswith('"')) or (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False
    if value_str.lower() in ('null', '~'):
        return None
    try:
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass
    return value_str


def extract_sprites_from_meta(meta_path: str) -> dict:
    result = {'fileType': None, 'guid': None, 'spriteMode': None, 'spriteMode_raw': None, 'pixelsPerUnit': None, 'filterMode': None, 'compression': None, 'maxTextureSize': None, 'textureCompression': None, 'spritesheet': [], 'sprites': [], 'raw_content': None, 'error': None, 'parse_method': None}
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            content = f.read()
            result['raw_content'] = content
        parsed = parse_yaml_like_meta(content)
        result['parse_method'] = 'yaml_parser'
        result['fileType'] = parsed.get('fileID')
        result['guid'] = parsed.get('guid')
        if 'spriteSettings' in parsed:
            settings = parsed['spriteSettings']
            result['spriteMode_raw'] = settings.get('spriteMode')
            mode_val = settings.get('spriteMode')
            if isinstance(mode_val, int):
                mode_map = {0: 'Single', 1: 'Multiple', 2: 'Polygon'}
                result['spriteMode'] = mode_map.get(mode_val, f'Unknown({mode_val})')
            result['pixelsPerUnit'] = settings.get('pixelsPerUnit')
            result['filterMode'] = settings.get('filterMode')
            result['maxTextureSize'] = settings.get('maxTextureSize')
            result['textureCompression'] = settings.get('textureCompression')
            result['compression'] = settings.get('compression')
        spritesheet = None
        if 'spritesheet' in parsed and parsed['spritesheet']:
            spritesheet = parsed['spritesheet']
        if 'sprites' in parsed and parsed['sprites']:
            spritesheet = parsed['sprites']
        for key in ['textureSettings', 'TextureSettings', 'm_TextureSettings']:
            if key in parsed and isinstance(parsed[key], dict):
                if 'spritesheet' in parsed[key]:
                    spritesheet = parsed[key]['spritesheet']
                elif 'sprites' in parsed[key]:
                    spritesheet = parsed[key]['sprites']
        if spritesheet:
            if isinstance(spritesheet, list):
                result['spritesheet'] = spritesheet
                result['sprites'] = spritesheet
            elif isinstance(spritesheet, dict):
                if 'sprites' in spritesheet:
                    result['spritesheet'] = spritesheet
                    result['sprites'] = spritesheet['sprites']
        if 'data' in parsed and isinstance(parsed['data'], dict):
            if 'sprites' in parsed['data']:
                result['sprites'] = parsed['data']['sprites']
    except Exception as e:
        result['error'] = str(e)
        result['parse_method'] = 'failed'
    return result


def inspect_png(png_path: str) -> dict:
    result = {'filename': os.path.basename(png_path), 'width': None, 'height': None, 'mode': None, 'has_alpha': False, 'format': None, 'error': None}
    try:
        with Image.open(png_path) as img:
            result['width'] = img.width
            result['height'] = img.height
            result['mode'] = img.mode
            result['has_alpha'] = img.mode in ('RGBA', 'LA', 'P') and 'transparency' in img.info
            result['format'] = img.format
    except Exception as e:
        result['error'] = str(e)
    return result


def main():
    parser = argparse.ArgumentParser(description='Inspect Unity PNG and .meta files')
    parser.add_argument('--unity-root', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--assets', nargs='+', default=['Assets/Sprites/characters.png', 'Assets/Sprites/animations.png'])
    args = parser.parse_args()
    unity_root = Path(args.unity_root).resolve()
    output_path = Path(args.output).resolve()
    if not unity_root.exists():
        print(f'ERROR: Unity root not found: {unity_root}', file=sys.stderr)
        sys.exit(1)
    report = {'unity_root': str(unity_root), 'assets': []}
    for asset_rel_path in args.assets:
        asset_path = unity_root / asset_rel_path
        meta_path = unity_root / f'{asset_rel_path}.meta'
        asset_info = {'relative_path': asset_rel_path, 'absolute_path': str(asset_path), 'png_info': None, 'meta_info': None, 'status': 'pending'}
        if not asset_path.exists():
            asset_info['status'] = 'error'
            asset_info['error'] = f'PNG file not found: {asset_path}'
            report['assets'].append(asset_info)
            continue
        asset_info['png_info'] = inspect_png(str(asset_path))
        if not meta_path.exists():
            asset_info['status'] = 'warning'
            asset_info['warning'] = f'.meta file not found: {meta_path}'
            report['assets'].append(asset_info)
            continue
        asset_info['meta_info'] = extract_sprites_from_meta(str(meta_path))
        meta_info = asset_info['meta_info']
        if meta_info.get('error'):
            asset_info['status'] = 'error'
            asset_info['error'] = meta_info['error']
        elif meta_info.get('spriteMode') == 'Multiple' and len(meta_info.get('sprites', [])) == 0:
            asset_info['status'] = 'error'
            asset_info['error'] = 'spriteMode is Multiple but 0 sprites found - parser may need fixing'
        else:
            asset_info['status'] = 'ok'
        report['assets'].append(asset_info)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'Asset report written to: {output_path}')
    print('\n=== ASSET INSPECTION SUMMARY ===')
    for asset in report['assets']:
        print(f"\n{asset['relative_path']}:")
        print(f"  Status: {asset['status']}")
        if asset.get('error'):
            print(f"  ERROR: {asset['error']}")
        if asset.get('warning'):
            print(f"  WARNING: {asset['warning']}")
        if asset['png_info']:
            png = asset['png_info']
            print(f"  PNG: {png['width']}x{png['height']}, mode={png['mode']}, alpha={png['has_alpha']}")
        if asset['meta_info']:
            meta = asset['meta_info']
            print(f"  Meta:")
            print(f"    parse_method: {meta.get('parse_method')}")
            print(f"    spriteMode: {meta.get('spriteMode')} ({meta.get('spriteMode_raw')})")
            print(f"    pixelsPerUnit: {meta.get('pixelsPerUnit')}")
            print(f"    filterMode: {meta.get('filterMode')}")
            print(f"    maxTextureSize: {meta.get('maxTextureSize')}")
            print(f"    textureCompression: {meta.get('textureCompression')}")
            sprites = meta.get('sprites', [])
            print(f"    sprites: {len(sprites)}")
            if sprites:
                print(f"    First 5 sprites:")
                for i, sprite in enumerate(sprites[:5]):
                    if isinstance(sprite, dict):
                        rect = sprite.get('rect', {})
                        pivot = sprite.get('pivot', {})
                        print(f"      [{i}] name={sprite.get('name')}, rect=({rect.get('x')},{rect.get('y')},{rect.get('width')}x{rect.get('height')}), pivot=({pivot.get('x')},{pivot.get('y')})")
                    else:
                        print(f"      [{i}] {sprite}")
    has_errors = any(a['status'] == 'error' for a in report['assets'])
    if has_errors:
        print('\nERROR: Some assets failed inspection', file=sys.stderr)
        sys.exit(1)
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Inspect Unity PNG and .meta files to extract real sprite slicing information using PyYAML."""

import argparse
import json
import os
import sys
from pathlib import Path
from PIL import Image

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(1)


def extract_sprites_from_meta(meta_path: str) -> dict:
    """Extract sprite information from Unity .meta file using PyYAML."""
    result = {
        'fileType': None, 'guid': None, 'spriteMode': None, 'spriteMode_raw': None,
        'pixelsPerUnit': None, 'filterMode': None, 'compression': None,
        'maxTextureSize': None, 'textureCompression': None, 'spritesheet': [],
        'sprites': [], 'raw_content': None, 'error': None, 'parse_method': None
    }
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            content = f.read()
            result['raw_content'] = content
        parsed = yaml.safe_load(content)
        result['parse_method'] = 'pyyaml'
        if not isinstance(parsed, dict):
            result['error'] = f'Expected dict, got {type(parsed)}'
            result['parse_method'] = 'failed'
            return result
        result['fileType'] = parsed.get('fileID')
        result['guid'] = parsed.get('guid')
        texture_importer = parsed.get('TextureImporter', {})
        if not isinstance(texture_importer, dict): texture_importer = {}
        result['spriteMode_raw'] = texture_importer.get('spriteMode')
        mode_val = texture_importer.get('spriteMode')
        if isinstance(mode_val, int):
            mode_map = {0: 'Single', 1: 'Multiple', 2: 'Polygon'}
            result['spriteMode'] = mode_map.get(mode_val, f'Unknown({mode_val})')
        result['pixelsPerUnit'] = texture_importer.get('pixelsPerUnit')
        result['filterMode'] = texture_importer.get('filterMode')
        result['maxTextureSize'] = texture_importer.get('maxTextureSize')
        result['textureCompression'] = texture_importer.get('textureCompression')
        result['compression'] = texture_importer.get('compression')
        sprite_sheet = texture_importer.get('spriteSheet', {})
        if not isinstance(sprite_sheet, dict): sprite_sheet = {}
        sprites = sprite_sheet.get('sprites', [])
        if not isinstance(sprites, list): sprites = []
        result['spritesheet'] = sprite_sheet
        result['sprites'] = sprites
        if not sprites:
            alt_sprite_sheet = parsed.get('spriteSheet', {})
            if isinstance(alt_sprite_sheet, dict):
                alt_sprites = alt_sprite_sheet.get('sprites', [])
                if isinstance(alt_sprites, list) and len(alt_sprites) > 0:
                    result['spritesheet'] = alt_sprite_sheet
                    result['sprites'] = alt_sprites
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
    parser.add_argument('--debug-images', help='Output directory for debug images')
    args = parser.parse_args()
    unity_root = Path(args.unity_root).resolve()
    output_path = Path(args.output).resolve()
    debug_dir = Path(args.debug_images).resolve() if args.debug_images else None
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
            asset_info['error'] = f'spriteMode is Multiple but 0 sprites found - parser failed. spriteMode_raw={meta_info.get("spriteMode_raw")}'
        else:
            asset_info['status'] = 'ok'
        report['assets'].append(asset_info)
        if debug_dir and asset_info['png_info'] and meta_info.get('sprites'):
            try:
                generate_debug_image(asset_path, meta_info['sprites'], debug_dir / f"{Path(asset_rel_path).stem}_annotated.png")
            except Exception as e:
                print(f"Warning: Could not generate debug image for {asset_rel_path}: {e}", file=sys.stderr)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'Asset report written to: {output_path}')
    print('\n=== ASSET INSPECTION SUMMARY ===')
    for asset in report['assets']:
        print(f"\n{asset['relative_path']}:")
        print(f"  Status: {asset['status']}")
        if asset.get('error'): print(f"  ERROR: {asset['error']}")
        if asset.get('warning'): print(f"  WARNING: {asset['warning']}")
        if asset['png_info']:
            png = asset['png_info']
            print(f"  PNG: {png['width']}x{png['height']}, mode={png['mode']}, alpha={png['has_alpha']}")
        if asset['meta_info']:
            meta = asset['meta_info']
            print(f"  Meta:")
            print(f"    parse_method: {meta.get('parse_method')}")
            print(f"    spriteMode: {meta.get('spriteMode')} (raw: {meta.get('spriteMode_raw')})")
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


def generate_debug_image(png_path: str, sprites: list, output_path: Path):
    """Generate debug image with rectangles drawn for each sprite."""
    from PIL import ImageDraw
    img = Image.open(png_path).convert('RGBA')
    draw = ImageDraw.Draw(img)
    for i, sprite in enumerate(sprites):
        if not isinstance(sprite, dict): continue
        rect = sprite.get('rect', {})
        if not rect: continue
        x = rect.get('x', 0)
        y = rect.get('y', 0)
        w = rect.get('width', 32)
        h = rect.get('height', 32)
        y_pil = img.height - y - h
        draw.rectangle([x, y_pil, x + w, y_pil + h], outline='red', width=1)
        if i < 50:
            draw.text((x + 2, y_pil + 2), str(i), fill='yellow')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Debug image saved to: {output_path}")


if __name__ == '__main__':
    sys.exit(main())

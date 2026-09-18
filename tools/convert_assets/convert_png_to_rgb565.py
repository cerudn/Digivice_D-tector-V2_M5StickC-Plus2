#!/usr/bin/env python3
"""Convert Unity PNG assets to RGB565 C++ headers using asset-report.json."""

import argparse
import json
import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np


def rgb888_to_rgb565(r, g, b):
    """Convert RGB888 to RGB565."""
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def extract_sprite_rgb565(img: Image.Image, x: int, y_unity: int, w: int, h: int) -> np.ndarray:
    """Extract a sprite from PNG and convert to RGB565 array.
    
    Unity uses bottom-left origin, PIL uses top-left.
    Convert: y_pil = img.height - y_unity - h
    """
    y_pil = img.height - y_unity - h
    sprite = img.crop((x, y_pil, x + w, y_pil + h)).convert('RGB')
    pixels = np.array(sprite, dtype=np.uint16)
    rgb565 = np.zeros((h, w), dtype=np.uint16)
    for row in range(h):
        for col in range(w):
            r, g, b = pixels[row, col]
            rgb565[row, col] = rgb888_to_rgb565(r, g, b)
    return rgb565


def generate_cpp_header(sprite_name: str, rgb565: np.ndarray, output_path: Path):
    """Generate C++ header with RGB565 array."""
    h, w = rgb565.shape
    symbol = sprite_name.replace('/', '_').replace('.', '_').replace('-', '_')
    
    lines = [
        f'// Auto-generated sprite header',
        f'#ifndef {symbol.upper()}_H',
        f'#define {symbol.upper()}_H',
        f'',
        f'#include <stdint.h>',
        f'',
        f'// Sprite: {sprite_name}',
        f'// Size: {w}x{h}',
        f'// Format: RGB565',
        f'// Bytes: {w * h * 2}',
        f'',
        f'static const uint16_t {symbol}[{h * w}] = {{'
    ]
    
    # Format as comma-separated hex values, 16 per line
    flat = rgb565.flatten()
    for i in range(0, len(flat), 16):
        chunk = flat[i:i+16]
        hex_vals = [f'0x{v:04x}' for v in chunk]
        lines.append('  ' + ', '.join(hex_vals) + ',')
    
    lines.extend([
        '};',
        f'',
        f'#endif // {symbol.upper()}_H'
    ])
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description='Convert Unity PNG assets to RGB565')
    parser.add_argument('--unity-root', required=True, help='Path to Unity repository root')
    parser.add_argument('--asset-report', required=True, help='Path to asset-report.json')
    parser.add_argument('--output-dir', required=True, help='Output directory for converted assets')
    
    args = parser.parse_args()
    
    unity_root = Path(args.unity_root).resolve()
    report_path = Path(args.asset_report).resolve()
    output_dir = Path(args.output_dir).resolve()
    
    if not unity_root.exists():
        print(f'ERROR: Unity root not found: {unity_root}', file=sys.stderr)
        sys.exit(1)
    
    if not report_path.exists():
        print(f'ERROR: Asset report not found: {report_path}', file=sys.stderr)
        sys.exit(1)
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    print(f'Converting assets from {unity_root}')
    print(f'Output directory: {output_dir}')
    
    total_sprites = 0
    successful = 0
    failed = 0
    
    for asset in report.get('assets', []):
        if asset.get('status') != 'ok':
            continue
        
        rel_path = asset['relative_path']
        meta_info = asset.get('meta_info', {})
        sprites = meta_info.get('sprites', [])
        
        if not sprites:
            print(f'\nERROR: {rel_path} has 0 sprites in asset-report.json')
            failed += 1
            continue
        
        png_path = unity_root / rel_path
        if not png_path.exists():
            print(f'\nERROR: PNG not found: {png_path}')
            failed += 1
            continue
        
        with Image.open(png_path) as img:
            img = img.convert('RGB')
            print(f'\nProcessing: {rel_path}')
            print(f'  Loaded: {img.width}x{img.height}, mode={img.mode}')
            print(f'  Found {len(sprites)} sprite rect(s)')
            
            # Determine output subdirectory
            asset_name = Path(rel_path).stem
            category = 'characters' if 'character' in rel_path.lower() else 'animations' if 'anim' in rel_path.lower() else 'unknown'
            category_dir = output_dir / category
            
            for i, sprite in enumerate(sprites):
                if not isinstance(sprite, dict):
                    continue
                
                rect = sprite.get('rect', {})
                if not rect:
                    continue
                
                x = rect.get('x', 0)
                y = rect.get('y', 0)
                w = rect.get('width', 32)
                h = rect.get('height', 32)
                name = sprite.get('name', f'{asset_name}_{i}')
                
                # Validate sprite size
                if w != 32 or h != 32:
                    print(f'  WARNING: Sprite {name} has non-standard size {w}x{h}')
                
                try:
                    rgb565 = extract_sprite_rgb565(img, x, y, w, h)
                    output_file = category_dir / f'{name}.h'
                    generate_cpp_header(name, rgb565, output_file)
                    print(f'  Sprite {i}: {x},{y},{w}x{h} -> {output_file.name}')
                    successful += 1
                except Exception as e:
                    print(f'  ERROR converting sprite {i}: {e}')
                    failed += 1
                
                total_sprites += 1
    
    print(f'\n=== CONVERSION SUMMARY ===')
    print(f'Total sprites: {total_sprites}')
    print(f'Successful: {successful}')
    print(f'Failed: {failed}')
    
    # Validation: fail if we expected sprites but got 0
    if total_sprites > 0 and successful == 0:
        print('\nERROR: Expected sprites but conversion produced 0 outputs', file=sys.stderr)
        sys.exit(1)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

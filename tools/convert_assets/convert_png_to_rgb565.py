#!/usr/bin/env python3
"""Convert Unity PNG assets to RGB565 format for ESP32."""

import argparse
import json
import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np


def image_to_rgb565_array(img: Image.Image) -> np.ndarray:
    if img.mode != 'RGB': img = img.convert('RGB')
    pixels = np.array(img)
    r = (pixels[:,:,0] & 0xF8) << 8
    g = (pixels[:,:,1] & 0xFC) << 3
    b = (pixels[:,:,2]) >> 3
    return (r | g | b).astype(np.uint16)


def extract_sprite(img: Image.Image, rect: dict) -> Image.Image:
    x, y, w, h = rect['x'], rect['y'], rect['width'], rect['height']
    y_pil = img.height - y - h
    return img.crop((x, y_pil, x + w, y_pil + h))


def save_rgb565_header(data: np.ndarray, output_path: str, symbol_name: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f'// Auto-generated RGB565 sprite data\n// Symbol: {symbol_name}\n// Dimensions: {data.shape[1]}x{data.shape[0]}\n// Total bytes: {data.size * 2}\n\n')
        f.write(f'#ifndef {symbol_name.upper()}_H\n#define {symbol_name.upper()}_H\n\n#include <stdint.h>\n\n')
        f.write(f'constexpr uint16_t {symbol_name}_width = {data.shape[1]};\n')
        f.write(f'constexpr uint16_t {symbol_name}_height = {data.shape[0]};\n')
        f.write(f'constexpr uint16_t {symbol_name}_size = {data.size * 2};\n\n')
        f.write(f'constexpr uint16_t {symbol_name}[] PROGMEM = {{\n')
        for row_idx in range(data.shape[0]):
            hex_values = [f'0x{val:04X}' for val in data[row_idx]]
            f.write(f'  {", ".join(hex_values)},\n')
        f.write(f'}};\n\n#endif // {symbol_name.upper()}_H\n')


def main():
    parser = argparse.ArgumentParser(description='Convert Unity PNG to RGB565')
    parser.add_argument('--unity-root', required=True)
    parser.add_argument('--asset-report', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    unity_root = Path(args.unity_root).resolve()
    report_path = Path(args.asset_report).resolve()
    output_dir = Path(args.output_dir).resolve()
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    if not report.get('assets'):
        print('ERROR: No assets found in report', file=sys.stderr)
        sys.exit(1)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'characters').mkdir(exist_ok=True)
    (output_dir / 'animations').mkdir(exist_ok=True)
    (output_dir / 'ui').mkdir(exist_ok=True)
    print(f'Converting assets from: {unity_root}\nOutput directory: {output_dir}')
    conversion_stats = {'total_sprites':0,'successful':0,'failed':0,'sprites':[]}
    for asset in report['assets']:
        if asset['status'] not in ('ok','partial','warning'):
            print(f"Skipping {asset['relative_path']}: status={asset['status']}")
            continue
        png_path = Path(asset['absolute_path'])
        meta_info = asset.get('meta_info', {})
        print(f"\nProcessing: {asset['relative_path']}")
        try:
            with Image.open(png_path) as img:
                img = img.convert('RGB')
                print(f"  Loaded: {img.width}x{img.height}, mode={img.mode}")
        except Exception as e:
            print(f"  ERROR loading PNG: {e}")
            conversion_stats['failed'] += 1
            continue
        sprite_rects = meta_info.get('spriteRects', [])
        if not sprite_rects:
            print(f"  No sprite rects found - using full image")
            sprite_rects = [{'x':0,'y':0,'width':img.width,'height':img.height}]
        print(f"  Found {len(sprite_rects)} sprite rect(s)")
        category = 'characters' if 'characters' in asset['relative_path'] else ('animations' if 'animations' in asset['relative_path'] else 'ui')
        for i, rect in enumerate(sprite_rects):
            conversion_stats['total_sprites'] += 1
            try:
                sprite_img = extract_sprite(img, rect)
                rgb565_data = image_to_rgb565_array(sprite_img)
                base_name = Path(asset['relative_path']).stem
                symbol_name = f"{base_name}_sprite_{i:03d}"
                output_filename = f"{base_name}_sprite_{i:03d}.h"
                output_path = output_dir / category / output_filename
                save_rgb565_header(rgb565_data, str(output_path), symbol_name)
                conversion_stats['successful'] += 1
                conversion_stats['sprites'].append({'source':asset['relative_path'],'sprite_index':i,'rect':rect,'output_file':str(output_path),'symbol':symbol_name,'dimensions':{'width':int(sprite_img.width),'height':int(sprite_img.height)}})
                print(f"  Sprite {i}: {rect['width']}x{rect['height']} -> {output_filename}")
            except Exception as e:
                print(f"  ERROR converting sprite {i}: {e}")
                conversion_stats['failed'] += 1
    print(f"\n=== CONVERSION SUMMARY ===\nTotal sprites: {conversion_stats['total_sprites']}\nSuccessful: {conversion_stats['successful']}\nFailed: {conversion_stats['failed']}")
    return 0 if conversion_stats['failed'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())

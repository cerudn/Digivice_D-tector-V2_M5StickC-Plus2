#!/usr/bin/env python3
"""
Build reproducible Unity-to-ESP32 asset mapping.

This tool reads:
- Unity repository (PNG + .meta files)
- Generated firmware assets (characters/*.h, animations/*.h)

And produces:
- assets/asset_manifest.json - authoritative mapping from Unity to generated assets
- Docs/ASSET_MAPPING.md - human-readable report

Identity levels:
- RAW_DISCOVERED: Sprite exists in Unity metadata
- ASSET_MATCHED: Generated header content matches Unity sprite RGB565 data
- SEMANTICALLY_MAPPED: We know what character/animation this represents
"""

import json
import os
import sys
import re
from pathlib import Path
from enum import Enum

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow required. Install with: pip install pillow")
    sys.exit(1)


class MatchStatus(Enum):
    RAW_DISCOVERED = "RAW_DISCOVERED"
    ASSET_MATCHED = "ASSET_MATCHED"
    SEMANTICALLY_MAPPED = "SEMANTICALLY_MAPPED"
    UNMATCHED = "UNMATCHED"
    AMBIGUOUS = "AMBIGUOUS"
    MISSING_METADATA = "MISSING_METADATA"


def rgb888_to_rgb565(r, g, b):
    """Convert RGB888 to RGB565 using the same formula as convert_png_to_rgb565.py"""
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def extract_sprite_from_png(png_path, rect):
    """Extract sprite pixels from PNG and convert to RGB565 array."""
    try:
        img = Image.open(png_path).convert('RGB')
        
        # Unity Y is from bottom, PIL Y is from top
        x = rect['x']
        y_unity = rect['y']
        w = rect['width']
        h = rect['height']
        
        # Convert Unity Y to PIL Y
        y_pil = img.height - y_unity - h
        
        # Crop the sprite
        sprite = img.crop((x, y_pil, x + w, y_pil + h))
        
        # Convert to RGB565 array
        rgb565_data = []
        for py in range(h):
            for px in range(w):
                r, g, b = sprite.getpixel((px, py))
                rgb565_data.append(rgb888_to_rgb565(r, g, b))
        
        return tuple(rgb565_data)
    except Exception as e:
        print(f"Warning: Could not extract sprite from {png_path}: {e}")
        return None


def parse_cpp_header(header_path):
    """Parse a C++ header file to extract the uint16_t array."""
    try:
        with open(header_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the array definition: static const uint16_t <symbol>[<size>] = { ... };
        match = re.search(r'static\s+const\s+uint16_t\s+(\w+)\s*\[\s*(\d+)\s*\]\s*=\s*\{([^}]+)\}', content, re.DOTALL)
        
        if not match:
            return None, None, None
        
        symbol = match.group(1)
        size = int(match.group(2))
        array_str = match.group(3)
        
        # Parse the array values
        values = []
        for val_str in array_str.split(','):
            val_str = val_str.strip()
            if val_str:
                if val_str.lower().startswith('0x'):
                    values.append(int(val_str, 16))
                else:
                    values.append(int(val_str))
        
        return symbol, size, tuple(values)
    except Exception as e:
        print(f"Warning: Could not parse header {header_path}: {e}")
        return None, None, None


def parse_meta_file(meta_path):
    """Parse Unity .meta file to extract sprite information."""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            data = yaml.safe_load(content.replace('!u!', '!!'))
        except:
            data = {}
        
        sprites = []
        
        if data:
            texture_importer = data.get('TextureImporter', {})
            sprite_sheet = texture_importer.get('spriteSheet', {})
            sprites_list = sprite_sheet.get('sprites', [])
            
            for sprite in sprites_list:
                rect = sprite.get('rect', {})
                pivot = sprite.get('pivot', {})
                
                if not rect:
                    continue
                
                sprite_info = {
                    'name': sprite.get('name', None),
                    'rect': {
                        'x': rect.get('x'),
                        'y': rect.get('y'),
                        'width': rect.get('width'),
                        'height': rect.get('height'),
                    },
                    'pivot': {
                        'x': pivot.get('x'),
                        'y': pivot.get('y'),
                    } if pivot else None,
                }
                
                if any(v is None for v in sprite_info['rect'].values()):
                    continue
                
                sprites.append(sprite_info)
        
        return sprites
    except Exception as e:
        print(f"Warning: Could not parse {meta_path}: {e}")
        return []


def scan_unity_spritesheets(unity_root):
    """Scan Unity repository for spritesheets and their .meta files."""
    spritesheets = []
    
    search_patterns = [
        '**/characters.png',
        '**/animations.png',
        '**/Sprites/*.png',
        '**/Resources/Sprites/*.png',
    ]
    
    for pattern in search_patterns:
        for png_file in Path(unity_root).glob(pattern):
            meta_file = png_file.with_suffix('.png.meta')
            if meta_file.exists():
                sprites = parse_meta_file(meta_file)
                if sprites:
                    spritesheets.append({
                        'png_path': str(png_file.relative_to(unity_root)),
                        'meta_path': str(meta_file.relative_to(unity_root)),
                        'sprites': sprites,
                    })
    
    return spritesheets


def scan_generated_assets(assets_dir):
    """Scan generated firmware assets and parse their content."""
    characters = []
    animations = []
    
    characters_dir = Path(assets_dir) / 'characters'
    animations_dir = Path(assets_dir) / 'animations'
    
    if characters_dir.exists():
        for h_file in sorted(characters_dir.glob('characters_*.h')):
            symbol, size, values = parse_cpp_header(h_file)
            if symbol and values:
                characters.append({
                    'file': str(h_file.relative_to(assets_dir)),
                    'symbol': symbol,
                    'size': size,
                    'values': values,
                })
    
    if animations_dir.exists():
        for h_file in sorted(animations_dir.glob('animations_*.h')):
            symbol, size, values = parse_cpp_header(h_file)
            if symbol and values:
                animations.append({
                    'file': str(h_file.relative_to(assets_dir)),
                    'symbol': symbol,
                    'size': size,
                    'values': values,
                })
    
    return characters, animations


def build_manifest(unity_root, assets_dir):
    """Build the asset manifest mapping Unity to generated assets using RGB565 content matching."""
    spritesheets = scan_unity_spritesheets(unity_root)
    characters, animations = scan_generated_assets(assets_dir)
    
    # Build lookup maps: RGB565 tuple -> list of generated assets
    char_lookup = {}
    for char in characters:
        key = char['values']
        if key not in char_lookup:
            char_lookup[key] = []
        char_lookup[key].append(char)
    
    anim_lookup = {}
    for anim in animations:
        key = anim['values']
        if key not in anim_lookup:
            anim_lookup[key] = []
        anim_lookup[key].append(anim)
    
    manifest = {
        'source_repository': 'cerudn/Digivice_D-tector-V2_Unity-',
        'unity_revision': 'unknown',
        'generated_at': str(Path(assets_dir).absolute()),
        'spritesheets': spritesheets,
        'generated_assets': {
            'characters': [{'file': c['file'], 'symbol': c['symbol'], 'size': c['size']} for c in characters],
            'animations': [{'file': a['file'], 'symbol': a['symbol'], 'size': a['size']} for a in animations],
        },
        'mapping': [],
        'statistics': {
            'total_generated': len(characters) + len(animations),
            'raw_discovered': 0,
            'asset_matched': 0,
            'semantically_mapped': 0,
            'unmatched': 0,
            'ambiguous': 0,
            'missing_metadata': 0,
        }
    }
    
    # Track which generated assets have been matched
    matched_chars = set()
    matched_anims = set()
    
    # Map character frames by content matching
    for sheet in spritesheets:
        png_path = Path(unity_root) / sheet['png_path']
        
        for sprite_idx, sprite in enumerate(sheet['sprites']):
            rect = sprite['rect']
            
            expected_rgb565 = extract_sprite_from_png(png_path, rect)
            
            if expected_rgb565 is None:
                manifest['statistics']['missing_metadata'] += 1
                continue
            
            manifest['statistics']['raw_discovered'] += 1
            
            matching_chars = char_lookup.get(expected_rgb565, [])
            
            mapping_entry = {
                'generated_symbol': None,
                'generated_file': None,
                'source': {
                    'png': sheet['png_path'],
                    'meta': sheet['meta_path'],
                    'sprite_name': sprite.get('name'),
                    'rect': rect,
                    'pivot': sprite.get('pivot'),
                },
                'identity': {
                    'asset_match': MatchStatus.UNMATCHED.value,
                    'character': None,
                    'animation': None,
                    'semantic_status': MatchStatus.RAW_DISCOVERED.value,
                }
            }
            
            if len(matching_chars) == 0:
                manifest['statistics']['unmatched'] += 1
            elif len(matching_chars) == 1:
                matched_char = matching_chars[0]
                mapping_entry['generated_symbol'] = matched_char['symbol']
                mapping_entry['generated_file'] = matched_char['file']
                mapping_entry['identity']['asset_match'] = MatchStatus.ASSET_MATCHED.value
                manifest['statistics']['asset_matched'] += 1
                matched_chars.add(matched_char['symbol'])
            else:
                mapping_entry['generated_symbol'] = matching_chars[0]['symbol']
                mapping_entry['generated_file'] = matching_chars[0]['file']
                mapping_entry['identity']['asset_match'] = MatchStatus.AMBIGUOUS.value
                mapping_entry['identity']['ambiguous_matches'] = [c['symbol'] for c in matching_chars]
                manifest['statistics']['ambiguous'] += 1
            
            manifest['mapping'].append(mapping_entry)
    
    # Add unmatched generated assets
    for char in characters:
        if char['symbol'] not in matched_chars:
            mapping_entry = {
                'generated_symbol': char['symbol'],
                'generated_file': char['file'],
                'source': None,
                'identity': {
                    'asset_match': MatchStatus.UNMATCHED.value,
                    'character': None,
                    'animation': None,
                    'semantic_status': MatchStatus.UNMATCHED.value,
                }
            }
            manifest['mapping'].append(mapping_entry)
    
    return manifest


def generate_mapping_report(manifest, output_path):
    """Generate human-readable mapping report."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Asset Mapping Report\n\n")
        f.write(f"Source: {manifest['source_repository']}\n\n")
        
        f.write("## Statistics\n\n")
        stats = manifest['statistics']
        f.write(f"- Total generated assets: {stats['total_generated']}\n")
        f.write(f"- RAW_DISCOVERED: {stats['raw_discovered']}\n")
        f.write(f"- ASSET_MATCHED: {stats['asset_matched']}\n")
        f.write(f"- SEMANTICALLY_MAPPED: {stats['semantically_mapped']}\n")
        f.write(f"- UNMATCHED: {stats['unmatched']}\n")
        f.write(f"- AMBIGUOUS: {stats['ambiguous']}\n")
        f.write(f"- MISSING_METADATA: {stats['missing_metadata']}\n\n")
        
        f.write("## Asset Identity Strategy\n\n")
        f.write("Asset identity is determined by RGB565 content matching:\n")
        f.write("1. Extract sprite from Unity PNG using rect from .meta\n")
        f.write("2. Convert to RGB565 using: ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)\n")
        f.write("3. Compare against generated header content\n")
        f.write("4. ASSET_MATCHED: exactly one header matches\n")
        f.write("5. AMBIGUOUS: multiple headers match (visual duplicates)\n")
        f.write("6. UNMATCHED: no header matches\n\n")
        
        f.write("## Spritesheets\n\n")
        for sheet in manifest['spritesheets']:
            f.write(f"- {sheet['png_path']}\n")
            f.write(f"  - Meta: {sheet['meta_path']}\n")
            f.write(f"  - Sprites: {len(sheet['sprites'])}\n")
        
        f.write("\n## Sample Mappings\n\n")
        f.write("| Generated | Unity Sprite | Rect | Status |\n")
        f.write("|-----------|--------------|------|--------|\n")
        for entry in manifest['mapping'][:20]:
            gen = entry.get('generated_symbol', 'UNMATCHED') or 'UNMATCHED'
            src = entry.get('source', {})
            sprite_name = src.get('sprite_name', 'N/A') or 'N/A'
            rect = src.get('rect', {})
            if rect:
                rect_str = f"({rect.get('x','?')},{rect.get('y','?')}) {rect.get('width','?')}x{rect.get('height','?')}"
            else:
                rect_str = 'N/A'
            status = entry['identity']['asset_match']
            f.write(f"| {gen} | {sprite_name} | {rect_str} | {status} |\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Build Unity-to-ESP32 asset mapping')
    parser.add_argument('--unity-root', required=True, help='Path to Unity repository root')
    parser.add_argument('--assets-dir', required=True, help='Path to generated assets directory')
    parser.add_argument('--output', default='assets/asset_manifest.json', help='Output manifest path')
    parser.add_argument('--report', default='Docs/ASSET_MAPPING.md', help='Output report path')
    
    args = parser.parse_args()
    
    print(f"Scanning Unity repository: {args.unity_root}")
    print(f"Scanning generated assets: {args.assets_dir}")
    
    manifest = build_manifest(args.unity_root, args.assets_dir)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Written: {args.output}")
    
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    generate_mapping_report(manifest, args.report)
    print(f"Written: {args.report}")
    
    stats = manifest['statistics']
    print(f"\nSummary:")
    print(f"  TOTAL_GENERATED: {stats['total_generated']}")
    print(f"  RAW_DISCOVERED: {stats['raw_discovered']}")
    print(f"  ASSET_MATCHED: {stats['asset_matched']}")
    print(f"  SEMANTICALLY_MAPPED: {stats['semantically_mapped']}")
    print(f"  UNMATCHED: {stats['unmatched']}")
    print(f"  AMBIGUOUS: {stats['ambiguous']}")
    print(f"  MISSING_METADATA: {stats['missing_metadata']}")


if __name__ == '__main__':
    main()

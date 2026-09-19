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
- ASSET_MATCHED: Generated header RGB565 content matches Unity sprite
- SEMANTICALLY_MAPPED: We know what character/animation this represents
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timezone
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
        
        x = rect['x']
        y_unity = rect['y']
        w = rect['width']
        h = rect['height']
        
        # Convert Unity Y (from bottom) to PIL Y (from top)
        y_pil = img.height - y_unity - h
        
        sprite = img.crop((x, y_pil, x + w, y_pil + h))
        
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
        
        match = re.search(r'static\s+const\s+uint16_t\s+(\w+)\s*\[\s*(\d+)\s*\]\s*=\s*\{([^}]+)\}', content, re.DOTALL)
        
        if not match:
            return None, None, None
        
        symbol = match.group(1)
        size = int(match.group(2))
        array_str = match.group(3)
        
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
    """Scan Unity repository for spritesheets and their .meta files with deduplication."""
    spritesheets = []
    seen_paths = set()
    
    search_patterns = [
        '**/characters.png',
        '**/animations.png',
    ]
    
    for pattern in search_patterns:
        for png_file in Path(unity_root).glob(pattern):
            # Deduplicate by relative path
            rel_path = str(png_file.relative_to(unity_root))
            if rel_path in seen_paths:
                continue
            seen_paths.add(rel_path)
            
            meta_file = png_file.with_suffix('.png.meta')
            if meta_file.exists():
                sprites = parse_meta_file(meta_file)
                if sprites:
                    spritesheets.append({
                        'png_path': rel_path,
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


def get_lookup_for_sheet(sheet, char_lookup, anim_lookup):
    """Get the appropriate lookup map for a spritesheet based on its name."""
    png_name = Path(sheet['png_path']).name.lower()
    
    if 'characters' in png_name:
        return 'character', char_lookup
    elif 'animations' in png_name:
        return 'animation', anim_lookup
    else:
        # Default to character lookup for unknown sheets
        return 'unknown', char_lookup


def build_manifest(unity_root, assets_dir, unity_revision=None):
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
        'unity_revision': unity_revision or 'unknown',
        'generated_at': datetime.now(timezone.utc).isoformat(),
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
            'character_generated': len(characters),
            'character_matched': 0,
            'character_unmatched': 0,
            'animation_generated': len(animations),
            'animation_matched': 0,
            'animation_unmatched': 0,
        }
    }
    
    matched_chars = set()
    matched_anims = set()
    
    for sheet in spritesheets:
        png_path = Path(unity_root) / sheet['png_path']
        
        asset_type, lookup = get_lookup_for_sheet(sheet, char_lookup, anim_lookup)
        
        for sprite_idx, sprite in enumerate(sheet['sprites']):
            rect = sprite['rect']
            
            expected_rgb565 = extract_sprite_from_png(png_path, rect)
            
            if expected_rgb565 is None:
                manifest['statistics']['missing_metadata'] += 1
                continue
            
            manifest['statistics']['raw_discovered'] += 1
            
            matching = lookup.get(expected_rgb565, [])
            
            mapping_entry = {
                'generated_symbol': None,
                'generated_file': None,
                'asset_type': asset_type,
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
            
            if len(matching) == 0:
                manifest['statistics']['unmatched'] += 1
                if asset_type == 'character':
                    manifest['statistics']['character_unmatched'] += 1
                elif asset_type == 'animation':
                    manifest['statistics']['animation_unmatched'] += 1
            elif len(matching) == 1:
                matched_asset = matching[0]
                mapping_entry['generated_symbol'] = matched_asset['symbol']
                mapping_entry['generated_file'] = matched_asset['file']
                mapping_entry['identity']['asset_match'] = MatchStatus.ASSET_MATCHED.value
                manifest['statistics']['asset_matched'] += 1
                
                if asset_type == 'character':
                    manifest['statistics']['character_matched'] += 1
                    matched_chars.add(matched_asset['symbol'])
                elif asset_type == 'animation':
                    manifest['statistics']['animation_matched'] += 1
                    matched_anims.add(matched_asset['symbol'])
            else:
                mapping_entry['generated_symbol'] = matching[0]['symbol']
                mapping_entry['generated_file'] = matching[0]['file']
                mapping_entry['identity']['asset_match'] = MatchStatus.AMBIGUOUS.value
                mapping_entry['identity']['ambiguous_matches'] = [a['symbol'] for a in matching]
                manifest['statistics']['ambiguous'] += 1
            
            manifest['mapping'].append(mapping_entry)
    
    # Add unmatched generated assets
    for char in characters:
        if char['symbol'] not in matched_chars:
            mapping_entry = {
                'generated_symbol': char['symbol'],
                'generated_file': char['file'],
                'asset_type': 'character',
                'source': None,
                'identity': {
                    'asset_match': MatchStatus.UNMATCHED.value,
                    'character': None,
                    'animation': None,
                    'semantic_status': MatchStatus.UNMATCHED.value,
                }
            }
            manifest['mapping'].append(mapping_entry)
    
    for anim in animations:
        if anim['symbol'] not in matched_anims:
            mapping_entry = {
                'generated_symbol': anim['symbol'],
                'generated_file': anim['file'],
                'asset_type': 'animation',
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
        f.write(f"Source: {manifest['source_repository']}\n")
        f.write(f"Unity Revision: {manifest['unity_revision']}\n")
        f.write(f"Generated At: {manifest['generated_at']}\n\n")
        
        f.write("## Statistics\n\n")
        stats = manifest['statistics']
        f.write(f"- Total generated assets: {stats['total_generated']}\n")
        f.write(f"  - Characters: {stats['character_generated']}\n")
        f.write(f"  - Animations: {stats['animation_generated']}\n")
        f.write(f"- RAW_DISCOVERED: {stats['raw_discovered']}\n")
        f.write(f"- ASSET_MATCHED: {stats['asset_matched']}\n")
        f.write(f"  - Characters: {stats['character_matched']}\n")
        f.write(f"  - Animations: {stats['animation_matched']}\n")
        f.write(f"- SEMANTICALLY_MAPPED: {stats['semantically_mapped']}\n")
        f.write(f"- UNMATCHED: {stats['unmatched']}\n")
        f.write(f"  - Characters: {stats['character_unmatched']}\n")
        f.write(f"  - Animations: {stats['animation_unmatched']}\n")
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
        f.write("| Generated | Type | Unity Sprite | Rect | Status |\n")
        f.write("|-----------|------|--------------|------|--------|\n")
        for entry in manifest['mapping'][:20]:
            gen = entry.get('generated_symbol', 'UNMATCHED') or 'UNMATCHED'
            asset_type = entry.get('asset_type', '?')
            src = entry.get('source', {})
            sprite_name = src.get('sprite_name', 'N/A') or 'N/A'
            rect = src.get('rect', {})
            if rect:
                rect_str = f"({rect.get('x','?')},{rect.get('y','?')}) {rect.get('width','?')}x{rect.get('height','?')}"
            else:
                rect_str = 'N/A'
            status = entry['identity']['asset_match']
            f.write(f"| {gen} | {asset_type} | {sprite_name} | {rect_str} | {status} |\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Build Unity-to-ESP32 asset mapping')
    parser.add_argument('--unity-root', required=True, help='Path to Unity repository root')
    parser.add_argument('--assets-dir', required=True, help='Path to generated assets directory')
    parser.add_argument('--unity-revision', default='unknown', help='Unity repository revision SHA')
    parser.add_argument('--output', default='assets/asset_manifest.json', help='Output manifest path')
    parser.add_argument('--report', default='Docs/ASSET_MAPPING.md', help='Output report path')
    
    args = parser.parse_args()
    
    print(f"Scanning Unity repository: {args.unity_root}")
    print(f"Unity revision: {args.unity_revision}")
    print(f"Scanning generated assets: {args.assets_dir}")
    
    manifest = build_manifest(args.unity_root, args.assets_dir, args.unity_revision)
    
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
    print(f"    - Characters: {stats['character_matched']}")
    print(f"    - Animations: {stats['animation_matched']}")
    print(f"  SEMANTICALLY_MAPPED: {stats['semantically_mapped']}")
    print(f"  UNMATCHED: {stats['unmatched']}")
    print(f"  AMBIGUOUS: {stats['ambiguous']}")
    print(f"  MISSING_METADATA: {stats['missing_metadata']}")


if __name__ == '__main__':
    main()

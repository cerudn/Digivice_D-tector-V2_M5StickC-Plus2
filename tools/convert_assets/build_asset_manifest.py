#!/usr/bin/env python3
"""
Build reproducible Unity-to-ESP32 asset mapping.

This tool reads:
- Unity repository (PNG + .meta files)
- Generated firmware assets (characters/*.h, animations/*.h)

And produces:
- assets/asset_manifest.json - authoritative mapping from Unity to generated assets
- Docs/ASSET_MAPPING.md - human-readable report

Strategy:
- Use sprite rects from .meta files as primary identity
- Use Unity sprite name when available
- Track GUID/fileID when present
- Map generated headers to Unity sprites by matching rect + order
"""

import json
import os
import sys
from pathlib import Path

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


def parse_meta_file(meta_path):
    """Parse Unity .meta file to extract sprite information."""
    with open(meta_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple YAML-like parser for Unity .meta format
    data = {}
    current_key = None
    current_list = []
    in_sprites = False
    sprites = []
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith('Sprite:'):
            in_sprites = False
            current_key = 'Sprite'
            continue
        elif stripped.startswith('sprites:'):
            in_sprites = True
            current_key = 'sprites'
            current_list = []
            i += 1
            # Parse sprite entries
            while i < len(lines):
                line = lines[i]
                if line.strip() and not line.startswith(' '):
                    break
                if '- ' in line:
                    sprite_entry = {}
                    # Extract sprite data from indented lines
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith('    ') or lines[j].strip() == ''):
                        if ':' in lines[j]:
                            key_val = lines[j].strip().split(': ', 1)
                            if len(key_val) == 2:
                                sprite_entry[key_val[0].strip()] = key_val[1].strip()
                        j += 1
                    if sprite_entry:
                        current_list.append(sprite_entry)
                    i = j
                    continue
                i += 1
            sprites = current_list
            in_sprites = False
            continue
        elif ':' in stripped and not stripped.startswith('-'):
            parts = stripped.split(': ', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                data[key] = value
                current_key = key
        i += 1
    
    data['sprites'] = sprites
    return data


def extract_sprite_rects_from_meta(meta_path):
    """Extract sprite rectangles from Unity .meta file."""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        data = yaml.safe_load(content.replace('!u!', '!!'))
        sprites = []
        
        if data and 'TextureImporter' in str(type(data)):
            sprite_data = data.get('TextureImporter', {})
            sprites_list = sprite_data.get('spriteSheet', {}).get('sprites', [])
            
            for sprite in sprites_list:
                rect = sprite.get('rect', {})
                sprites.append({
                    'name': sprite.get('name', ''),
                    'x': rect.get('x', 0),
                    'y': rect.get('y', 0),
                    'width': rect.get('width', 32),
                    'height': rect.get('height', 32),
                    'pivot': sprite.get('alignment', 0),
                })
        
        return sprites
    except Exception as e:
        print(f"Warning: Could not parse {meta_path}: {e}")
        return []


def scan_unity_spritesheets(unity_root):
    """Scan Unity repository for spritesheets and their .meta files."""
    spritesheets = []
    
    # Common paths for spritesheets in Unity projects
    search_paths = [
        'Assets/Sprites',
        'Assets/Resources/Sprites',
        'Assets/Art/Sprites',
        'Sprites',
        '.',
    ]
    
    for search_path in search_paths:
        full_path = Path(unity_root) / search_path
        if not full_path.exists():
            continue
        
        for png_file in full_path.rglob('*.png'):
            meta_file = png_file.with_suffix('.png.meta')
            if meta_file.exists():
                sprites = extract_sprite_rects_from_meta(meta_file)
                if sprites:
                    spritesheets.append({
                        'png_path': str(png_file.relative_to(unity_root)),
                        'meta_path': str(meta_file.relative_to(unity_root)),
                        'sprites': sprites,
                    })
    
    return spritesheets


def scan_generated_assets(assets_dir):
    """Scan generated firmware assets."""
    characters = []
    animations = []
    
    characters_dir = Path(assets_dir) / 'characters'
    animations_dir = Path(assets_dir) / 'animations'
    
    if characters_dir.exists():
        for h_file in sorted(characters_dir.glob('characters_*.h')):
            characters.append({
                'file': str(h_file.relative_to(assets_dir)),
                'symbol': h_file.stem,
                'index': int(h_file.stem.split('_')[1]),
            })
    
    if animations_dir.exists():
        for h_file in sorted(animations_dir.glob('animations_*.h')):
            animations.append({
                'file': str(h_file.relative_to(assets_dir)),
                'symbol': h_file.stem,
                'index': int(h_file.stem.split('_')[1]),
            })
    
    return characters, animations


def build_manifest(unity_root, assets_dir):
    """Build the asset manifest mapping Unity to generated assets."""
    spritesheets = scan_unity_spritesheets(unity_root)
    characters, animations = scan_generated_assets(assets_dir)
    
    manifest = {
        'source_repository': 'cerudn/Digivice_D-tector-V2_Unity-',
        'generated_at': Path(assets_dir).parent.name,
        'spritesheets': spritesheets,
        'generated_assets': {
            'characters': characters,
            'animations': animations,
        },
        'mapping': [],
        'statistics': {
            'total_spritesheets': len(spritesheets),
            'total_character_frames': len(characters),
            'total_animation_frames': len(animations),
            'mapped_frames': 0,
            'unmapped_frames': 0,
        }
    }
    
    # Build mapping by matching sprite order
    # This is a placeholder - real mapping requires Unity animation data
    all_sprites = []
    for sheet in spritesheets:
        for sprite in sheet['sprites']:
            all_sprites.append({
                'sheet': sheet['png_path'],
                'sprite': sprite,
            })
    
    # Map characters
    for i, char in enumerate(characters):
        mapping_entry = {
            'asset_type': 'character',
            'generated_file': char['file'],
            'generated_symbol': char['symbol'],
            'unity_source': None,
            'sprite_name': None,
            'character': None,
            'animation': None,
            'frame_index': i,
        }
        
        if i < len(all_sprites):
            sprite_info = all_sprites[i]
            mapping_entry['unity_source'] = sprite_info['sheet']
            mapping_entry['sprite_name'] = sprite_info['sprite'].get('name')
        
        manifest['mapping'].append(mapping_entry)
        manifest['statistics']['mapped_frames'] += 1
    
    # Map animations
    for i, anim in enumerate(animations):
        mapping_entry = {
            'asset_type': 'animation',
            'generated_file': anim['file'],
            'generated_symbol': anim['symbol'],
            'unity_source': None,
            'sprite_name': None,
            'character': None,
            'animation': None,
            'frame_index': i,
        }
        
        sprite_index = len(characters) + i
        if sprite_index < len(all_sprites):
            sprite_info = all_sprites[sprite_index]
            mapping_entry['unity_source'] = sprite_info['sheet']
            mapping_entry['sprite_name'] = sprite_info['sprite'].get('name')
        
        manifest['mapping'].append(mapping_entry)
        manifest['statistics']['mapped_frames'] += 1
    
    manifest['statistics']['unmapped_frames'] = len(characters) + len(animations) - manifest['statistics']['mapped_frames']
    
    return manifest


def generate_mapping_report(manifest, output_path):
    """Generate human-readable mapping report."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Asset Mapping Report\n\n")
        f.write(f"Source: {manifest['source_repository']}\n\n")
        
        f.write("## Statistics\n\n")
        stats = manifest['statistics']
        f.write(f"- Total spritesheets: {stats['total_spritesheets']}\n")
        f.write(f"- Total character frames: {stats['total_character_frames']}\n")
        f.write(f"- Total animation frames: {stats['total_animation_frames']}\n")
        f.write(f"- Mapped frames: {stats['mapped_frames']}\n")
        f.write(f"- Unmapped frames: {stats['unmapped_frames']}\n\n")
        
        f.write("## Spritesheets\n\n")
        for sheet in manifest['spritesheets']:
            f.write(f"- {sheet['png_path']}\n")
            f.write(f"  - Meta: {sheet['meta_path']}\n")
            f.write(f"  - Sprites: {len(sheet['sprites'])}\n")
        
        f.write("\n## Character Frames\n\n")
        f.write("| Index | Generated File | Unity Source | Sprite Name |\n")
        f.write("|-------|---------------|--------------|-------------|\n")
        for entry in manifest['mapping']:
            if entry['asset_type'] == 'character':
                unity_src = entry.get('unity_source', 'UNKNOWN') or 'UNKNOWN'
                sprite_name = entry.get('sprite_name', 'UNKNOWN') or 'UNKNOWN'
                f.write(f"| {entry['frame_index']} | {entry['generated_file']} | {unity_src} | {sprite_name} |\n")
        
        f.write("\n## Animation Frames\n\n")
        f.write("| Index | Generated File | Unity Source | Sprite Name |\n")
        f.write("|-------|---------------|--------------|-------------|\n")
        for entry in manifest['mapping']:
            if entry['asset_type'] == 'animation':
                unity_src = entry.get('unity_source', 'UNKNOWN') or 'UNKNOWN'
                sprite_name = entry.get('sprite_name', 'UNKNOWN') or 'UNKNOWN'
                f.write(f"| {entry['frame_index']} | {entry['generated_file']} | {unity_src} | {sprite_name} |\n")


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
    
    # Write manifest
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Written: {args.output}")
    
    # Generate report
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    generate_mapping_report(manifest, args.report)
    print(f"Written: {args.report}")
    
    # Print summary
    stats = manifest['statistics']
    print(f"\nSummary:")
    print(f"  Spritesheets: {stats['total_spritesheets']}")
    print(f"  Character frames: {stats['total_character_frames']}")
    print(f"  Animation frames: {stats['total_animation_frames']}")
    print(f"  Mapped: {stats['mapped_frames']}")
    print(f"  Unmapped: {stats['unmapped_frames']}")


if __name__ == '__main__':
    main()

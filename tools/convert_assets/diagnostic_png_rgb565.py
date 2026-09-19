#!/usr/bin/env python3
"""
TEMPORARY DIAGNOSTIC SCRIPT - To be removed after root cause analysis

Diagnoses PNG assets from Unity to determine why generated headers are 0xffff
"""
import sys
import json
import hashlib
import re
from pathlib import Path
from PIL import Image

# Add tools directory to path to reuse existing functions
TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(TOOLS_DIR))

from build_asset_manifest import parse_meta_file, rgb888_to_rgb565

UNITY_SPRITES = Path("unity_source/Assets/Sprites")
CHAR_PNG = UNITY_SPRITES / "characters.png"
ANIM_PNG = UNITY_SPRITES / "animations.png"
CHAR_META = UNITY_SPRITES / "characters.png.meta"
ANIM_META = UNITY_SPRITES / "animations.png.meta"
DEBUG_DIR = Path("debug")
ASSETS_DIR = Path("assets")

def diagnose_png(path: Path, label: str) -> dict:
    """Diagnose a PNG file and return statistics"""
    print(f"\n{'='*60}")
    print(f"PNG DIAGNOSTIC: {label}")
    print(f"{'='*60}")
    print(f"path: {path}")
    
    if not path.exists():
        print("ERROR: file not found")
        return None
    
    im = Image.open(path)
    result = {
        'size': im.size,
        'mode': im.mode,
        'bands': len(im.getbands()),
        'format': im.format
    }
    
    print(f"size: {im.size}")
    print(f"mode: {im.mode}")
    print(f"bands: {len(im.getbands())}")
    print(f"format: {im.format}")
    
    # Alpha analysis
    if "A" in im.mode:
        a = im.getchannel("A")
        a_min, a_max = a.getextrema()
        a_vals = set(a.getdata())
        pixels_alpha_zero = sum(1 for v in a.getdata() if v == 0)
        pixels_alpha_nonzero = len(a.getdata()) - pixels_alpha_zero
        pixels_alpha_255 = sum(1 for v in a.getdata() if v == 255)
        pct_transparent = 100.0 * pixels_alpha_zero / len(a.getdata())
        pct_opaque = 100.0 * pixels_alpha_nonzero / len(a.getdata())
        pct_fully_opaque = 100.0 * pixels_alpha_255 / len(a.getdata())
        
        result['alpha'] = {
            'min': a_min,
            'max': a_max,
            'unique_values': len(a_vals),
            'pixels_zero': pixels_alpha_zero,
            'pixels_nonzero': pixels_alpha_nonzero,
            'pixels_255': pixels_alpha_255,
            'pct_transparent': pct_transparent,
            'pct_opaque': pct_opaque,
            'pct_fully_opaque': pct_fully_opaque
        }
        
        print(f"alpha_min: {a_min}")
        print(f"alpha_max: {a_max}")
        print(f"alpha_unique_values: {len(a_vals)}")
        print(f"pixels_alpha_zero: {pixels_alpha_zero}")
        print(f"pixels_alpha_nonzero: {pixels_alpha_nonzero}")
        print(f"pixels_alpha_255: {pixels_alpha_255}")
        print(f"percentage_transparent: {pct_transparent:.4f}")
        print(f"percentage_opaque: {pct_opaque:.4f}")
        print(f"percentage_fully_opaque: {pct_fully_opaque:.4f}")
        
        # RGB by alpha zones
        rgba = list(im.getdata())
        rgb_alpha0 = [(r,g,b) for (r,g,b,a) in rgba if a == 0]
        rgb_alpha_gt0 = [(r,g,b) for (r,g,b,a) in rgba if a > 0]
        rgb_alpha_255 = [(r,g,b) for (r,g,b,a) in rgba if a == 255]
        
        def rgb_stats(pixels, tag):
            if not pixels:
                print(f"unique_RGB_count_{tag}: 0")
                return {'unique': 0}
            unique_rgb = len(set(pixels))
            r_vals, g_vals, b_vals = zip(*pixels)
            print(f"unique_RGB_count_{tag}: {unique_rgb}")
            print(f"R_min_{tag}: {min(r_vals)}")
            print(f"R_max_{tag}: {max(r_vals)}")
            print(f"G_min_{tag}: {min(g_vals)}")
            print(f"G_max_{tag}: {max(g_vals)}")
            print(f"B_min_{tag}: {min(b_vals)}")
            print(f"B_max_{tag}: {max(b_vals)}")
            return {'unique': unique_rgb, 'min_r': min(r_vals), 'max_r': max(r_vals)}
        
        result['rgb_alpha0'] = rgb_stats(rgb_alpha0, "alpha_eq_0")
        result['rgb_alpha_gt0'] = rgb_stats(rgb_alpha_gt0, "alpha_gt_0")
        result['rgb_alpha_255'] = rgb_stats(rgb_alpha_255, "alpha_eq_255")
    else:
        result['alpha'] = None
        print("alpha: NONE")
        
        # RGB analysis
        if im.mode != "RGB":
            rgb_im = im.convert("RGB")
        else:
            rgb_im = im
        pixels = list(rgb_im.getdata())
        unique_rgb = len(set(pixels))
        r_vals, g_vals, b_vals = zip(*pixels)
        
        result['rgb'] = {
            'unique': unique_rgb,
            'r_min': min(r_vals),
            'r_max': max(r_vals),
            'g_min': min(g_vals),
            'g_max': max(g_vals),
            'b_min': min(b_vals),
            'b_max': max(b_vals)
        }
        
        print(f"unique_RGB_count: {unique_rgb}")
        print(f"R_min: {min(r_vals)}")
        print(f"R_max: {max(r_vals)}")
        print(f"G_min: {min(g_vals)}")
        print(f"G_max: {max(g_vals)}")
        print(f"B_min: {min(b_vals)}")
        print(f"B_max: {max(b_vals)}")
    
    return result

def analyze_sprite(im: Image.Image, rect: dict, index: int, label: str, meta_name: str, header_path: Path = None) -> dict:
    """Analyze a single sprite and compare with existing header"""
    x = rect["x"]
    y = rect["y"]
    w = rect["w"]
    h = rect["h"]
    
    # REAL transformation from production converter
    y_pil = im.height - y - h
    crop_box = (x, y_pil, x + w, y_pil + h)
    
    print(f"\n{'='*60}")
    print(f"SPRITE DIAGNOSTIC: {label}_{index}")
    print(f"{'='*60}")
    print(f"sprite_name: {meta_name}")
    print(f"rect: x={x}, y={y}, w={w}, h={h}")
    print(f"image_size: {im.size}")
    print(f"y_pil: {y_pil}")
    print(f"crop_box: {crop_box}")
    
    # Check bounds
    if crop_box[0] < 0 or crop_box[1] < 0 or crop_box[2] > im.width or crop_box[3] > im.height:
        print("ERROR: CROP OUT OF BOUNDS")
        return {'error': 'out_of_bounds'}
    
    crop = im.crop(crop_box)
    
    # RGBA analysis
    if crop.mode != "RGBA":
        crop_rgba = crop.convert("RGBA")
    else:
        crop_rgba = crop
    
    rgba_pixels = list(crop_rgba.getdata())
    unique_rgba = len(set(rgba_pixels))
    r_vals, g_vals, b_vals, a_vals = zip(*rgba_pixels)
    alpha_min, alpha_max = min(a_vals), max(a_vals)
    transparent_pixels = sum(1 for a in a_vals if a == 0)
    non_transparent_pixels = sum(1 for a in a_vals if a > 0)
    white_rgb_pixels = sum(1 for (r,g,b) in zip(r_vals,g_vals,b_vals) if r==255 and g==255 and b==255)
    non_white_rgb_pixels = len(rgba_pixels) - white_rgb_pixels
    
    print(f"RGBA_unique_count: {unique_rgba}")
    print(f"alpha_min: {alpha_min}")
    print(f"alpha_max: {alpha_max}")
    print(f"transparent_pixels: {transparent_pixels}")
    print(f"non_transparent_pixels: {non_transparent_pixels}")
    print(f"white_RGB_pixels: {white_rgb_pixels}")
    print(f"non_white_RGB_pixels: {non_white_rgb_pixels}")
    
    # RGB analysis
    crop_rgb = crop_rgba.convert("RGB")
    rgb_pixels = list(crop_rgb.getdata())
    unique_rgb = len(set(rgb_pixels))
    print(f"RGB_unique_count: {unique_rgb}")
    
    # RGB565 conversion (production logic)
    rgb565_vals = [rgb888_to_rgb565(r,g,b) for (r,g,b) in rgb_pixels]
    unique_rgb565 = len(set(rgb565_vals))
    white_count = sum(1 for v in rgb565_vals if v == 0xFFFF)
    white_pct = 100.0 * white_count / len(rgb565_vals)
    non_white_pct = 100.0 - white_pct
    
    print(f"RGB565_unique_count: {unique_rgb565}")
    print(f"RGB565_min: {min(rgb565_vals)}")
    print(f"RGB565_max: {max(rgb565_vals)}")
    print(f"percentage_0xffff: {white_pct:.4f}")
    print(f"percentage_non_0xffff: {non_white_pct:.4f}")
    
    result = {
        'sprite_name': meta_name,
        'rect': rect,
        'y_pil': y_pil,
        'rgba_unique': unique_rgba,
        'alpha_min': alpha_min,
        'alpha_max': alpha_max,
        'transparent_pixels': transparent_pixels,
        'non_transparent_pixels': non_transparent_pixels,
        'non_white_pixels': non_white_rgb_pixels,
        'rgb_unique': unique_rgb,
        'rgb565_unique': unique_rgb565,
        'rgb565_min': min(rgb565_vals),
        'rgb565_max': max(rgb565_vals),
        'white_pct': white_pct
    }
    
    # Compare with existing header if provided
    if header_path and header_path.exists():
        print(f"\nComparing with header: {header_path}")
        header_content = header_path.read_text()
        header_arr = re.findall(r"0x[0-9A-Fa-f]+", header_content)
        
        if header_arr:
            header_vals = [int(v, 16) for v in header_arr]
            header_unique = len(set(header_vals))
            header_white = sum(1 for v in header_vals if v == 0xFFFF)
            header_white_pct = 100.0 * header_white / len(header_vals)
            header_sha = hashlib.sha256(
                bytes([(v>>8)&0xFF for v in header_vals] + [v&0xFF for v in header_vals])
            ).hexdigest()
            
            print(f"Header elements: {len(header_vals)}")
            print(f"Header unique RGB565: {header_unique}")
            print(f"Header percentage_0xffff: {header_white_pct:.4f}")
            print(f"Header SHA256: {header_sha}")
            
            # Compare RGB565 arrays
            if len(header_vals) == len(rgb565_vals):
                exact_match = all(h == e for h, e in zip(header_vals, rgb565_vals))
                print(f"EXACT MATCH: {exact_match}")
                result['header_match'] = 'EXACT' if exact_match else 'NO_MATCH'
            else:
                print(f"SIZE MISMATCH: header={len(header_vals)}, expected={len(rgb565_vals)}")
                result['header_match'] = 'SIZE_MISMATCH'
            
            result['header'] = {
                'elements': len(header_vals),
                'unique': header_unique,
                'white_pct': header_white_pct,
                'sha256': header_sha
            }
        else:
            print("No array found in header")
            result['header_match'] = 'NO_ARRAY'
    else:
        result['header_match'] = 'NO_HEADER'
    
    return result

def analyze_header(path: Path) -> dict:
    """Analyze an existing header file"""
    if not path.exists():
        print(f"{path.name}: NOT FOUND")
        return None
    
    content = path.read_text()
    arr = re.findall(r"0x[0-9A-Fa-f]+", content)
    
    if not arr:
        print(f"{path.name}: no array found")
        return None
    
    vals = [int(v, 16) for v in arr]
    unique = len(set(vals))
    white = sum(1 for v in vals if v == 0xFFFF)
    white_pct = 100.0 * white / len(vals)
    non_white_pct = 100.0 - white_pct
    sha = hashlib.sha256(
        bytes([(v>>8)&0xFF for v in vals] + [v&0xFF for v in vals])
    ).hexdigest()
    
    print(f"\n{path.name}:")
    print(f"  elements: {len(vals)}")
    print(f"  unique_RGB565: {unique}")
    print(f"  percentage_0xffff: {white_pct:.4f}")
    print(f"  percentage_non_0xffff: {non_white_pct:.4f}")
    print(f"  array_SHA256: {sha}")
    
    return {
        'elements': len(vals),
        'unique': unique,
        'white_pct': white_pct,
        'sha256': sha
    }

def make_debug_grid(im: Image.Image, meta_list: list, label: str, out_name: str, on_black: bool = False):
    """Generate debug visualization of first 25 sprites"""
    if not im or not meta_list:
        return
    
    rects = meta_list[:25]
    tile_w = max(r["w"] for r in rects)
    tile_h = max(r["h"] for r in rects)
    
    grid = Image.new("RGBA" if not on_black else "RGB", (5*tile_w, 5*tile_h), (0,0,0,0) if not on_black else (0,0,0))
    
    from PIL import ImageDraw
    draw = ImageDraw.Draw(grid)
    
    for idx, r in enumerate(rects):
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]
        y_pil = im.height - y - h
        crop_box = (x, y_pil, x+w, y_pil+h)
        sprite = im.crop(crop_box)
        
        if on_black:
            sprite = sprite.convert("RGBA")
            bg = Image.new("RGB", sprite.size, (0,0,0))
            bg.paste(sprite, mask=sprite.getchannel("A"))
            sprite = bg
        else:
            sprite = sprite.convert("RGBA")
        
        sprite = sprite.resize((tile_w, tile_h))
        gx = (idx % 5) * tile_w
        gy = (idx // 5) * tile_h
        grid.paste(sprite, (gx, gy))
        
        # Label
        text = f"{idx}\n{r['name'][:10]}"
        draw.text((gx+2, gy+2), text, fill=(255,255,255))
    
    grid.save(out_name)
    print(f"Saved {out_name}")

def main():
    print("\n" + "="*60)
    print("TEMPORARY PNG RGB565 DIAGNOSTIC")
    print("="*60)
    
    # Create debug directory
    DEBUG_DIR.mkdir(exist_ok=True)
    
    # Load metadata from .meta files
    print("\nLoading Unity metadata...")
    char_meta = parse_meta_file(CHAR_META) if CHAR_META.exists() else None
    anim_meta = parse_meta_file(ANIM_META) if ANIM_META.exists() else None
    
    if not char_meta or not anim_meta:
        print("ERROR: Could not load .meta files")
        sys.exit(1)
    
    print(f"Loaded {len(char_meta)} character sprites")
    print(f"Loaded {len(anim_meta)} animation sprites")
    
    # Load PNGs
    char_im = diagnose_png(CHAR_PNG, "characters.png")
    anim_im = diagnose_png(ANIM_PNG, "animations.png")
    
    # Representative sprites
    indices_chars = [0, 1, 10, 100, 224]
    indices_anims = [0, 1, 10, 100, 224]
    
    results = {
        'characters': [],
        'animations': []
    }
    
    # Analyze representative character sprites
    if char_im and char_meta:
        print("\n" + "="*60)
        print("CHARACTER SPRITES")
        print("="*60)
        for i in indices_chars:
            if i < len(char_meta):
                rect = char_meta[i]["rect"]
                name = char_meta[i]["name"]
                header_path = ASSETS_DIR / "characters" / f"characters_{i}.h"
                result = analyze_sprite(char_im, rect, i, "characters", name, header_path)
                results['characters'].append(result)
    
    # Analyze representative animation sprites
    if anim_im and anim_meta:
        print("\n" + "="*60)
        print("ANIMATION SPRITES")
        print("="*60)
        for i in indices_anims:
            if i < len(anim_meta):
                rect = anim_meta[i]["rect"]
                name = anim_meta[i]["name"]
                header_path = ASSETS_DIR / "animations" / f"animations_{i}.h"
                result = analyze_sprite(anim_im, rect, i, "animations", name, header_path)
                results['animations'].append(result)
    
    # Analyze existing headers
    print("\n" + "="*60)
    print("EXISTING HEADERS")
    print("="*60)
    
    header_results = {'characters': [], 'animations': []}
    
    for i in [0, 1, 224]:
        p = ASSETS_DIR / "characters" / f"characters_{i}.h"
        result = analyze_header(p)
        if result:
            header_results['characters'].append(result)
    
    for i in [0, 1, 224]:
        p = ASSETS_DIR / "animations" / f"animations_{i}.h"
        result = analyze_header(p)
        if result:
            header_results['animations'].append(result)
    
    # Generate debug visualizations
    print("\n" + "="*60)
    print("DEBUG VISUALIZATION")
    print("="*60)
    
    if char_im and char_meta:
        make_debug_grid(char_im, char_meta, "characters", str(DEBUG_DIR/"characters_first25_raw.png"), on_black=False)
        make_debug_grid(char_im, char_meta, "characters", str(DEBUG_DIR/"characters_first25_on_black.png"), on_black=True)
    
    if anim_im and anim_meta:
        make_debug_grid(anim_im, anim_meta, "animations", str(DEBUG_DIR/"animations_first25_raw.png"), on_black=False)
        make_debug_grid(anim_im, anim_meta, "animations", str(DEBUG_DIR/"animations_first25_on_black.png"), on_black=True)
    
    # Save results
    results_file = DEBUG_DIR / "diagnostic_results.json"
    with open(results_file, 'w') as f:
        json_output = {
            'characters_png': char_im,
            'animations_png': anim_im,
            'sprites': results,
            'headers': header_results
        }
        json.dump(json_output, f, indent=2, default=str)
    
    print(f"\nSaved results to {results_file}")
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()

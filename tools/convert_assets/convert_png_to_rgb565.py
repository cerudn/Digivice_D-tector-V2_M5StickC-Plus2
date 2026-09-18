#!/usr/bin/env python3
"""
PNG to RGB565 converter for D-Tector V2 ESP32 firmware.

Usage:
    python convert_png_to_rgb565.py input.png output.h SPRITE_NAME [--sheet WxH --grid CxR --scale N]

Options:
    --sheet WxH     : Sprite sheet dimensions in pixels (e.g., 256x256)
    --grid CxR      : Grid layout: columns x rows (e.g., 4x4 for 16 frames)
    --scale N       : Scale factor for output (default: 1, use 4 for 128x128 sprites)
    --transparent   : Enable transparency (black = transparent)

Output:
    Generates a C++ header with PROGMEM arrays:
    - SPRITE_NAME_frames[] : RGB565 pixel data
    - SPRITE_NAME_width, SPRITE_NAME_height : dimensions
    - SPRITE_NAME_frameCount : number of frames

Example (Takuya idle 32x32 scaled to 128x128):
    python convert_png_to_rgb565.py characters.png takuya_idle.h TAKUYA_IDLE \
        --sheet 256x256 --grid 8x8 --scale 4 --transparent
"""

import sys
import os
from PIL import Image
import argparse

def rgb_to_rgb565(r, g, b):
    """Convert RGB888 to RGB565."""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def convert_png_to_rgb565(input_path, output_header, sprite_name, sheet_dims=None, grid=None, scale=1, transparent=False):
    """Convert PNG sprite sheet to C++ header with RGB565 arrays."""
    
    img = Image.open(input_path).convert('RGBA')
    
    # Determine frame dimensions
    if sheet_dims and grid:
        sheet_w, sheet_h = sheet_dims
        cols, rows = grid
        frame_w = sheet_w // cols
        frame_h = sheet_h // rows
        total_frames = cols * rows
    else:
        # Single sprite
        frame_w, frame_h = img.size
        total_frames = 1
        cols, rows = 1, 1
    
    # Apply scaling
    out_w = frame_w * scale
    out_h = frame_h * scale
    
    # Extract frames
    frames = []
    for frame_idx in range(total_frames):
        col = frame_idx % cols
        row = frame_idx // cols
        
        left = col * frame_w
        upper = row * frame_h
        right = left + frame_w
        lower = upper + frame_h
        
        frame = img.crop((left, upper, right, lower))
        
        # Scale if needed
        if scale > 1:
            frame = frame.resize((out_w, out_h), Image.NEAREST)
        
        # Convert to RGB565
        pixels = []
        for y in range(out_h):
            for x in range(out_w):
                r, g, b, a = frame.getpixel((x, y))
                if transparent and a < 128:
                    # Transparent pixel: use black with special marker or skip
                    pixels.append(0x0000)  # Black, will be handled as transparent in blit
                else:
                    pixels.append(rgb_to_rgb565(r, g, b))
        
        frames.append(pixels)
    
    # Generate C++ header
    os.makedirs(os.path.dirname(output_header), exist_ok=True) if os.path.dirname(output_header) else None
    
    with open(output_header, 'w') as f:
        f.write(f"#pragma once\n")
        f.write(f"#include <cstdint>\n")
        f.write(f"#include <M5Unified.h>\n\n")
        f.write(f"namespace dtec::assets {{\n\n")
        
        f.write(f"// {sprite_name}\n")
        f.write(f"// Source: {os.path.basename(input_path)}\n")
        f.write(f"// Frame size: {out_w}x{out_h} (scaled from {frame_w}x{frame_h})\n")
        f.write(f"// Total frames: {total_frames}\n")
        f.write(f"// Format: RGB565, {'with transparency' if transparent else 'opaque'}\n\n")
        
        f.write(f"constexpr uint16_t {sprite_name}_width = {out_w};\n")
        f.write(f"constexpr uint16_t {sprite_name}_height = {out_h};\n")
        f.write(f"constexpr uint8_t {sprite_name}_frameCount = {total_frames};\n\n")
        
        for i, frame_pixels in enumerate(frames):
            f.write(f"// Frame {i}\n")
            f.write(f"constexpr uint16_t {sprite_name}_frame{i}[] PROGMEM = {{\n    ")
            for j, pixel in enumerate(frame_pixels):
                if j > 0 and j % 16 == 0:
                    f.write("\n    ")
                f.write(f"0x{pixel:04X}, ")
            f.write("\n};\n\n")
        
        f.write(f"// Frame pointer array\n")
        f.write(f"constexpr const uint16_t* {sprite_name}_frames[] PROGMEM = {{\n    ")
        for i in range(total_frames):
            f.write(f"{sprite_name}_frame{i}, ")
        f.write("\n};\n\n")
        
        f.write(f"}} // namespace dtec::assets\n")
    
    print(f"Converted {input_path} -> {output_header}")
    print(f"  Sprite: {sprite_name}")
    print(f"  Frame size: {out_w}x{out_h} ({total_frames} frames)")
    print(f"  Scale: {scale}x")
    print(f"  Transparency: {'enabled' if transparent else 'disabled'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PNG sprite sheet to RGB565 C++ header")
    parser.add_argument("input", help="Input PNG file")
    parser.add_argument("output", help="Output C++ header file")
    parser.add_argument("name", help="Sprite name (C++ identifier)")
    parser.add_argument("--sheet", help="Sprite sheet dimensions (WxH), e.g., 256x256")
    parser.add_argument("--grid", help="Grid layout (ColsxRows), e.g., 8x8")
    parser.add_argument("--scale", type=int, default=1, help="Scale factor (default: 1)")
    parser.add_argument("--transparent", action="store_true", help="Enable transparency (black=transparent)")
    
    args = parser.parse_args()
    
    sheet_dims = None
    if args.sheet:
        w, h = map(int, args.sheet.split('x'))
        sheet_dims = (w, h)
    
    grid = None
    if args.grid:
        c, r = map(int, args.grid.split('x'))
        grid = (c, r)
    
    convert_png_to_rgb565(args.input, args.output, args.name, sheet_dims, grid, args.scale, args.transparent)

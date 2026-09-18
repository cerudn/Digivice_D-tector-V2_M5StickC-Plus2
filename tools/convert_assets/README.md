# Asset Conversion Pipeline

This directory contains tools for converting Unity assets (PNG sprites) into ESP32-optimized formats (RGB565, PROGMEM arrays).

## convert_png_to_rgb565.py

Converts PNG sprite sheets into C++ headers with RGB565 pixel arrays suitable for direct blitting to M5StickC Plus2 display.

### Usage

```bash
python convert_png_to_rgb565.py input.png output.h SPRITE_NAME [options]
```

### Options

- `--sheet WxH` : Sprite sheet dimensions in pixels (e.g., `256x256`)
- `--grid CxR` : Grid layout: columns x rows (e.g., `8x8` for 16 frames)
- `--scale N` : Scale factor for output (default: `1`, use `4` for 128x128 sprites)
- `--transparent` : Enable transparency (black pixels treated as transparent)

### Examples

#### Convert Takuya idle sprite (assuming 32x32 frame in 256x256 sheet, 8x8 grid)

```bash
python convert_png_to_rgb565.py ../../Assets/Sprites/characters.png takuya_idle.h TAKUYA_IDLE \\
    --sheet 256x256 --grid 8x8 --scale 4 --transparent
```

#### Convert single PNG (no sheet)

```bash
python convert_png_to_rgb565.py idle_frame.png idle_frame.h IDLE_FRAME --scale 4 --transparent
```

### Output Format

Generates a C++ header with:

- `SPRITE_NAME_width`, `SPRITE_NAME_height` : frame dimensions
- `SPRITE_NAME_frameCount` : number of frames
- `SPRITE_NAME_frame0[]`, `SPRITE_NAME_frame1[]`, ... : RGB565 pixel arrays (PROGMEM)
- `SPRITE_NAME_frames[]` : array of frame pointers

### Integration

Include the generated header in your firmware:

```cpp
#include "assets/takuya_idle.h"

// In GameRenderer:
const uint16_t* frame = dtec::assets::TAKUYA_IDLE_frames[anim.currentFrameIndex()];
display_.blit(x, y, dtec::assets::TAKUYA_IDLE_width, dtec::assets::TAKUYA_IDLE_height, frame, true);
```

## Dependencies

- Python 3.8+
- Pillow (`pip install Pillow`)

## Notes

- RGB565 format: 5 bits red, 6 bits green, 5 bits blue (16-bit color)
- `--transparent` marks black pixels (0x0000) as transparent in blit operations
- Use `--scale 4` to match the 128x128 logical screen (32x32 base sprites scaled 4x)
- For sprite sheets, ensure `--sheet` and `--grid` match the actual layout in Unity

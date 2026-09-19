# Asset Mapping Report

**Status:** IN PROGRESS - Phase 1 of Milestone 2

**Source Repository:** cerudn/Digivice_D-tector-V2_Unity-

**Generated Assets:** firmware/assets/characters/*.h, firmware/assets/animations/*.h

## Overview

This document tracks the mapping between Unity source assets and generated firmware RGB565 headers.

## Statistics (Preliminary)

| Category | Count |
|----------|-------|
| Total generated frames | 450 |
| Character frames | 225 |
| Animation frames | 225 |
| Mapped to Unity sprites | TBD |
| Unmapped | TBD |

## Strategy

### Identity Strategy

The primary identity for each frame is established by:

1. **Sprite rect coordinates** (x, y, width, height) from Unity .meta files
2. **Sprite name** when available in .meta
3. **Order of extraction** from the spritesheet

The generated headers are identified by:
- `characters_N.h` for character sprites
- `animations_N.h` for animation frames

Where N is the sequential index during extraction.

### Mapping Approach

1. Parse Unity .meta files to extract sprite rects and names
2. Match extraction order to generated header order
3. Record the correspondence in `assets/asset_manifest.json`
4. Generate this human-readable report

## Unity Spritesheets

### characters.png

- **Source:** Unity repository
- **Meta:** characters.png.meta
- **Sprite mode:** Multiple (sprite sheet)
- **Expected sprites:** 225

### animations.png

- **Source:** Unity repository
- **Meta:** animations.png.meta
- **Sprite mode:** Multiple (sprite sheet)
- **Expected sprites:** 225

## Character Frames

| Index | Generated File | Unity Source | Sprite Name | Character | Notes |
|-------|---------------|--------------|-------------|-----------|-------|
| 0 | characters_0.h | TBD | TBD | TBD | First extracted sprite |
| 1 | characters_1.h | TBD | TBD | TBD | |
| ... | ... | TBD | TBD | TBD | |
| 224 | characters_224.h | TBD | TBD | TBD | Last character sprite |

**Note:** Actual Unity correspondence will be populated by `build_asset_manifest.py`.

## Animation Frames

| Index | Generated File | Unity Source | Sprite Name | Animation | Frame | Notes |
|-------|---------------|--------------|-------------|-----------|-------|-------|
| 0 | animations_0.h | TBD | TBD | TBD | 0 | First animation frame |
| 1 | animations_1.h | TBD | TBD | TBD | 0 | |
| ... | ... | TBD | TBD | TBD | ... | |
| 224 | animations_224.h | TBD | TBD | TBD | 0 | Last animation frame |

## Unresolved Mappings

The following mappings require additional Unity data:

- **Character identity:** Which Unity character does each sprite represent?
- **Animation sequences:** Which frames belong to which animation?
- **Frame order:** What is the correct playback order for each animation?

## Next Steps

1. Run `build_asset_manifest.py` against Unity repository
2. Populate Unity source references
3. Identify character names from Unity data
4. Map animation sequences
5. Validate frame order

## Tool Usage

```bash
cd tools/convert_assets
python build_asset_manifest.py \
  --unity-root /path/to/Unity/repo \
  --assets-dir ../../assets \
  --output ../../assets/asset_manifest.json \
  --report ../../Docs/ASSET_MAPPING.md
```

## Known Limitations

- Mapping currently based on extraction order, not semantic Unity data
- Character names not yet determined
- Animation sequences not yet mapped
- Requires access to Unity repository for full mapping

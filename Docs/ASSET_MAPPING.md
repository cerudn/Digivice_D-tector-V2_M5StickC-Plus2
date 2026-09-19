# Asset Mapping Report

**Status:** IN PROGRESS - Phase 1 of Milestone 2

**Source Repository:** cerudn/Digivice_D-tector-V2_Unity-

**Generated Assets:** assets/characters/*.h, assets/animations/*.h

## Overview

This document tracks the mapping between Unity source assets and generated firmware RGB565 headers.

## Identity Levels

We distinguish three levels of identity:

1. **RAW_DISCOVERED**: Sprite exists in Unity metadata
2. **ASSET_MATCHED**: Generated header corresponds to this Unity sprite (by rect + order)
3. **SEMANTICALLY_MAPPED**: We know what character/animation this represents

## Statistics

| Category | Count |
|----------|-------|
| Total generated assets | 450 |
| RAW_DISCOVERED | TBD |
| ASSET_MATCHED | TBD |
| SEMANTICALLY_MAPPED | 0 |
| UNMATCHED | TBD |
| AMBIGUOUS | TBD |
| MISSING_METADATA | TBD |

**Note:** SEMANTICALLY_MAPPED = 0 is expected at this phase. We prioritize honest reporting over false positives.

## Strategy

### Asset Identity (Level A)

The primary identity for each frame is established by:

1. **Sprite rect coordinates** (x, y, width, height) from Unity .meta files
2. **Sprite name** when available in .meta
3. **Source PNG path**
4. **Source .meta path**

The generated headers are identified by:
- `characters_N.h` for character sprites
- `animations_N.h` for animation frames

Where N is the sequential index during extraction.

### Semantic Identity (Levels B + C)

**B. Character identity:** Which Unity character does each sprite represent?

**C. Animation identity:** Which frames belong to which animation, in what order?

These require analysis of:
- Unity AnimationClip files
- Animator Controller files
- Game code that references sprites
- ScriptableObject / MonoBehaviour data

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

## Asset Matching

Matching currently based on extraction order (placeholder).

**Real matching requires:**
- Rect comparison
- GUID/fileID when available
- Verification against actual Unity data

## Character Frames

| Index | Generated File | Asset Match | Sprite Name | Rect | Character | Animation | Notes |
|-------|---------------|-------------|-------------|------|-----------|-----------|-------|
| 0 | characters_0.h | TBD | TBD | TBD | null | null | First extracted sprite |
| 1 | characters_1.h | TBD | TBD | TBD | null | null | |
| ... | ... | TBD | TBD | TBD | null | null | |
| 224 | characters_224.h | TBD | TBD | TBD | null | null | Last character sprite |

**Note:** Character and Animation columns are null until semantic mapping is complete.

## Animation Frames

| Index | Generated File | Asset Match | Sprite Name | Rect | Character | Animation | Frame | Notes |
|-------|---------------|-------------|-------------|------|-----------|-----------|-------|-------|
| 0 | animations_0.h | TBD | TBD | TBD | null | null | 0 | First animation frame |
| 1 | animations_1.h | TBD | TBD | TBD | null | null | 0 | |
| ... | ... | TBD | TBD | TBD | null | null | ... | |
| 224 | animations_224.h | TBD | TBD | TBD | null | null | 0 | Last animation frame |

## Unresolved Mappings

The following mappings require additional Unity data:

- **Character identity:** Which Unity character does each sprite represent?
- **Animation sequences:** Which frames belong to which animation?
- **Frame order:** What is the correct playback order for each animation?

## Next Steps

1. Run `build_asset_manifest.py` against Unity repository
2. Populate Unity source references with actual rect data
3. Identify character names from Unity data
4. Map animation sequences from AnimationClip files
5. Validate frame order
6. Analyze game code for sprite references

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

- Matching currently based on extraction order, not semantic Unity data
- Character names not yet determined
- Animation sequences not yet mapped
- Requires access to Unity repository for full mapping
- SEMANTICALLY_MAPPED = 0 at this phase (by design)

## Manifest Structure

The `assets/asset_manifest.json` contains:

```json
{
  "generated_symbol": "characters_37",
  "generated_file": "characters/characters_37.h",
  "generated_index": 37,
  
  "source": {
    "png": "Assets/Sprites/characters.png",
    "meta": "Assets/Sprites/characters.png.meta",
    "sprite_name": "...",
    "rect": {
      "x": 123,
      "y": 64,
      "width": 32,
      "height": 32
    },
    "pivot": {
      "x": 0.5,
      "y": 0.5
    }
  },
  
  "identity": {
    "asset_match": "ASSET_MATCHED",
    "character": null,
    "animation": null,
    "semantic_status": "RAW_DISCOVERED"
  }
}
```

**Note:** `character` and `animation` are null until semantic mapping is complete.

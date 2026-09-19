# Asset Mapping Report

**Status:** INFRASTRUCTURE READY - AWAITING GITHUB ACTIONS EXECUTION

**Source Repository:** cerudn/Digivice_D-tector-V2_Unity-
**Unity Revision:** TBD (will be set by workflow)

**Generated Assets:** assets/characters/*.h, assets/animations/*.h

## Overview

This document tracks the mapping between Unity source assets and generated firmware RGB565 headers.

## Asset Identity Strategy

Asset identity is determined by **RGB565 content matching**, NOT by index:

1. **Extract sprite from Unity PNG** using rect from .meta file
2. **Convert to RGB565** using: `((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)`
3. **Compare against generated header content** (parsed uint16_t array)
4. **ASSET_MATCHED**: exactly one header matches the RGB565 data
5. **AMBIGUOUS**: multiple headers match (visual duplicates)
6. **UNMATCHED**: no header matches

This eliminates assumptions based on extraction order or index correspondence.

## Identity Levels

We distinguish three levels of identity:

1. **RAW_DISCOVERED**: Sprite exists in Unity metadata
2. **ASSET_MATCHED**: Generated header RGB565 content matches Unity sprite
3. **SEMANTICALLY_MAPPED**: We know what character/animation this represents

## Statistics

| Category | Count | Status |
|----------|-------|--------|
| Total generated assets | 450 | VERIFIED |
| RAW_DISCOVERED | TBD | AWAITING EXECUTION |
| ASSET_MATCHED | TBD | AWAITING EXECUTION |
| SEMANTICALLY_MAPPED | 0 | BY DESIGN |
| UNMATCHED | TBD | AWAITING EXECUTION |
| AMBIGUOUS | TBD | AWAITING EXECUTION |
| MISSING_METADATA | TBD | AWAITING EXECUTION |

**Note:** SEMANTICALLY_MAPPED = 0 is expected at this phase.

## Visual Duplicates

Two Unity sprites may be visually identical but remain distinct sprites. The mapping handles this as:

- **1 Unity sprite → 1 header with matching RGB565** → ASSET_MATCHED
- **1 Unity sprite → 2+ headers with identical RGB565** → AMBIGUOUS
- **1 Unity sprite → 0 headers** → UNMATCHED

AMBIGUOUS entries include all matching header symbols for manual resolution.

## Execution

The mapping is executed by GitHub Actions workflow:

```yaml
GitHub Actions
    ↓
checkout Unity real (cerudn/Digivice_D-tector-V2_Unity-)
    ↓
checkout firmware
    ↓
build_asset_manifest.py
    ↓
RGB565 content matching
    ↓
validate
    ↓
tests
    ↓
real samples
    ↓
commit manifest/report
```

## Unity Spritesheets

### characters.png

- **Expected path:** Assets/Sprites/characters.png
- **Meta:** Assets/Sprites/characters.png.meta
- **Sprite mode:** Multiple (sprite sheet)
- **Expected sprites:** 225

### animations.png

- **Expected path:** Assets/Sprites/animations.png
- **Meta:** Assets/Sprites/animations.png.meta
- **Sprite mode:** Multiple (sprite sheet)
- **Expected sprites:** 225

## Manifest Structure

The `assets/asset_manifest.json` contains:

```json
{
  "generated_symbol": "characters_37",
  "generated_file": "characters/characters_37.h",
  
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

## Next Steps

1. Execute GitHub Actions workflow
2. Verify ASSET_MATCHED count based on RGB565 content matching
3. Review AMBIGUOUS entries for visual duplicates
4. Begin semantic mapping analysis (AnimationClip, Animator, game code)

## Known Limitations

- Semantic mapping (character/animation identity) not yet implemented
- Visual duplicates result in AMBIGUOUS status requiring manual resolution
- Requires Unity repository access for sprite extraction

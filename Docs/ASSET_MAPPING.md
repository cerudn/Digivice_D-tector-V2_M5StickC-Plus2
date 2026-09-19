# Asset Mapping Report

**Status:** INFRASTRUCTURE READY - AWAITING UNITY REPOSITORY EXECUTION

**Source Repository:** cerudn/Digivice_D-tector-V2_Unity-
**Unity Revision:** 17ceaf584227947bbc23b4a43f8cc1278f96adbb

**Generated Assets:** assets/characters/*.h, assets/animations/*.h

## Overview

This document tracks the mapping between Unity source assets and generated firmware RGB565 headers.

## Identity Levels

We distinguish three levels of identity:

1. **RAW_DISCOVERED**: Sprite exists in Unity metadata
2. **ASSET_MATCHED**: Generated header corresponds to this Unity sprite (by rect + order)
3. **SEMANTICALLY_MAPPED**: We know what character/animation this represents

## Statistics

| Category | Count | Status |
|----------|-------|--------|
| Total generated assets | 450 | VERIFIED |
| RAW_DISCOVERED | 0 | NOT YET POPULATED |
| ASSET_MATCHED | 0 | NOT YET POPULATED |
| SEMANTICALLY_MAPPED | 0 | BY DESIGN |
| UNMATCHED | 450 | PLACEHOLDER |
| AMBIGUOUS | 0 | - |
| MISSING_METADATA | 0 | - |

**Note:** Statistics are placeholders. Actual values require executing `build_asset_manifest.py` against the Unity repository.

## Execution Status

The mapping tool `tools/convert_assets/build_asset_manifest.py` is ready but requires:

1. Local checkout of Unity repository
2. Execution with correct paths

**Command to execute:**

```bash
cd tools/convert_assets
python build_asset_manifest.py \
  --unity-root /path/to/Digivice_D-tector-V2_Unity- \
  --assets-dir ../../assets \
  --output ../../assets/asset_manifest.json \
  --report ../../Docs/ASSET_MAPPING.md
```

## Unity Repository

- **Repository:** cerudn/Digivice_D-tector-V2_Unity-
- **Revision:** 17ceaf584227947bbc23b4a43f8cc1278f96adbb
- **Access:** AVAILABLE via GitHub MCP

## Expected Spritesheets

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

## Asset Matching Strategy

Matching will be based on:

1. Sprite rect coordinates from Unity .meta files
2. Sprite name when available
3. Source PNG path
4. Order of extraction (as fallback)

## Semantic Mapping

**Character identity** and **Animation identity** require analysis of:

- Unity AnimationClip files
- Animator Controller files
- Game code that references sprites
- ScriptableObject / MonoBehaviour data

**Current status:** NOT YET ANALYZED

## Manifest Structure

The `assets/asset_manifest.json` will contain:

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

## Next Steps

1. Execute `build_asset_manifest.py` against Unity repository
2. Populate `assets/asset_manifest.json` with real data
3. Update this report with actual statistics
4. Begin semantic mapping analysis (AnimationClip, Animator, game code)

## Known Limitations

- Current manifest contains placeholder values
- Requires local Unity repository checkout for full execution
- Semantic mapping (character/animation identity) not yet implemented

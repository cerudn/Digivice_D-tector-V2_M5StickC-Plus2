# Asset Mapping Report

## Manifest model

`assets/asset_manifest.json` is **generated-asset-centric**: `mapping` contains exactly one entry for every RGB565 header in `assets/characters/` and `assets/animations/`.

A generated asset has one of these identity states:

- `ASSET_MATCHED`: exactly one Unity sprite produces identical RGB565 content.
- `AMBIGUOUS`: multiple Unity sprites produce content identical to the same generated header; `sources` lists every candidate.
- `UNMATCHED`: no Unity sprite in the matching sheet category produces the header content; `source` is `null`.

The matching process is content-based: Unity `.meta` rect -> Unity PNG extraction with the Unity-Y-to-PIL-Y transform -> RGB565 conversion -> exact comparison with the parsed header array. Header indices are never used as evidence.

## Invariants

- `len(mapping) == statistics.total_generated`.
- Every `generated_assets.characters` symbol appears exactly once in `mapping`.
- Every `generated_assets.animations` symbol appears exactly once in `mapping`.
- `asset_matched + ambiguous + unmatched == total_generated`.
- `characters.png` only compares with `characters_*.h`; `animations.png` only compares with `animations_*.h`.

## Semantic status

This phase does not assign Digimon characters, animation names, or frame order. Every mapping retains `character: null` and `animation: null` unless future Unity evidence establishes those semantics.

## Workflow output

The GitHub Actions mapping job regenerates this report from the real Unity checkout and records the Unity commit SHA in the manifest. The report will then include real statistics and generated-asset sample mappings.

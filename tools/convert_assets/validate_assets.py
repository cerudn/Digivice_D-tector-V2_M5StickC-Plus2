#!/usr/bin/env python3
"""Validate converted RGB565 assets against manifest."""

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Validate converted assets')
    parser.add_argument('--assets-dir', required=True, help='Directory containing converted assets')
    parser.add_argument('--manifest', required=True, help='Path to asset_manifest.json')
    
    args = parser.parse_args()
    
    assets_dir = Path(args.assets_dir).resolve()
    manifest_path = Path(args.manifest).resolve()
    
    if not assets_dir.exists():
        print(f'ERROR: Assets directory not found: {assets_dir}', file=sys.stderr)
        sys.exit(1)
    
    if not manifest_path.exists():
        print(f'ERROR: Manifest not found: {manifest_path}', file=sys.stderr)
        sys.exit(1)
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    total_entries = manifest.get('total_entries', 0)
    by_category = manifest.get('by_category', {})
    entries = manifest.get('entries', [])
    
    print(f'Validating {total_entries} assets...')
    
    # Check expected counts
    expected_characters = 225
    expected_animations = 225
    expected_total = 450
    
    actual_characters = by_category.get('characters', 0)
    actual_animations = by_category.get('animations', 0)
    actual_total = total_entries
    
    errors = []
    
    # Validate counts
    if actual_characters != expected_characters:
        errors.append(f'characters: expected {expected_characters}, got {actual_characters}')
    
    if actual_animations != expected_animations:
        errors.append(f'animations: expected {expected_animations}, got {actual_animations}')
    
    if actual_total != expected_total:
        errors.append(f'total: expected {expected_total}, got {actual_total}')
    
    # Validate each entry
    missing_files = []
    for entry in entries:
        output_file = entry.get('output_file', '')
        file_path = assets_dir / output_file
        
        if not file_path.exists():
            missing_files.append(output_file)
        else:
            # Check file size (32x32 RGB565 = 2048 bytes + header overhead)
            file_size = file_path.stat().st_size
            if file_size < 2048:
                errors.append(f'{output_file}: file too small ({file_size} bytes, expected ~2048+)')
    
    if missing_files:
        errors.append(f'Missing {len(missing_files)} files')
        for f in missing_files[:10]:  # Show first 10
            errors.append(f'  - {f}')
    
    # Report results
    print(f'\n=== VALIDATION RESULTS ===')
    print(f'characters: {actual_characters} / {expected_characters}')
    print(f'animations: {actual_animations} / {expected_animations}')
    print(f'total: {actual_total} / {expected_total}')
    
    if errors:
        print(f'\nERRORS ({len(errors)}):')
        for error in errors:
            print(f'  {error}')
        print('\nValidation FAILED', file=sys.stderr)
        sys.exit(1)
    else:
        print('\nValidation passed')
        return 0


if __name__ == '__main__':
    sys.exit(main())

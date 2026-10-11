#!/usr/bin/env python3
"""
Arabians Lost (PSP) — Master English Build System.
Assembles reviewed English translations, repacks scenario files,
rebuilds data.cpk, and compiles the final English ISO.
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, List

sys.path.insert(0, os.path.abspath('.'))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from tools.repack import repack_file
from tools.patch_cpk import patch_cpk
from tools.iso import patch_iso

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def build_english_iso(translations_jsonl: str, output_iso: str = 'build/ArabiansLost_English.iso'):
    start_time = time.time()
    os.makedirs('build', exist_ok=True)
    os.makedirs('build/repacked_ks', exist_ok=True)
    
    print("=" * 60)
    print("ARABIANS LOST — ENGLISH ISO BUILD PIPELINE")
    print("=" * 60)
    
    # 1. Load translations
    print(f"Loading translations from {translations_jsonl}...")
    trans_by_file: Dict[str, Dict[str, str]] = {}
    total_loaded = 0
    
    with open(translations_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            d = json.loads(line)
            en = d.get('english')
            if en:
                src = d['source_file']
                if src not in trans_by_file:
                    trans_by_file[src] = {}
                trans_by_file[src][d['id']] = en
                total_loaded += 1
                
    print(f"Loaded {total_loaded} translated records across {len(trans_by_file)} scenario files.")
    
    # 2. Repack scenario files
    cpk_patches = {}
    for src_file, trans_dict in trans_by_file.items():
        orig_path = os.path.join('extracted/data_cpk/scenario', src_file)
        if not os.path.exists(orig_path):
            print(f"Warning: Original file {orig_path} not found! Skipping.")
            continue
            
        repacked_content = repack_file(orig_path, trans_dict, src_file)
        out_path = os.path.join('build/repacked_ks', src_file)
        with open(out_path, 'w', encoding='cp932', newline='') as f:
            f.write(repacked_content)
            
        cpk_patches[f"scenario/{src_file}"] = out_path
        
    print(f"Repacked {len(cpk_patches)} scenario files into build/repacked_ks/")
    
    # 2b. Add localized graphics
    graphics_dir = 'translations/graphics'
    if os.path.exists(graphics_dir):
        for root, _, files in os.walk(graphics_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, graphics_dir).replace('\\', '/')
                cpk_patches[rel_path] = full_path
                print(f"Including graphic patch: {rel_path} -> {full_path}")
    
    # 3. Patch data.cpk
    build_cpk = 'build/data.cpk'
    orig_cpk = 'extracted/filesystem/PSP_GAME/USRDIR/data.cpk'
    print(f"Patching {len(cpk_patches)} total files into {build_cpk}...")
    patch_cpk(orig_cpk, cpk_patches, build_cpk)
    
    # 4. Patch ISO
    orig_iso = 'input/original.iso'
    print(f"Building final English ISO: {output_iso}...")
    patch_iso(orig_iso, {'PSP_GAME/USRDIR/data.cpk': build_cpk}, output_iso)
    
    # 5. Build Verification
    iso_size = os.path.getsize(output_iso)
    print("Computing output ISO SHA-256 hash...")
    iso_sha256 = compute_sha256(output_iso)
    
    elapsed = time.time() - start_time
    print("=" * 60)
    print("BUILD COMPLETE!")
    print(f"Output File:     {output_iso}")
    print(f"File Size:       {iso_size:,} bytes")
    print(f"SHA-256:         {iso_sha256}")
    print(f"Patched Files:   {len(cpk_patches)}")
    print(f"Translated Text: {total_loaded} records")
    print(f"Elapsed Time:    {elapsed:.2f} seconds")
    print("=" * 60)
    
    return {
        'output_iso': output_iso,
        'size': iso_size,
        'sha256': iso_sha256,
        'files_patched': len(cpk_patches),
        'records_translated': total_loaded
    }

if __name__ == '__main__':
    trans_file = sys.argv[1] if len(sys.argv) > 1 else 'translations/reviewed/master_translated.jsonl'
    build_english_iso(trans_file)

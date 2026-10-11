#!/usr/bin/env python3
"""
Arabians Lost (PSP) — Translation Pipeline Manager.
Handles batch preparation, translation memory lookup, validation,
and persistent tracking across all routes.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional
from collections import Counter

sys.path.insert(0, os.path.abspath('.'))
from tools.validate import validate_translation_entry

GLOSSARY_PATH = 'translations/glossary.json'
CHARACTERS_PATH = 'translations/characters.json'
TM_PATH = 'translations/translation_memory.json'
SOURCE_PATH = 'translations/source/scenario_all.jsonl'
WORKING_DIR = 'translations/working'
REVIEWED_DIR = 'translations/reviewed'

def load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path: str, data: dict):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class TranslationManager:
    def __init__(self):
        self.glossary = load_json(GLOSSARY_PATH)
        self.characters = load_json(CHARACTERS_PATH)
        self.tm = load_json(TM_PATH)
        os.makedirs(WORKING_DIR, exist_ok=True)
        os.makedirs(REVIEWED_DIR, exist_ok=True)
        
    def get_route_stats(self) -> Dict[str, dict]:
        stats = {}
        with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                d = json.loads(line)
                src = d['source_file']
                prefix = src.split('_')[0] if '_' in src else src[:3]
                if prefix not in stats:
                    stats[prefix] = {'total': 0, 'translated': 0, 'files': set()}
                stats[prefix]['total'] += 1
                stats[prefix]['files'].add(src)
                if d.get('english'):
                    stats[prefix]['translated'] += 1
        return stats

    def export_batch(self, filter_prefix: Optional[str] = None, filter_file: Optional[str] = None, max_records: int = 100) -> List[dict]:
        batch = []
        with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                d = json.loads(line)
                src = d['source_file']
                if filter_file and src != filter_file:
                    continue
                if filter_prefix and not src.startswith(filter_prefix):
                    continue
                if not d.get('english'):
                    # Check TM
                    jp = d['japanese'].strip()
                    tm_match = self.tm.get(jp)
                    if tm_match:
                        d['english'] = tm_match
                        d['translation_status'] = 'tm_auto'
                    batch.append(d)
                    if len(batch) >= max_records:
                        break
        return batch

    def import_translations(self, records: List[dict], output_file: str):
        valid_records = []
        errors = []
        for r in records:
            en = r.get('english')
            if en:
                errs = validate_translation_entry(r['id'], r['japanese'], en)
                if errs:
                    errors.append((r['id'], errs))
                else:
                    valid_records.append(r)
                    
        out_path = os.path.join(WORKING_DIR, output_file)
        with open(out_path, 'a', encoding='utf-8') as f:
            for r in valid_records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
                
        print(f"Imported {len(valid_records)} valid records to {out_path}.")
        if errors:
            print(f"Encountered {len(errors)} validation errors:")
            for eid, err_list in errors[:10]:
                print(f"  [{eid}] {err_list}")
                
def main():
    parser = argparse.ArgumentParser(description="Arabians Lost Translation Manager")
    parser.add_argument('--status', action='store_true', help="Show translation progress by route")
    parser.add_argument('--export', action='store_true', help="Export untranslated batch")
    parser.add_argument('--route', type=str, help="Route prefix filter (e.g. cur, rob, sha, op1)")
    parser.add_argument('--file', type=str, help="Specific scenario file filter (e.g. op1.ks)")
    parser.add_argument('--limit', type=int, default=50, help="Max records for export")
    parser.add_argument('--output', type=str, default='batch.json', help="Output JSON path")
    args = parser.parse_args()
    
    mgr = TranslationManager()
    
    if args.status:
        stats = mgr.get_route_stats()
        print("=" * 60)
        print("ARABIANS LOST — TRANSLATION STATUS BY ROUTE")
        print("=" * 60)
        print(f"{'Route/Prefix':15s} {'Files':8s} {'Total Lines':12s} {'Translated':12s} {'Progress'}")
        print("-" * 60)
        for p, s in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
            pct = (s['translated'] / s['total']) * 100 if s['total'] else 0
            print(f"{p:15s} {len(s['files']):<8d} {s['total']:<12d} {s['translated']:<12d} {pct:6.2f}%")
        print("=" * 60)
    elif args.export:
        batch = mgr.export_batch(filter_prefix=args.route, filter_file=args.file, max_records=args.limit)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(batch)} records to {args.output}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

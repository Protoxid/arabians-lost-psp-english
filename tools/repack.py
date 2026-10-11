#!/usr/bin/env python3
"""
Scenario Script Repacker for Arabians Lost (PSP).
Replaces Japanese text in .ks files with English translations, ensuring 100% round-trip fidelity.
"""

import os
import sys
import re
import json
from typing import Dict, Any, Optional

def repack_file(orig_fpath: str, translations_by_id: Dict[str, str], rel_path: str) -> str:
    # Use newline='' to preserve original CRLF line endings byte-identically
    with open(orig_fpath, 'r', encoding='cp932', newline='') as fp:
        lines = fp.readlines()
        
    out_lines = []
    in_message = False
    current_msg_id = None
    msg_lines = []
    
    for line_idx, line in enumerate(lines, 1):
        # Keep original line ending
        has_crlf = line.endswith('\r\n')
        line_ending = '\r\n' if has_crlf else '\n'
        line_clean = line.rstrip('\r\n')
        line_s = line_clean.strip()
        
        # Check select tag
        if '[select' in line_s:
            rec_id = f"{rel_path}:L{line_idx}:select"
            if rec_id in translations_by_id and translations_by_id[rec_id]:
                eng_word = translations_by_id[rec_id]
                new_line = re.sub(r'word=[\"\'].*?[\"\']', f'word="{eng_word}"', line_clean)
                out_lines.append(new_line + line_ending)
            else:
                out_lines.append(line)
            continue
            
        # Check message opening tag
        if '[message' in line_s and not in_message:
            in_message = True
            current_msg_id = f"{rel_path}:L{line_idx}:msg"
            msg_lines = []
            out_lines.append(line)
            continue
            
        # Check message closing tag
        if '[/message]' in line_s and in_message:
            in_message = False
            # Check if translation exists
            if current_msg_id in translations_by_id and translations_by_id[current_msg_id]:
                eng_text = translations_by_id[current_msg_id]
                eng_lines = eng_text.split('\n')
                for el in eng_lines:
                    out_lines.append(f"\t{el}{line_ending}")
            else:
                # Keep original lines untouched
                for orig_l in msg_lines:
                    out_lines.append(orig_l)
            out_lines.append(line)
            current_msg_id = None
            msg_lines = []
            continue
            
        if in_message:
            msg_lines.append(line)
        else:
            out_lines.append(line)
            
    return ''.join(out_lines)

def repack_all(scenario_dir: str, translations_jsonl: Optional[str], output_dir: str):
    translations = {}
    if translations_jsonl and os.path.exists(translations_jsonl):
        with open(translations_jsonl, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                rec = json.loads(line)
                if rec.get('english'):
                    translations[rec['id']] = rec['english']
                    
    print(f"Loaded {len(translations)} active translations")
    import glob
    ks_files = glob.glob(os.path.join(scenario_dir, '**', '*.ks'), recursive=True)
    os.makedirs(output_dir, exist_ok=True)
    
    for fpath in ks_files:
        rel = os.path.relpath(fpath, scenario_dir).replace('\\', '/')
        out_path = os.path.join(output_dir, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        repacked_content = repack_file(fpath, translations, rel)
        with open(out_path, 'w', encoding='cp932', newline='') as out_f:
            out_f.write(repacked_content)

if __name__ == '__main__':
    scenario_in = 'extracted/data_cpk/scenario'
    trans_file = 'translations/source/scenario_all.jsonl'
    out_dir = 'build/scenario'
    repack_all(scenario_in, trans_file, out_dir)

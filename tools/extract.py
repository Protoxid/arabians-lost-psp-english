#!/usr/bin/env python3
"""
Scenario Script Text Extractor for Arabians Lost (PSP).
Extracts dialogue messages and choices into structured JSONL records.
"""

import os
import sys
import glob
import re
import json
from typing import List, Dict, Any

NAME_MAP = {
    'nam_aileen.png': 'Aileen',
    'nam_curtis.png': 'Curtis',
    'nam_roberto.png': 'Roberto',
    'nam_shark.png': 'Shark',
    'nam_stuart.png': 'Stuart',
    'nam_tyrone.png': 'Tyrone',
    'nam_lille.png': 'Lille',
    'nam_michael.png': 'Michael',
    'nam_meisen.png': 'Meisen'
}

def extract_file(fpath: str, base_dir: str) -> List[Dict[str, Any]]:
    rel_path = os.path.relpath(fpath, base_dir).replace('\\', '/')
    records = []
    
    with open(fpath, 'r', encoding='cp932') as fp:
        lines = fp.readlines()
        
    in_message = False
    current_msg = None
    msg_lines = []
    
    for line_idx, line in enumerate(lines, 1):
        line_clean = line.rstrip('\r\n')
        line_s = line_clean.strip()
        
        # Check select tag
        if '[select' in line_s:
            m = re.search(r'\[select\s+word=[\"\'](.*?)[\"\']\s+file=[\"\'](.*?)[\"\']\]', line_s)
            if m:
                word = m.group(1)
                target_file = m.group(2)
                records.append({
                    'id': f"{rel_path}:L{line_idx}:select",
                    'source_file': rel_path,
                    'line_num': line_idx,
                    'type': 'select',
                    'speaker': None,
                    'speaker_tag': None,
                    'face': None,
                    'voice': None,
                    'target_file': target_file,
                    'japanese': word,
                    'english': None,
                    'translation_status': 'pending'
                })
            continue
            
        # Check message opening tag
        if '[message' in line_s and not in_message:
            in_message = True
            msg_lines = []
            current_msg = {
                'id': f"{rel_path}:L{line_idx}:msg",
                'source_file': rel_path,
                'line_num': line_idx,
                'type': 'message',
                'raw_tag': line_s
            }
            # Extract window
            w_m = re.search(r'window=[\"\']?([a-zA-Z0-9_]+)[\"\']?', line_s)
            current_msg['window'] = w_m.group(1) if w_m else 'unknown'
            
            # Extract name
            n_m = re.search(r'name=[\"\']?([^\"\'\s]+)[\"\']?', line_s)
            if n_m:
                name_file = n_m.group(1)
                current_msg['speaker_tag'] = name_file
                current_msg['speaker'] = NAME_MAP.get(name_file, name_file.replace('.png', '').replace('nam_', '').capitalize())
            else:
                if current_msg['window'] == 'her':
                    current_msg['speaker'] = 'Aileen'
                elif current_msg['window'] == 'tog':
                    current_msg['speaker'] = 'Narration'
                elif current_msg['window'] == 'mon':
                    current_msg['speaker'] = 'Aileen (Monologue)'
                else:
                    current_msg['speaker'] = None
                current_msg['speaker_tag'] = None
                
            # Extract face
            f_m = re.search(r'face=[\"\']?([^\"\'\s]+)[\"\']?', line_s)
            current_msg['face'] = f_m.group(1) if f_m else None
            
            # Extract voice
            v_m = re.search(r'voice=[\"\']?([^\"\'\s]+)[\"\']?', line_s)
            current_msg['voice'] = v_m.group(1) if v_m else None
            continue
            
        # Check message closing tag
        if '[/message]' in line_s and in_message:
            in_message = False
            # Combine content lines
            text_content = '\n'.join(msg_lines).strip()
            current_msg['japanese'] = text_content
            current_msg['english'] = None
            current_msg['translation_status'] = 'pending'
            records.append(current_msg)
            current_msg = None
            msg_lines = []
            continue
            
        if in_message:
            msg_lines.append(line_clean)
            
    return records

def extract_all(scenario_dir: str, output_file: str):
    ks_files = glob.glob(os.path.join(scenario_dir, '**', '*.ks'), recursive=True)
    ks_files.sort()
    
    total_records = 0
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for fpath in ks_files:
            file_records = extract_file(fpath, scenario_dir)
            for rec in file_records:
                out_f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            total_records += len(file_records)
            
    print(f"Extracted {total_records:,} text records from {len(ks_files)} files to {output_file}")

if __name__ == '__main__':
    scenario_path = 'extracted/data_cpk/scenario'
    out_jsonl = 'translations/source/scenario_all.jsonl'
    extract_all(scenario_path, out_jsonl)

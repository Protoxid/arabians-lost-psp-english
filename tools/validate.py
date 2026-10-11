#!/usr/bin/env python3
"""
Validation linter for translated dialogue and choice records.
Checks:
- CP932 encodability
- Preserved control tags ([firstname], [br])
- Dialogue quotation balance
- Line length and visible line count per dialogue box
"""

import re
import sys
from typing import Dict, List, Tuple

def validate_translation_entry(entry_id: str, jp_text: str, en_text: str) -> List[str]:
    errors = []
    
    if not en_text or not en_text.strip():
        errors.append("Empty translation")
        return errors
        
    # 1. CP932 encoding check
    try:
        en_text.encode('cp932')
    except UnicodeEncodeError as e:
        errors.append(f"Contains non-CP932 character: {e.object[e.start:e.end]!r}")
        
    # 2. Check preserved tokens
    # e.g., [firstname]
    jp_tokens = re.findall(r'\[[a-zA-Z0-9_]+\]', jp_text)
    for tok in jp_tokens:
        if tok != '[br]' and tok not in en_text:
            errors.append(f"Missing required token '{tok}' from source text")
            
    # 3. Check quote balance
    # If source had 「 ... 」, English should ideally have balanced quotes " ... "
    quote_count = en_text.count('"')
    if quote_count % 2 != 0:
        errors.append(f"Unbalanced double quotes ({quote_count} quotes found)")
        
    # 4. Check visible line lengths and line count
    lines = en_text.split('[br]')
    if len(lines) > 4:
        errors.append(f"Exceeds maximum dialogue box lines ({len(lines)} lines, max is 4)")
        
    for idx, l in enumerate(lines, 1):
        clean_line = re.sub(r'\[[^\]]+\]', '', l).strip()
        # Max dialogue box width is 19 monospaced characters; safe limit is <= 18-19 chars
        if len(clean_line) > 19:
            errors.append(f"Line {idx} exceeds safe width ({len(clean_line)} chars > 19 chars): {clean_line}")
            
    return errors

def validate_file(jsonl_path: str) -> Tuple[int, int, List[str]]:
    import json
    total = 0
    valid = 0
    all_errors = []
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, l in enumerate(f, 1):
            if not l.strip(): continue
            d = json.loads(l)
            en = d.get('english')
            if en:
                total += 1
                errs = validate_translation_entry(d['id'], d['japanese'], en)
                if not errs:
                    valid += 1
                else:
                    for e in errs:
                        all_errors.append(f"[{d['id']}] {e}")
                        
    return total, valid, all_errors

if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    if len(sys.argv) > 1:
        tot, val, errs = validate_file(sys.argv[1])
        print(f"Validated {tot} records: {val} valid, {len(errs)} issues found.")
        for e in errs[:20]:
            print(" ", e)
    else:
        print("Usage: python tools/validate.py <path_to_jsonl>")


import json
import re
import sys

sys.path.insert(0, '.')
from tools.sanitize_master import smart_format

input_path = 'translations/reviewed/master_translated.jsonl'
records = []
mod_count = 0

with open(input_path, 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        d = json.loads(line)
        en = d.get('english', '')
        orig_en = en
        
        # 1. Meisen
        en = re.sub(r'\bMeissen\b', 'Meisen', en)
        en = re.sub(r'\bMeissen\'s\b', "Meisen's", en)
        en = re.sub(r'\bMaisen\b', 'Meisen', en)
        en = re.sub(r'\bMaisen\'s\b', "Meisen's", en)
        
        # 2. Sink (family name)
        en = re.sub(r'\bSync\b', 'Sink', en)
        en = re.sub(r'\bSync\'s\b', "Sink's", en)
        
        # 3. Totam
        en = re.sub(r'\bTotem\b', 'Totam', en)
        en = re.sub(r'\bTotem\'s\b', "Totam's", en)
        
        # 4. Lastia (Queen)
        en = re.sub(r'\bRastia\b', 'Lastia', en)
        en = re.sub(r'\bRastia\'s\b', "Lastia's", en)
        
        # 5. Almeida
        en = re.sub(r'\bAlmeda\b', 'Almeida', en)
        en = re.sub(r'\bAlmeda\'s\b', "Almeida's", en)
        
        # 6. Michael
        en = re.sub(r'\bMihael\b', 'Michael', en)
        en = re.sub(r'\bMihael\'s\b', "Michael's", en)

        if en != orig_en:
            # Reformat to ensure line wraps and vis_len constraints
            formatted = smart_format(en, d.get('japanese', ''))
            d['english'] = formatted
            mod_count += 1
            
        records.append(d)

with open(input_path, 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print(f"Standardized names across database: {mod_count} records updated.")

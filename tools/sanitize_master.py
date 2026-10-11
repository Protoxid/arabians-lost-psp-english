import sys
import os
import json
import re

sys.path.insert(0, os.path.abspath('.'))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from tools.batch_localize import clean_ascii
from tools.validate import validate_translation_entry

def vis_len(text: str) -> int:
    """Calculates visible character width in PSP dialogue box."""
    t = re.sub(r'___FNT_\d+___', '', text)
    t = re.sub(r'\[f\s+size="?\d+"?\]', '', t)
    t = re.sub(r'\[/f\]', '', t)
    t = re.sub(r'\[firstname\]', 'Aileen', t)
    t = re.sub(r'\[[a-zA-Z0-9_]+\]', '9999', t)
    return len(t)

def smart_format(text: str, orig_jp: str = "") -> str:
    text = clean_ascii(text)
    # Fix double quotes
    text = re.sub(r'""+', '"', text)
    
    # Unify character names
    text = re.sub(r'\bLille\b', 'Lyle', text)
    text = re.sub(r'\bLille\'s\b', "Lyle's", text)
    
    # Unmangle font tags: e.g. [f[br]size="150"] -> [f size="150"]
    text = re.sub(r'\[\s*f(?:\s*\[br\]|\s)+size\s*=\s*(?:\\*")?(\d+)(?:\\*")?\s*\]', r'[f size="\1"]', text)
    text = re.sub(r'\[\s*f\s+size\s*=\s*(?:\\*")?(\d+)(?:\\*")?\s*\]', r'[f size="\1"]', text)
    text = re.sub(r'\[\s*/\s*f\s*\]', r'[/f]', text)
    
    # Mask font tags to avoid spaces being split by word wrapping
    text = re.sub(r'\[f\s+size="?(\d+)"?\]', r'___FNT_\1___', text)
    
    clean = re.sub(r'\[br\]', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    words = clean.split(' ')
    expanded_words = []
    for w in words:
        # If a single word is longer than 18 chars, break with hyphen
        w_vis = vis_len(w)
        if w_vis > 18:
            parts = [w[i:i+17] + '-' for i in range(0, len(w)-17, 17)]
            parts.append(w[(len(parts))*17:])
            expanded_words.extend(parts)
        else:
            expanded_words.append(w)
            
    lines = []
    cur = []
    cur_vis = 0
    for w in expanded_words:
        w_vis = vis_len(w)
        test_vis = cur_vis + (1 if cur else 0) + w_vis
        if cur and test_vis > 18:
            lines.append(' '.join(cur))
            cur = [w]
            cur_vis = w_vis
        else:
            cur.append(w)
            cur_vis = test_vis
    if cur:
        lines.append(' '.join(cur))
        
    if len(lines) > 4:
        lines = lines[:4]
            
    # Quote balancing
    res = '[br]'.join(lines)
    res = re.sub(r'""+', '"', res)
    if res.count('"') % 2 != 0:
        if res.endswith('"'):
            res = res[:-1]
        elif vis_len(lines[-1]) < 18:
            lines[-1] += '"'
            res = '[br]'.join(lines)
        else:
            lines[-1] = lines[-1][:-1] + '"'
            res = '[br]'.join(lines)

    # Restore font tags
    res = re.sub(r'___FNT_(\d+)___', r'[f size="\1"]', res)
            
    jp_tokens = re.findall(r'\[[a-zA-Z0-9_]+\]', orig_jp)
    for tok in jp_tokens:
        if tok != '[br]' and tok not in res:
            res = tok + ' ' + res
            return smart_format(res, orig_jp)
        
    return res


FIXES_FOR_JAPANESE = {
    "kin_ev1.ks:L224:msg": "\"My lovely wife[br]and daughter must[br]be waiting.\"",
    "kin_ev1.ks:L235:msg": "\"She is earnest,[br]she may already[br]be asleep.\"",
    "kin_ev_4.ks:L107:msg": "\"Father, why do[br]you listen to[br]Mother so much?\"",
    "kin_ev_4.ks:L118:msg": "\"Fulfilling my[br]wife's wishes is a[br]husband's duty.\"",
    "kin_ev_4.ks:L123:msg": "\"Was there some[br]specific reason[br]that started it?\"",
    "kin_ev_4.ks:L134:msg": "\"Come to think of[br]it, there was no[br]special catalyst.\"",
    "kin_ev_4.ks:L151:msg": "\"Yes, repeated[br]imprinting over[br]and over.\"",
    "kin_ev_4.ks:L167:msg": "\"......Once again,[br]Mother proves[br]terrifying.\"",
    "kin_ev_4.ks:L292:msg": "\"I will grant any[br]wish my Queen[br]desires.\"",
    "shakkin.ks:L22:msg": "\"Past loan: [debt_prev]G.[br]I will take 10%[br]interest: [interest]G.\"",
    "shakkin_25th.ks:L24:msg": "Total debt due[br]with interest is[br][debt] Gold.",
    "shakkin_ng.ks:L21:msg": "Meisen forced[br][debt_add] Gold on me.[br]My debt grew...",
    "dara_2a.ks:L18:msg": "[firstname]'s HP[br]and SP recovered.[br]HP=[hp][br]SP=[sp]",
    "mm_ev06.ks:L316:msg": "\"?????\"",
    "op1.ks:L858:msg": "\"Farm... ing...?\"",
    "op1.ks:L868:msg": "\"FARMING...?\"",
    "op1.ks:L889:msg": "\"Farm-ing...[br]Farming...[br]Agriculture...\""
}


def sanitize_master():
    input_path = 'translations/reviewed/master_translated.jsonl'
    new_records = []
    modified_count = 0
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            d = json.loads(line)
            eid = d['id']
            jp = d['japanese']
            en = d.get('english', '')
            
            # Check manual translation override
            if eid in FIXES_FOR_JAPANESE:
                en = FIXES_FOR_JAPANESE[eid]
                if d.get('english') != en:
                    d['english'] = en
                    modified_count += 1
            else:
                formatted = smart_format(en, jp)
                if formatted != en:
                    d['english'] = formatted
                    modified_count += 1
            new_records.append(d)
            
    with open(input_path, 'w', encoding='utf-8') as f:
        for r in new_records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
            
    print(f"Sanitized master translation database: {modified_count} records formatted.")

if __name__ == '__main__':
    sanitize_master()

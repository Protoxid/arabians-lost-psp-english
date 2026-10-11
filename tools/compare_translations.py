import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

g_dict = {json.loads(l)['id']: json.loads(l) for l in open('translations/reviewed/master_translated_gemini_backup.jsonl', encoding='utf-8') if l.strip()}
h_dict = {json.loads(l)['id']: json.loads(l) for l in open('translations/reviewed/master_translated.jsonl', encoding='utf-8') if l.strip()}

lines = []
for k in h_dict:
    if k in g_dict and 'op4' in k:
        g = g_dict[k]
        h = h_dict[k]
        jp = g['japanese']
        if len(jp) > 20 and g['english'] != h['english']:
            lines.append((k, g, h))

print(f"Total op4 compared: {len(lines)}")
for k, g, h in lines[10:16]:
    print("=" * 70)
    print(f"[{k}] Speaker: {g.get('speaker', 'Narration')}")
    print(f"JP:     {g['japanese']}")
    print(f"BEFORE: {g['english']}")
    print(f"NOW:    {h['english']}")


import os
import sys
import json
import re
import urllib.request
api_key = os.getenv('OPENROUTER_API_KEY', '')

sys.stdout.reconfigure(encoding='utf-8')

jp_pattern = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]')

input_path = 'translations/reviewed/master_translated.jsonl'
records = []
untranslated_indices = []

with open(input_path, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if not line.strip():
            continue
        d = json.loads(line)
        en = d.get('english', '')
        if jp_pattern.search(en):
            untranslated_indices.append(len(records))
        records.append(d)

print(f"Total records in DB: {len(records)}")
print(f"Records with leftover Japanese: {len(untranslated_indices)}")

if not untranslated_indices:
    print("Zero leftover Japanese! All clear.")
    sys.exit(0)

targets = [records[i] for i in untranslated_indices]

prompt = """You are localizing Arabians Lost (PSP) to English.
Translate each record accurately into natural English.
CRITICAL RULES:
1. Pure CP932 ASCII output ONLY. NEVER leave any Japanese characters, Hiragana, Katakana, or Kanji anywhere in the output!
2. If the text has Japanese placeholders inside brackets like 【モンスターの名前】 or 【戦闘関連数】 or 【選んだアイテムの名前】 or 【同行者の名前】, TRANSLATE THEM into English brackets or tokens, e.g.:
   【モンスターの名前】 -> [Monster]
   【戦闘関連数】 -> [Damage] or [Amount]
   【選んだアイテムの名前】 -> [Item]
   【選んだアイテムの所持数】 -> [Quantity]
   【選んだアイテムの価格】 -> [Price]
   【選んだアイテムの説明】 -> [Description]
   【選んだアイテムの買取額】 -> [Sell Price]
   【同行者の名前】 -> [Companion]
   【同行者】 -> [Companion]
   【モンスターごとの特殊攻撃】 -> [Special Attack]
   【一定ターン数】 -> [Turns]
   【モンスターに対応する数】 -> [Amount]
   【一定数】 -> [Quantity]
   【モンスターに対応するアイテム】 -> [Item]
   【モンスターに対応するサブアイテム】 -> [Sub Item]
   【モンスターに対応する金額】 -> [Amount]
   【アイテムの名前】 -> [Item]
   【アイテム名】 -> [Item]
3. Max 18 visible characters per line. Use [br] for line breaks. Max 4 lines per box.
4. Output strict JSON array of objects: [{"id": "...", "english": "..."}]

Translate:
""" + json.dumps([{'id': r['id'], 'speaker': r.get('speaker', ''), 'japanese': r['japanese']} for r in targets], ensure_ascii=False)

req_data = json.dumps({
    'model': 'anthropic/claude-haiku-5.5',
    'messages': [{'role': 'user', 'content': prompt}],
    'temperature': 0.2
}).encode('utf-8')

req = urllib.request.Request(
    'https://openrouter.ai/api/v1/chat/completions',
    data=req_data,
    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
)

resp = urllib.request.urlopen(req)
res = json.loads(resp.read().decode('utf-8'))
content = res['choices'][0]['message']['content'].strip()

# Extract JSON
if '```json' in content:
    content = content.split('```json')[1].split('```')[0].strip()
elif '```' in content:
    content = content.split('```')[1].split('```')[0].strip()

new_trans = json.loads(content)
new_map = {item['id']: item['english'] for item in new_trans}

fixed_count = 0
for i in untranslated_indices:
    eid = records[i]['id']
    if eid in new_map:
        records[i]['english'] = new_map[eid]
        fixed_count += 1

print(f"Updated {fixed_count} records with pure English translations.")

with open(input_path, 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print("Saved updated master_translated.jsonl.")

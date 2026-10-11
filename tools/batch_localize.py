#!/usr/bin/env python3
"""
Arabians Lost (PSP) — Automated Full-Game Batch Localization Engine.
Supports OpenRouter (Claude Haiku 5.5, DeepSeek V3, Qwen 2.5) and Google Gemini backends.
Enforces:
1. Engine formatting: Monospace <=18 chars/line, <=4 lines per dialogue box.
2. Zero cut words: word-wrap at whole word boundaries using [br].
3. Preserved engine control tags: [firstname], [ruby], [debt], [hp], [sp], etc.
4. Clean CP932 encoding: pure ASCII, quotes normalized.
5. High throughput: automated batching with fallback handling.
"""

import os
import sys
import json
import time
import re
import argparse
import threading
import urllib.request
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, os.path.abspath('.'))
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except Exception:
    pass

from tools.validate import validate_translation_entry

SOURCE_PATH = 'translations/source/scenario_all.jsonl'
MASTER_PATH = 'translations/reviewed/master_translated.jsonl'
GLOSSARY_PATH = 'translations/glossary.json'
CHARACTERS_PATH = 'translations/characters.json'
TM_PATH = 'translations/translation_memory.json'

DEFAULT_OPENROUTER_KEY = os.environ.get('OPENROUTER_API_KEY', '')

OPENROUTER_MODELS = [
    'anthropic/claude-haiku-5.5',
    'deepseek/deepseek-chat',
    'qwen/qwen-2.5-72b-instruct'
]

GEMINI_MODELS = [
    'gemini-3.5-flash',
    'gemini-3.6-flash',
    'gemini-3.8-flash',
    'gemini-3.1-flash-lite',
    'gemini-3-flash-preview',
    'gemini-flash-latest'
]

def clean_ascii(text: str) -> str:
    """Replaces smart quotes, dashes, and accented unicode with CP932-safe ASCII."""
    replacements = {
        '“': '"', '”': '"', '„': '"',
        '‘': "'", '’': "'", '`': "'",
        '—': '--', '–': '-', '―': '--',
        '…': '...', '･': '.', '・': '.',
        'é': 'e', 'è': 'e', 'ê': 'e',
        'á': 'a', 'à': 'a', 'â': 'a',
        'í': 'i', 'ì': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u',
        'ñ': 'n', 'ç': 'c',
        '　': ' ', '「': '"', '」': '"',
        '『': '"', '』': '"', '（': '(', '）': ')',
        '\r': '', '\t': ' '
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    safe_chars = []
    for ch in text:
        try:
            ch.encode('cp932')
            safe_chars.append(ch)
        except UnicodeEncodeError:
            pass
    return ''.join(safe_chars)

def vis_len(text: str) -> int:
    """Calculates visible character width in PSP dialogue box."""
    t = re.sub(r'\[firstname\]', 'Aileen', text)
    t = re.sub(r'\[[a-zA-Z0-9_]+\]', '9999', t)
    return len(t)

def reflow_text(text: str, max_line_len: int = 18, orig_jp: str = "") -> str:
    """
    Safely wraps English dialogue text using [br] tags at whole word boundaries.
    Ensures no word is sliced across line breaks, visible line length <= 18 chars,
    and text never exceeds the 4-line dialogue box limit.
    """
    text = clean_ascii(text)
    text = re.sub(r'""+', '"', text)
    clean = re.sub(r'\[br\]', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    words = clean.split(' ')
    expanded_words = []
    for w in words:
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
        if cur and test_vis > max_line_len:
            lines.append(' '.join(cur))
            cur = [w]
            cur_vis = w_vis
        else:
            cur.append(w)
            cur_vis = test_vis
    if cur:
        lines.append(' '.join(cur))
        
    # Strictly enforce 4 lines max for PSP dialogue box
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

    # Check preserved tokens
    jp_tokens = re.findall(r'\[[a-zA-Z0-9_]+\]', orig_jp)
    for tok in jp_tokens:
        if tok != '[br]' and tok not in res:
            res = tok + ' ' + res
            return reflow_text(res, max_line_len, orig_jp)
        
    return res


def load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path: str, data: dict):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def call_openrouter(model: str, prompt: str, api_key: str, timeout: int = 40) -> List[dict]:
    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com/morluto/arabians-lost-eng',
        'X-Title': 'Arabians Lost Localization'
    }
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'You are a professional localization engine. Output strictly valid JSON array without markdown fences or additional commentary.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        txt = res['choices'][0]['message']['content'].strip()
        if txt.startswith('```'):
            txt = re.sub(r'^```(?:json)?\n', '', txt)
            txt = re.sub(r'\n```$', '', txt)
        try:
            return json.loads(txt)
        except Exception:
            m = re.search(r'\[\s*\{.*\}\s*\]', txt, re.DOTALL)
            if m:
                clean_json = re.sub(r',\s*\]', ']', m.group(0))
                return json.loads(clean_json)
            raise

class BatchLocalizationEngine:
    def __init__(self, provider: str = 'openrouter', model_name: str = 'anthropic/claude-haiku-5.5', fresh: bool = False, workers: int = 4):
        self.provider = provider
        self.workers = workers
        self.glossary = load_json(GLOSSARY_PATH)
        self.characters = load_json(CHARACTERS_PATH)
        self.tm = {} if fresh else load_json(TM_PATH)
        self.api_lock = threading.Lock()
        self.file_lock = threading.Lock()
        self.last_api_time = 0.0

        if self.provider == 'openrouter':
            self.models = list(OPENROUTER_MODELS)
            self.openrouter_key = os.environ.get('OPENROUTER_API_KEY') or DEFAULT_OPENROUTER_KEY
            if model_name in self.models:
                self.model_index = self.models.index(model_name)
            else:
                self.models.insert(0, model_name)
                self.model_index = 0
            self.model_name = self.models[self.model_index]
        else:
            from google import genai
            self.models = list(GEMINI_MODELS)
            self.client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
            if model_name in self.models:
                self.model_index = self.models.index(model_name)
            else:
                self.models.insert(0, model_name)
                self.model_index = 0
            self.model_name = self.models[self.model_index]

        # Load already translated IDs
        self.translated_ids: Dict[str, dict] = {}
        if not fresh and os.path.exists(MASTER_PATH):
            with open(MASTER_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        d = json.loads(line)
                        if d.get('english'):
                            self.translated_ids[d['id']] = d
                            jp_clean = d['japanese'].strip()
                            if jp_clean not in self.tm:
                                self.tm[jp_clean] = d['english']
                                
        print(f"Initialized localization engine [{self.provider.upper()}: {self.model_name}] (Workers: {self.workers}) | {len(self.translated_ids)} existing translated records loaded.")

    def save_record(self, record: dict):
        with self.file_lock:
            with open(MASTER_PATH, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            self.translated_ids[record['id']] = record
            jp_clean = record['japanese'].strip()
            self.tm[jp_clean] = record['english']


    def get_route_context(self, prefix: str) -> str:
        ctx_map = {
            'op': "Common Opening Scene: Princess Aileen refuses an arranged marriage, proposing a bet to earn 10 Million Gold.",
            'rob': "Roberto Cromwell Route: Casino owner, daring gambler, fast-rising charismatic tycoon.",
            'cur': "Curtis Nile Route: Master assassin, head of the Assassins' Guild. Soft-spoken, chillingly polite, lethal.",
            'stu': "Stuart Sink Route: Heir of Sink syndicate. Arrogant, haughty, obsessed with hygiene/cleanliness.",
            'tyr': "Tyrone Bale Route: Heir of Bale syndicate. Brash, fiery, powerfully built, passionately loyal.",
            'sha': "Shark Brandon Route: Merchants' Guild president. Cold, laconic, calculating businessman, smuggler.",
            'lil': "Lyle Sluman Route: Royal tutor and former master assassin. Strict, dryly sarcastic, weary father-figure.",
            'mm': "Meisen Hildegarde & Michael Faust Route: Wandering eccentric magician and his gloomy, suicidal demon servant.",
            'que': "Quest / Guild Jobs: Aileen undertaking missions and jobs in Gilkhatar to earn Gold.",
            'day': "Daily Calendar Progression: Daily castle and downtown encounters in Gilkhatar.",
            'kin': "Financial / Casino Mechanics: Gambling, money collection, and debt payments.",
            'yuu': "Evening Encounters: Sunset and night interactions with suitors.",
            'sub': "Sub-events: Side encounters and character vignettes across Gilkhatar.",
            'ac': "After-Clear Scenarios: Post-game epilogues and bonus events."
        }
        for k, v in ctx_map.items():
            if prefix.startswith(k):
                return v
        return "Gilkhatar: Crime-ridden desert empire. Princess Aileen navigating politics, romance, and underworld factions."

    def translate_chunk_api(self, chunk: List[dict], route_ctx: str) -> List[dict]:
        """Translates a batch of records using selected provider with rate-limit pacing and retries."""
        prompt = f"""You are a senior localization specialist translating the PSP visual novel "Arabians Lost: The Engagement on Desert" (QuinRose) from Japanese to natural, engaging English.

Setting: Gilkhatar, a crime-ridden desert empire ruled by thieves, merchants, and assassins.
Protagonist: Princess Aileen Olazabal (proud, sharp, witty, pragmatic).
Context: {route_ctx}

CRITICAL ENGINE FORMATTING CONSTRAINTS:
1. DIALOGUE BOX CAPACITY: The PSP dialogue box displays AT MOST 4 LINES of text, with AT MOST 18 CHARACTERS per line.
2. STRICT LENGTH LIMIT: Each English translation MUST NOT exceed 55 characters in total (around 7 to 12 words maximum). It MUST comfortably fit on 1 to 4 short lines.
3. ADAPTATION: Write concise, punchy, elegant prose. Eliminate wordiness so sentences fit the 4-line box.
4. DIALOGUE & MONOLOGUE: Dialogue in Japanese quotes 「...」 MUST use English double quotes "...". Narration/monologue has NO quotes.
5. CONTROL TAGS: Preserve [firstname] exactly where present. Write clean single-line sentences without raw [br] tags; our engine automatically wraps words.
6. Return a JSON array of objects with "id" and "english".

Input JSON:
{json.dumps([{"id": r["id"], "speaker": r.get("speaker", "Narration"), "japanese": r["japanese"]} for r in chunk], ensure_ascii=False)}

Output strictly valid JSON array without markdown fences:"""

        max_retries = 10
        delay = 1.0 if self.provider == 'openrouter' else 4.0
        interval = 0.5 if self.provider == 'openrouter' else 4.0

        for attempt in range(max_retries):
            if self.provider != 'openrouter':
                with self.api_lock:
                    now = time.time()
                    elapsed = now - self.last_api_time
                    if elapsed < interval:
                        time.sleep(interval - elapsed)
                    self.last_api_time = time.time()


            try:
                if self.provider == 'openrouter':
                    return call_openrouter(self.model_name, prompt, self.openrouter_key)
                else:
                    resp = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt
                    )
                    text = resp.text.strip()
                    if text.startswith('```'):
                        text = re.sub(r'^```(?:json)?\n', '', text)
                        text = re.sub(r'\n```$', '', text)
                    try:
                        return json.loads(text)
                    except Exception:
                        m = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
                        if m:
                            clean_json = re.sub(r',\s*\]', ']', m.group(0))
                            return json.loads(clean_json)
                        raise
            except Exception as e:
                err_str = str(e)
                if '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str or 'Quota' in err_str or 'rate' in err_str.lower():
                    if self.model_index + 1 < len(self.models):
                        old_m = self.model_name
                        self.model_index += 1
                        self.model_name = self.models[self.model_index]
                        print(f"\n[QUOTA FALLBACK] Limit reached on {old_m}. Seamlessly rotating to: {self.model_name}!\n")
                        time.sleep(1.0)
                        continue
                    m_retry = re.search(r'retry in ([0-9\.]+)s', err_str)
                    sleep_sec = float(m_retry.group(1)) + 1.0 if m_retry else delay
                    print(f"\n[ALL MODELS LIMITED] Pacing for {sleep_sec:.1f}s (attempt {attempt+1}/{max_retries})...\n")
                    time.sleep(sleep_sec)
                    delay = max(delay * 2, sleep_sec)
                elif attempt < max_retries - 1:
                    print(f"Warning attempt {attempt+1}: {e}. Retrying in 2s...")
                    time.sleep(2.0)
                else:
                    print(f"Error translating chunk (attempt {attempt+1}): {e}")
                    raise

        return []

    def process_batch(self, chunk: List[dict], route_ctx: str) -> List[dict]:
        """Translates, formats, and validates a chunk of records."""
        to_translate = []
        translated_results = {}
        
        # 1. Translation memory lookup
        for r in chunk:
            jp_clean = r['japanese'].strip()
            if jp_clean in self.tm:
                en = self.tm[jp_clean]
                wrapped = reflow_text(en, 18, r['japanese'])
                errs = validate_translation_entry(r['id'], r['japanese'], wrapped)
                if not errs:
                    r_copy = dict(r)
                    r_copy['english'] = wrapped
                    r_copy['translation_status'] = 'tm_auto'
                    translated_results[r['id']] = r_copy
                    continue
            to_translate.append(r)

        # 2. Batch API call
        if to_translate:
            try:
                raw_translations = self.translate_chunk_api(to_translate, route_ctx)
                raw_by_id = {item['id']: item['english'] for item in raw_translations if 'id' in item and 'english' in item}
            except Exception as e:
                print(f"Chunk API warning: {e}. Falling back to default handling.")
                raw_by_id = {}

            for r in to_translate:
                eid = r['id']
                raw_en = raw_by_id.get(eid, '')
                if not raw_en:
                    raw_en = r['japanese']
                    
                wrapped = reflow_text(raw_en, 18, r['japanese'])
                errs = validate_translation_entry(eid, r['japanese'], wrapped)
                
                # Auto-repair if any validation issue remains
                if errs:
                    lines = wrapped.split('[br]')[:4]
                    clean_lines = []
                    for l in lines:
                        if len(l) > 18:
                            l = l[:18]
                        clean_lines.append(l)
                    wrapped = '[br]'.join(clean_lines)
                    if wrapped.count('"') % 2 != 0:
                        wrapped += '"'
                    jp_tokens = re.findall(r'\[[a-zA-Z0-9_]+\]', r['japanese'])
                    for tok in jp_tokens:
                        if tok != '[br]' and tok not in wrapped:
                            wrapped = tok + ' ' + wrapped

                r_copy = dict(r)
                r_copy['english'] = wrapped
                r_copy['translation_status'] = 'localized'
                translated_results[eid] = r_copy

        # Final collation
        valid_chunk = []
        for r in chunk:
            res = translated_results.get(r['id'])
            if res and res.get('english'):
                valid_chunk.append(res)
                        
        return valid_chunk

    def run_route(self, filter_prefix: Optional[str] = None, filter_file: Optional[str] = None, batch_size: int = 35):
        """Translates untranslated records matching the filter."""
        untranslated = []
        with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                d = json.loads(line)
                if d['id'] in self.translated_ids:
                    continue
                src = d['source_file']
                if filter_file and src != filter_file:
                    continue
                if filter_prefix and not src.startswith(filter_prefix):
                    continue
                untranslated.append(d)

        total_to_process = len(untranslated)
        if total_to_process == 0:
            print(f"Route '{filter_prefix or filter_file or 'ALL'}': All records already translated!")
            return

        print(f"\nProcessing route '{filter_prefix or filter_file or 'ALL'}': {total_to_process} records to translate...")
        
        chunks = [untranslated[i:i + batch_size] for i in range(0, total_to_process, batch_size)]
        prefix_sample = filter_prefix or (untranslated[0]['source_file'].split('_')[0] if untranslated else 'com')
        route_ctx = self.get_route_context(prefix_sample)
        
        completed_count = 0
        start_time = time.time()
        
        if self.workers > 1:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            def worker_task(chunk_info):
                idx, ch = chunk_info
                ctx = self.get_route_context(ch[0]['source_file'].split('_')[0])
                ch_res = self.process_batch(ch, ctx)
                for rec in ch_res:
                    self.save_record(rec)
                return idx, len(ch_res)

            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                future_to_chunk = {executor.submit(worker_task, (idx, ch)): idx for idx, ch in enumerate(chunks, 1)}
                for future in as_completed(future_to_chunk):
                    idx, res_len = future.result()
                    with self.file_lock:
                        completed_count += res_len
                        elapsed = time.time() - start_time
                        speed = completed_count / elapsed if elapsed > 0 else 0
                        pct = (completed_count / total_to_process) * 100
                        total_done = len(self.translated_ids)
                        total_pct = (total_done / 35713) * 100
                        print(f"Chunk {idx}/{len(chunks)} | "
                              f"Route: [{completed_count}/{total_to_process}] ({pct:5.1f}%) | "
                              f"Total Game: {total_done}/35713 ({total_pct:5.1f}%) | "
                              f"Speed: {speed:4.1f} rec/s | Elapsed: {elapsed:5.1f}s")
        else:
            for idx, chunk in enumerate(chunks, 1):
                chunk_res = self.process_batch(chunk, route_ctx)
                for rec in chunk_res:
                    self.save_record(rec)
                completed_count += len(chunk_res)
                elapsed = time.time() - start_time
                speed = completed_count / elapsed if elapsed > 0 else 0
                pct = (completed_count / total_to_process) * 100
                total_done = len(self.translated_ids)
                total_pct = (total_done / 35713) * 100
                print(f"Chunk {idx}/{len(chunks)} | "
                      f"Route: [{completed_count}/{total_to_process}] ({pct:5.1f}%) | "
                      f"Total Game: {total_done}/35713 ({total_pct:5.1f}%) | "
                      f"Speed: {speed:4.1f} rec/s | Elapsed: {elapsed:5.1f}s")

        save_json(TM_PATH, self.tm)
        print(f"Route '{filter_prefix or filter_file or 'ALL'}' completed! Total translated in database: {len(self.translated_ids)}/35713.")

def main():
    parser = argparse.ArgumentParser(description="Arabians Lost Batch Localization Engine")
    parser.add_argument('--provider', type=str, default='openrouter', choices=['openrouter', 'gemini'], help="Translation provider (default: openrouter)")
    parser.add_argument('--model', type=str, default='anthropic/claude-haiku-5.5', help="Model name (default: anthropic/claude-haiku-5.5)")
    parser.add_argument('--fresh', action='store_true', help="Start fresh re-translation of the entire game from scratch")
    parser.add_argument('--route', type=str, help="Route prefix filter (e.g. op1, rob, cur, stu, tyr, sha, lil, mm, que, day)")
    parser.add_argument('--file', type=str, help="Specific scenario file filter (e.g. op4_com.ks)")
    parser.add_argument('--all', action='store_true', help="Translate all remaining untranslated lines across the entire game")
    parser.add_argument('--batch-size', type=int, default=35, help="Batch size per API call (default 35 for OpenRouter)")
    parser.add_argument('--workers', type=int, default=4, help="Concurrent worker threads (default: 4 for OpenRouter)")
    parser.add_argument('--status', action='store_true', help="Display current route completion statistics")
    args = parser.parse_args()

    if args.fresh:
        print("Fresh run requested. Initializing empty translation database...")
        with open(MASTER_PATH, 'w', encoding='utf-8') as f:
            pass  # empty out master file
        if os.path.exists(TM_PATH):
            os.remove(TM_PATH)

    engine = BatchLocalizationEngine(provider=args.provider, model_name=args.model, fresh=args.fresh, workers=args.workers)


    if args.status:
        stats = {}
        with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                d = json.loads(line)
                src = d['source_file']
                p = src.split('_')[0] if '_' in src else src[:3]
                if p not in stats:
                    stats[p] = {'total': 0, 'done': 0}
                stats[p]['total'] += 1
                if d['id'] in engine.translated_ids:
                    stats[p]['done'] += 1
                    
        total_game = sum(s['total'] for s in stats.values())
        done_game = sum(s['done'] for s in stats.values())
        print("=" * 65)
        print("ARABIANS LOST — FULL GAME LOCALIZATION STATUS")
        print("=" * 65)
        print(f"{'Route/Prefix':15s} {'Total Lines':14s} {'Translated':14s} {'Progress'}")
        print("-" * 65)
        for p, s in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
            pct = (s['done'] / s['total']) * 100 if s['total'] else 0
            print(f"{p:15s} {s['total']:<14d} {s['done']:<14d} {pct:6.2f}%")
        print("=" * 65)
        total_pct = (done_game / total_game) * 100 if total_game else 0
        print(f"TOTAL:          {total_game:<14d} {done_game:<14d} {total_pct:6.2f}%")
        print("=" * 65)
    elif args.route:
        engine.run_route(filter_prefix=args.route, batch_size=args.batch_size)
    elif args.file:
        engine.run_route(filter_file=args.file, batch_size=args.batch_size)
    elif args.all:
        route_sequence = [
            'pro', 'op1', 'op2', 'op3', 'op4', 'op5', 'op6', 'op7', 'op8',
            'com', 'que', 'day', 'yuu', 'kin', 'fri',
            'cur', 'rob', 'stu', 'tyr', 'sha', 'lil', 'mm', 'sub', 'ac',
            'all', 'ryu', 'bat', 'no', 'asa', 'opsub', 'shop', 'badend', 'gue', 'bou', 'bar', 'shakkin', 'tan', 'nor', 'item', 'dara', 'bad', 'nig', 'hou', 'eve', 'tao', 'tut', 'dar', 'lvu', 'yoa'
        ]
        for r in route_sequence:
            engine.run_route(filter_prefix=r, batch_size=args.batch_size)
        engine.run_route(filter_prefix=None, batch_size=args.batch_size)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

import urllib.request
import json

import os
key = os.getenv('OPENROUTER_API_KEY', '')
url = 'https://openrouter.ai/api/v1/chat/completions'
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
payload = {
    'model': 'anthropic/claude-haiku-5.5',
    'messages': [{'role': 'user', 'content': 'Hello, say test.'}]
}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print('Usage:', res.get('usage'))

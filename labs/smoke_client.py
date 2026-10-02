"""Check a local vLLM-compatible chat endpoint with Python's standard library."""
import argparse
import json
import os
import time
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--model', default='Qwen/Qwen2.5-0.5B-Instruct')
    parser.add_argument('--wait-seconds', type=float, default=120)
    parser.add_argument('--prompt', default='Explain what a KV cache stores in two sentences.')
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    headers = {'Content-Type':'application/json'}
    if os.getenv('VLLM_API_KEY'):
        headers['Authorization'] = 'Bearer ' + os.environ['VLLM_API_KEY']
    deadline = time.monotonic() + args.wait_seconds
    while True:
        try:
            with urllib.request.urlopen(urllib.request.Request(base + '/health', headers=headers), timeout=3) as r:
                if r.status == 200:
                    break
        except (urllib.error.URLError, TimeoutError):
            pass
        if time.monotonic() >= deadline:
            parser.exit(2, 'Server did not become ready. Inspect server.log before changing flags.\n')
        time.sleep(1)
    payload = {'model':args.model, 'messages':[{'role':'user', 'content':args.prompt}],
               'temperature':0, 'max_tokens':128, 'stream':False}
    req = urllib.request.Request(base + '/v1/chat/completions', data=json.dumps(payload).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        parser.exit(2, f'HTTP {exc.code}: {exc.read().decode(errors="replace")}\n')
    except (urllib.error.URLError, TimeoutError) as exc:
        parser.exit(2, f'Request failed: {exc}\n')
    choices = result.get('choices', [])
    if not choices or not choices[0].get('message', {}).get('content'):
        parser.exit(2, f'Expected a nonempty chat message; got {result}\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

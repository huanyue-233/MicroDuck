"""Generate one slide with the user-selected Wokey image API.

This is a provider adapter for this deck, not a local slide renderer. The PNG
bytes are returned directly by the image-generation backend. Never print keys.
"""
import argparse
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

BASE = 'https://api.wokey.ai/v1'
ENV = Path.home() / '.codex-ppt-skill' / '.env'


def key_from_env():
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if key:
        return key
    if ENV.exists():
        for raw in ENV.read_text(encoding='utf-8').splitlines():
            if raw.startswith('OPENAI_API_KEY='):
                return raw.split('=', 1)[1].strip().strip('"').strip("'")
    raise RuntimeError('OPENAI_API_KEY is not configured')


def call(url, key, *, payload=None, timeout=60):
    headers = {'Authorization': 'Bearer ' + key, 'Accept': 'application/json'}
    if payload is not None:
        headers.update({'Content-Type': 'application/json'})
    req = urllib.request.Request(url, data=(json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload else None), method=('POST' if payload else 'GET'), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.headers.get('Content-Type', ''), resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')[:600]
        raise RuntimeError(f'Wokey HTTP {exc.code}: {detail}') from None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--timeout', type=int, default=900)
    args = parser.parse_args()
    job = json.loads(args.job.read_text(encoding='utf-8'))
    images = job.get('input_images') or []
    strict = [image for image in images if 'strict input asset' in image.get('role', '').lower() and 'not a strict input asset' not in image.get('role', '').lower()]
    if strict:
        raise RuntimeError('Strict source image input is required; text-only Wokey generation is not allowed for this slide')
    key = key_from_env()
    payload = {'model': 'gpt-image-2.5', 'prompt': job['prompt'], 'size': '1536x1024', 'n': 1}
    status, ctype, body = call(BASE + '/images/generations', key, payload=payload, timeout=240)
    if status == 200:
        import base64
        result = json.loads(body)
        data = result.get('data') or []
        if not data or not data[0].get('b64_json'):
            raise RuntimeError('Synchronous response has no data[0].b64_json')
        image = base64.b64decode(data[0]['b64_json'])
        job_id = None
    elif status == 202:
        result = json.loads(body)
        job_id = result.get('id')
        if not job_id:
            raise RuntimeError('Async response has no job id')
        print(f'Wokey job queued: {job_id}', flush=True)
        deadline = time.monotonic() + args.timeout
        while True:
            if time.monotonic() >= deadline:
                raise RuntimeError(f'Job {job_id} did not complete within {args.timeout}s')
            time.sleep(6)
            _, _, raw = call(BASE + '/images/jobs/' + job_id, key)
            state = json.loads(raw)
            current = state.get('status')
            print(f'Wokey job {job_id}: {current}', flush=True)
            if current == 'completed':
                if state.get('content_status') != 'available':
                    raise RuntimeError('Completed job has no available content')
                content_url = state.get('content_url') or ('/v1/images/jobs/' + job_id + '/content')
                if not content_url.startswith('/v1/images/jobs/'):
                    raise RuntimeError('Unexpected content URL')
                _, image_type, image = call('https://api.wokey.ai' + content_url, key)
                if 'image/png' not in image_type:
                    raise RuntimeError(f'Unexpected image content type: {image_type}')
                break
            if current in ('failed', 'cancelled', 'expired'):
                raise RuntimeError(f'Wokey job {job_id} ended with {current}: {state.get("error")}')
    else:
        raise RuntimeError(f'Unexpected Wokey status: {status}')
    if not image.startswith(b'\x89PNG\r\n\x1a\n'):
        raise RuntimeError('Backend did not return a PNG image')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise RuntimeError(f'Output already exists: {args.out}')
    args.out.write_bytes(image)
    print(json.dumps({'slide': job['slide'], 'job_id': job_id, 'out': str(args.out.resolve()), 'bytes': len(image)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()

"""Synthetic renderer contract; NOT a Llama or Qwen chat-template implementation.

No network, remote templates, image fetching or remote code execution.
Byte tokens make the roundtrip observable; real checkpoints need their tokenizer.
"""
from dataclasses import asdict, dataclass
import hashlib
import json

@dataclass(frozen=True)
class Identity:
    model: str
    tokenizer: str
    template: str
    processor: str
    tenant: str
    def __post_init__(self):
        if any(not isinstance(v,str) or not v for v in asdict(self).values()):
            raise ValueError('All identity fields require explicit nonempty strings')

def render(messages: list[dict], identity: Identity) -> dict:
    if not messages:
        raise ValueError('A conversation is required')
    parts = []
    for message in messages:
        role, content = message.get('role'), message.get('content')
        if role not in {'system','user','assistant','tool'} or not isinstance(content,str):
            raise ValueError('This lab accepts text-only, known-role messages')
        # Length-delimited UTF-8 body avoids delimiter injection ambiguities.
        body = content.encode('utf-8')
        parts.append(role.encode()+b':'+str(len(body)).encode()+b':'+body+b'\n')
    data = b''.join(parts)+b'assistant:'
    ids = list(data)
    record = {'identity':asdict(identity),'token_ids':ids,'max_new_tokens':8}
    return record

def accept(payload: dict, expected: Identity) -> list[int]:
    if payload.get('identity') != asdict(expected):
        raise ValueError('Renderer and generation worker identity mismatch')
    ids = payload.get('token_ids')
    if not isinstance(ids,list) or not ids or any(type(i) is not int or i<0 or i>255 for i in ids):
        raise ValueError('Invalid synthetic byte tokens')
    return ids

def prefix_key(payload: dict) -> str:
    packed = json.dumps({'identity':payload['identity'],'tokens':payload['token_ids']},
                        sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(packed).hexdigest()

if __name__ == '__main__':
    identity=Identity('model@revision','tok@revision','template-v1','text-v1','tenant-A')
    wire=json.dumps(render([{'role':'user','content':'What is KV cache?'}],identity))
    payload=json.loads(wire)
    print(json.dumps({'wire':payload,'roundtrip_token_count':len(accept(payload,identity)),
                      'cache_key':prefix_key(payload)},indent=2))

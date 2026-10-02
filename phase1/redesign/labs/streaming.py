"""SSE framing over arbitrarily split UTF-8 network bytes; no HTTP service."""
import codecs
import json
from collections.abc import Iterable

def events(chunks: Iterable[bytes]) -> list[str]:
    decoder=codecs.getincrementaldecoder('utf-8')('strict')
    pending=''; data=[]; out=[]
    def line(value):
        nonlocal data
        if not value:
            if data: out.append('\n'.join(data)); data=[]
        elif value.startswith('data:'):
            content=value[5:]
            data.append(content[1:] if content.startswith(' ') else content)
        # Ignore SSE comments/keep-alives and unrelated fields for this lab.
    for chunk in chunks:
        pending+=decoder.decode(chunk)
        while '\n' in pending:
            one,pending=pending.split('\n',1)
            line(one.removesuffix('\r'))
    pending+=decoder.decode(b'',final=True)
    if pending or data:
        raise ValueError('Incomplete SSE event at stream end')
    return out

if __name__=='__main__':
    payload=': keepalive\n\ndata: {"text":"你好"}\n\ndata: [DONE]\n\n'.encode()
    print(json.dumps(events([payload[i:i+1] for i in range(len(payload))]),ensure_ascii=False))

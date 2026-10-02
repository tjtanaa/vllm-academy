"""Separate content identity, readiness and lifetime. No distributed transport."""
from dataclasses import dataclass
import hashlib
import json

@dataclass
class Slot:
    state: str='loading'
    readers: int=0
    def ready(self):
        if self.state!='loading': raise RuntimeError('Invalid completion')
        self.state='ready'
    def acquire(self):
        if self.state!='ready': raise RuntimeError('Cannot read unpublished data')
        self.readers+=1
    def release(self):
        if self.readers<=0: raise RuntimeError('Reference underflow')
        self.readers-=1
    def recycle(self):
        if self.state!='ready' or self.readers: raise RuntimeError('Storage still in use')
        self.state='recycled'

def identity(stage: str, content: bytes, **options: str) -> str:
    if stage not in {'processor','encoder','kv'}:
        raise ValueError('Unknown cache layer')
    metadata=json.dumps({'stage':stage,**options},sort_keys=True).encode()
    # Length-prefix metadata; do not key by shape or image URL alone.
    return hashlib.sha256(len(metadata).to_bytes(8,'big')+metadata+content).hexdigest()

if __name__=='__main__':
    slot=Slot(); slot.ready(); slot.acquire()
    try: slot.recycle()
    except RuntimeError as error: print('Expected rejection:',error)
    slot.release(); slot.recycle()
    print('After last reader:',slot.state)

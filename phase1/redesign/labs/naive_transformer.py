"""A small decoder-only lab, not the original encoder-decoder Transformer.

Learned absolute positions, pre-LayerNorm, ordinary MHA and GELU deliberately
precede native RoPE/GQA/RMSNorm/SwiGLU model demos. Private contiguous KV only.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
import math
import torch
from torch import nn

@dataclass(frozen=True)
class Config:
    vocab: int = 32
    width: int = 24
    heads: int = 3
    layers: int = 2
    context: int = 64
    def __post_init__(self):
        if min(self.vocab, self.width, self.heads, self.layers, self.context) <= 0:
            raise ValueError('Dimensions must be positive')
        if self.width % self.heads:
            raise ValueError('This MHA lab needs width divisible by heads')

class Block(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.c = c
        self.n1, self.n2 = nn.LayerNorm(c.width), nn.LayerNorm(c.width)
        self.qkv = nn.Linear(c.width, 3*c.width, bias=False)
        self.out = nn.Linear(c.width, c.width, bias=False)
        self.mlp = nn.Sequential(nn.Linear(c.width, 4*c.width), nn.GELU(),
                                 nn.Linear(4*c.width, c.width))

    def forward(self, x, past=None):
        b, t, d = x.shape
        q, k, v = self.qkv(self.n1(x)).chunk(3, dim=-1)
        q, k, v = [a.reshape(b,t,self.c.heads,d//self.c.heads).transpose(1,2)
                   for a in (q,k,v)]
        offset = 0 if past is None else past[0].shape[2]
        if past is not None:
            k, v = torch.cat((past[0],k),dim=2), torch.cat((past[1],v),dim=2)
        scores = (q @ k.transpose(-1,-2)) / math.sqrt(d//self.c.heads)
        # Query i is at absolute position offset+i. A top-left triangular
        # t-by-(offset+t) mask would be WRONG for cached chunks.
        key_pos = torch.arange(k.shape[2], device=x.device)
        query_pos = offset + torch.arange(t, device=x.device)
        mask = key_pos[None,:] > query_pos[:,None]
        scores = scores.masked_fill(mask, float('-inf'))
        weights = scores.softmax(dim=-1)
        a = (weights @ v).transpose(1,2).contiguous().reshape(b,t,d)
        x = x + self.out(a)
        return x + self.mlp(self.n2(x)), (k,v), {
            'q': list(q.shape), 'k': list(k.shape),
            'attention_scores': list(scores.shape), 'offset': offset}

class NaiveDecoder(nn.Module):
    def __init__(self, config: Config = Config()):
        super().__init__()
        self.config = config
        self.token = nn.Embedding(config.vocab, config.width)
        self.position = nn.Embedding(config.context, config.width)
        self.blocks = nn.ModuleList([Block(config) for _ in range(config.layers)])
        self.norm = nn.LayerNorm(config.width)
        self.head = nn.Linear(config.width, config.vocab, bias=False)

    def forward(self, ids: torch.Tensor, past=None):
        c = self.config
        if ids.ndim != 2 or ids.shape[1] == 0 or ids.dtype != torch.long:
            raise ValueError('Expected nonempty [batch,tokens] int64 IDs')
        if bool(((ids < 0) | (ids >= c.vocab)).any()):
            raise ValueError('Token ID outside vocabulary')
        if past is not None:
            if len(past) != c.layers:
                raise ValueError('One KV pair per layer required')
            lengths = set()
            for k,v in past:
                if k.shape != v.shape or k.ndim != 4:
                    raise ValueError('KV pair shape mismatch')
                if (k.shape[0],k.shape[1],k.shape[3]) != (ids.shape[0],c.heads,c.width//c.heads):
                    raise ValueError('Invalid cache batch/head shape')
                if k.device != ids.device or v.device != ids.device:
                    raise ValueError('Cache must be on input device')
                lengths.add(k.shape[2])
            if len(lengths) != 1:
                raise ValueError('All layer cache lengths must agree')
            offset = next(iter(lengths))
        else:
            offset = 0
        if offset + ids.shape[1] > c.context:
            raise ValueError('Context limit exceeded')
        positions = torch.arange(offset,offset+ids.shape[1],device=ids.device)
        x = self.token(ids) + self.position(positions)
        trace = {'ids':list(ids.shape),'embedding':list(x.shape),'layers':[]}
        updated = []
        for index, block in enumerate(self.blocks):
            x, kv, row = block(x, None if past is None else past[index])
            updated.append(kv); trace['layers'].append(row)
        logits = self.head(self.norm(x))
        trace['logits'] = list(logits.shape)
        return logits, updated, trace

    @torch.inference_mode()
    def generate(self, prompt: torch.Tensor, count: int, cached: bool = True):
        if count <= 0 or prompt.ndim != 2 or prompt.shape[1]+count > self.config.context:
            raise ValueError('Invalid generation budget')
        ids, past, sampled = prompt.clone(), None, []
        for _ in range(count):
            model_ids = ids if past is None or not cached else ids[:,-1:]
            logits, new_past, _ = self(model_ids, past if cached else None)
            next_id = logits[:,-1].argmax(-1,keepdim=True)
            sampled.append(next_id)
            ids = torch.cat((ids,next_id),dim=1)
            past = new_past if cached else None
        return torch.cat(sampled,dim=1)

def demo():
    torch.manual_seed(5)
    model = NaiveDecoder().eval()
    ids = torch.tensor([[1,2,3,4,5,6]],dtype=torch.long)
    with torch.inference_mode():
        dense, _, trace = model(ids)
        _, cache, _ = model(ids[:,:4])
        tail, cache, cached_trace = model(ids[:,4:],cache)
        error = float((tail-dense[:,4:]).abs().max())
        torch.testing.assert_close(tail,dense[:,4:],atol=2e-6,rtol=2e-5)
        assert torch.equal(model.generate(ids,4),model.generate(ids,4,cached=False))
    return {'dense':trace,'cached_tail':cached_trace,
            'max_absolute_error':error,'generated_ids':model.generate(ids,4).tolist(),
            'scope':'random weights; correctness illustration, not a language-quality demo'}

if __name__ == '__main__':
    print(json.dumps(demo(),indent=2))

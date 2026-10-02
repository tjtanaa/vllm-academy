"""Small random-weight decoder: dense reference and incremental cached execution.

Not Qwen/Llama-compatible. Uses learned positional embeddings, ordinary MHA,
LayerNorm and GELU. No tokenizer, training, RoPE, GQA or optimized attention.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import torch
from torch import nn
from .cache import PagedKV


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int = 64
    hidden_size: int = 32
    num_heads: int = 4
    num_layers: int = 2
    max_length: int = 128

    def __post_init__(self):
        if min(self.vocab_size, self.hidden_size, self.num_heads, self.num_layers, self.max_length) <= 0:
            raise ValueError("All model dimensions must be positive")
        if self.hidden_size % self.num_heads:
            raise ValueError("hidden_size must be divisible by num_heads")

    @property
    def head_dim(self) -> int:
        return self.hidden_size // self.num_heads


class DecoderLayer(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        d = config.hidden_size
        self.norm1, self.norm2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.out = nn.Linear(d, d, bias=False)
        self.ffn = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))

    def dense(self, x: torch.Tensor) -> torch.Tensor:
        n, c = x.shape
        q, k, v = self.qkv(self.norm1(x)).chunk(3, dim=-1)
        q, k, v = [a.reshape(n, self.config.num_heads, self.config.head_dim).transpose(0, 1) for a in (q, k, v)]
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.config.head_dim)
        mask = torch.ones(n, n, dtype=torch.bool, device=x.device).triu(1)
        scores = scores.masked_fill(mask, float("-inf"))
        attended = (scores.softmax(-1) @ v).transpose(0, 1).reshape(n, c)
        x = x + self.out(attended)
        return x + self.ffn(self.norm2(x))

    def step(self, x: torch.Tensor, cache: PagedKV, layer: int) -> torch.Tensor:
        q, k, v = self.qkv(self.norm1(x)).chunk(3, dim=-1)
        h, d = self.config.num_heads, self.config.head_dim
        q, k, v = [a.reshape(h, d) for a in (q, k, v)]
        cache.write_layer(layer, k, v)
        all_k, all_v = cache.read_layer(layer, include_pending=True)
        scores = torch.einsum("hd,thd->ht", q, all_k) / math.sqrt(d)
        attended = torch.einsum("ht,thd->hd", scores.softmax(-1), all_v).flatten()
        x = x + self.out(attended)
        return x + self.ffn(self.norm2(x))


class TinyDecoder(nn.Module):
    def __init__(self, config: ModelConfig = ModelConfig(), seed: int = 7):
        super().__init__()
        self.config = config
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            self.token_embedding = nn.Embedding(config.vocab_size, config.hidden_size)
            self.position_embedding = nn.Embedding(config.max_length, config.hidden_size)
            self.layers = nn.ModuleList([DecoderLayer(config) for _ in range(config.num_layers)])
            self.norm = nn.LayerNorm(config.hidden_size)
            self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.eval()

    @property
    def device(self) -> torch.device:
        return self.token_embedding.weight.device

    def _validate(self, tokens: list[int], offset: int = 0) -> None:
        if not tokens or offset < 0 or offset + len(tokens) > self.config.max_length:
            raise ValueError("Empty sequence or context length exceeded")
        if any(type(t) is not int or not 0 <= t < self.config.vocab_size for t in tokens):
            raise ValueError("Token IDs must be integers within the vocabulary")

    @torch.inference_mode()
    def forward(self, tokens: list[int]) -> torch.Tensor:
        self._validate(tokens)
        ids = torch.tensor(tokens, device=self.device)
        pos = torch.arange(len(tokens), device=self.device)
        x = self.token_embedding(ids) + self.position_embedding(pos)
        for layer in self.layers:
            x = layer.dense(x)
        return self.lm_head(self.norm(x))

    @torch.inference_mode()
    def cached(self, tokens: list[int], cache: PagedKV) -> torch.Tensor:
        self._validate(tokens, cache.length)
        if cache.pool.k.device != self.device:
            raise ValueError("Model and KV pool must be on the same device")
        logits = []
        # Deliberately token-by-token, including prefill; not a fast prefill path.
        for token in tokens:
            pos = cache.length
            cache.reserve_token()
            x = self.token_embedding(torch.tensor(token, device=self.device))
            x = x + self.position_embedding(torch.tensor(pos, device=self.device))
            for index, layer in enumerate(self.layers):
                x = layer.step(x, cache, index)
            cache.commit_token()
            logits.append(self.lm_head(self.norm(x)))
        return torch.stack(logits)

    @torch.inference_mode()
    def generate_dense(self, prompt: list[int], max_new_tokens: int) -> list[int]:
        if max_new_tokens <= 0:
            raise ValueError("max_new_tokens must be positive")
        tokens = list(prompt)
        self._validate(tokens)
        if len(tokens) + max_new_tokens > self.config.max_length:
            raise ValueError("Context length exceeded")
        for _ in range(max_new_tokens):
            tokens.append(int(self(tokens)[-1].argmax()))
        return tokens[len(prompt):]

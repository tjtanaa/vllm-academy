"""KV-cache and memory budgeting (episode E07). Pure Python.

Presets come from public Hugging Face config.json files. Always double-check
your own checkpoint: layers, num_key_value_heads and head_dim are what matter.
"""
from __future__ import annotations

from dataclasses import dataclass

GIB = 1024 ** 3


@dataclass(frozen=True)
class ModelSpec:
    name: str
    layers: int
    kv_heads: int = 0
    head_dim: int = 0
    params_b: float = 0.0
    attention: str = "gqa"  # gqa | mha | mla
    kv_lora_rank: int = 0  # MLA only
    rope_dim: int = 0  # MLA only
    query_heads: int = 0

    def kv_bytes_per_token(self, dtype_bytes: float) -> float:
        if self.attention == "mla":
            # One compressed latent + decoupled RoPE key per layer, no separate K and V.
            return self.layers * (self.kv_lora_rank + self.rope_dim) * dtype_bytes
        return 2 * self.layers * self.kv_heads * self.head_dim * dtype_bytes

    def formula(self, dtype_bytes: float) -> str:
        if self.attention == "mla":
            return f"{self.layers} layers × ({self.kv_lora_rank} + {self.rope_dim}) × {dtype_bytes:g} B"
        return f"2 × {self.layers} layers × {self.kv_heads} KV heads × {self.head_dim} head_dim × {dtype_bytes:g} B"


MODELS: dict[str, ModelSpec] = {m.name: m for m in [
    ModelSpec("qwen3-0.6b", layers=28, kv_heads=8, head_dim=128, params_b=0.6, query_heads=16),
    ModelSpec("llama-3.2-1b", layers=16, kv_heads=8, head_dim=64, params_b=1.24, query_heads=32),
    ModelSpec("llama-2-7b", layers=32, kv_heads=32, head_dim=128, params_b=6.74, attention="mha", query_heads=32),
    ModelSpec("mistral-7b", layers=32, kv_heads=8, head_dim=128, params_b=7.24, query_heads=32),
    ModelSpec("llama-3.1-8b", layers=32, kv_heads=8, head_dim=128, params_b=8.03, query_heads=32),
    ModelSpec("qwen3-8b", layers=36, kv_heads=8, head_dim=128, params_b=8.19, query_heads=32),
    ModelSpec("qwen3-30b-a3b", layers=48, kv_heads=4, head_dim=128, params_b=30.5, query_heads=32),
    ModelSpec("qwen3-32b", layers=64, kv_heads=8, head_dim=128, params_b=32.8, query_heads=64),
    ModelSpec("llama-3.1-70b", layers=80, kv_heads=8, head_dim=128, params_b=70.6, query_heads=64),
    ModelSpec("qwen3-235b-a22b", layers=94, kv_heads=4, head_dim=128, params_b=235.0, query_heads=64),
    ModelSpec("llama-3.1-405b", layers=126, kv_heads=8, head_dim=128, params_b=405.0, query_heads=128),
    ModelSpec("deepseek-v3", layers=61, params_b=671.0, attention="mla", kv_lora_rank=512, rope_dim=64, query_heads=128),
]}

# Usable device memory in GiB (approximate, as reported by the driver).
GPUS: dict[str, float] = {
    "T4-16G (Colab)": 15.0,
    "RTX-4090-24G": 24.0,
    "L4-24G": 22.5,
    "RTX-5090-32G": 32.0,
    "L40S-48G": 45.0,
    "A100-40G": 40.0,
    "A100-80G": 80.0,
    "H100-80G": 79.6,
    "H200-141G": 140.4,
    "B200-180G": 178.0,
    "MI300X-192G": 192.0,
    "MI325X-256G": 256.0,
    "MI355X-288G": 288.0,
}

DTYPES: dict[str, float] = {"bf16": 2.0, "fp16": 2.0, "fp8": 1.0, "int8": 1.0, "fp4": 0.5, "int4": 0.5}


@dataclass
class KVResult:
    model: ModelSpec
    context: int
    users: int
    kv_dtype: str
    weight_dtype: str
    gpus: int
    gpu_mem_gib: float
    util: float
    kv_per_token: float
    kv_per_seq: float
    kv_total: float
    weights: float
    budget: float
    kv_room: float
    max_seqs: int

    @property
    def weights_fit(self) -> bool:
        return self.kv_room > 0

    @property
    def fits(self) -> bool:
        return self.weights_fit and self.kv_total <= self.kv_room

    @property
    def formula(self) -> str:
        return self.model.formula(DTYPES[self.kv_dtype])


def compute(model: ModelSpec, *, context: int, users: int = 1, kv_dtype: str = "bf16",
            weight_dtype: str = "bf16", gpus: int = 1, gpu_mem_gib: float = 80.0,
            util: float = 0.92) -> KVResult:
    if context <= 0 or users <= 0 or gpus <= 0 or gpu_mem_gib <= 0:
        raise ValueError("context, users, gpus and gpu memory must be positive")
    if not 0 < util <= 1:
        raise ValueError("util must be in (0, 1]")
    if kv_dtype not in DTYPES or weight_dtype not in DTYPES:
        raise ValueError(f"dtype must be one of {sorted(DTYPES)}")
    per_token = model.kv_bytes_per_token(DTYPES[kv_dtype])
    per_seq = per_token * context
    weights = model.params_b * 1e9 * DTYPES[weight_dtype]
    budget = gpus * gpu_mem_gib * GIB * util
    kv_room = budget - weights
    max_seqs = int(kv_room // per_seq) if kv_room > 0 and per_seq > 0 else 0
    return KVResult(model=model, context=context, users=users, kv_dtype=kv_dtype, weight_dtype=weight_dtype,
                    gpus=gpus, gpu_mem_gib=gpu_mem_gib, util=util, kv_per_token=per_token, kv_per_seq=per_seq,
                    kv_total=per_seq * users, weights=weights, budget=budget, kv_room=kv_room, max_seqs=max_seqs)


def human_bytes(n: float) -> str:
    n = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(n) < 1024 or unit == "TiB":
            if unit == "B":
                return f"{n:.0f} {unit}"
            return f"{n:.1f} {unit}" if abs(n) < 100 else f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TiB"


def find_model(name: str) -> ModelSpec | None:
    key = name.strip().lower().replace(" ", "-").replace("_", "-")
    if key in MODELS:
        return MODELS[key]
    matches = [m for k, m in MODELS.items() if key in k]
    return matches[0] if len(matches) == 1 else None


def find_gpu(name: str) -> tuple[str, float] | None:
    key = name.strip().lower()
    for k, v in GPUS.items():
        if k.lower() == key or k.lower().startswith(key):
            return k, v
    return None

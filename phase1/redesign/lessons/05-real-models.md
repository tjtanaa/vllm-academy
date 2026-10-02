# 05 — From naive code to real Llama and Qwen demos

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

The naive decoder is a microscope, not the final demo. Phase 1 must reach understandable real text generation through mini-vLLM itself. Its required checkpoints remain `meta-llama/Llama-3.2-1B` and `Qwen/Qwen3-0.6B`.

## Explain the architecture changes before loading weights

Compare learned positions with RoPE, ordinary MHA with GQA, LayerNorm with RMSNorm, and the toy feed-forward network with a gated FFN. These are executable differences, not interchangeable labels. Weight names, tensor shapes, normalization details, rotary parameters and tied embeddings all matter. [R15–R18](../REFERENCES.md)

For the inspected Qwen3 configuration, `hidden_size=1024`, query heads are 16, KV heads are 8, and `head_dim=128`. Calculate Q's projected width: 2048. The naive assumption `1024/16=64` would break checkpoint compatibility. Use the actual local config, not the model name as a substitute. [R13](../REFERENCES.md)

The two required checkpoints are text models. An optional vision lab does not add a trained vision encoder to their checkpoints. A base Llama completion also should not be graded against an instruction-tuned assistant prompt without accounting for that objective difference. [R12–R14](../REFERENCES.md)

## Hands-on sequence

First audit configuration without loading weights:

```bash
python -m labs.inspect_snapshot /path/to/approved/snapshot
```

Next inspect native implementation modules in the separately prepared pretrained patch. Ask where positions rotate Q/K, where KV heads differ from query heads, and how the final vocabulary weights are loaded. Model loading must reject missing/unexpected tensors rather than accidentally leave random parameters in a claimed pretrained demo.

Finally, after that patch is integrated and reviewed, run the actual native model commands from the Academy checkout, not this standalone supplement:

```bash
python -m mini_vllm.generate --model meta-llama/Llama-3.2-1B \
  --mode completion --device cpu \
  --prompt "The purpose of an inference engine is" --max-new-tokens 32
python -m mini_vllm.generate --model Qwen/Qwen3-0.6B \
  --device cpu --prompt "Explain KV caching in two sentences." --max-new-tokens 64
```

These are **integration-gate commands from the prepared patch**, not commands executed or provided as an implementation by this supplement. Authorized model access and dependencies are prerequisites. Thinking-mode and tokenizer settings must be explicit in Qwen evidence.

## Correctness before attractive prose

Compare native logits against an independent reference under teacher forcing, then compare incremental execution and prefix reuse. Record dtype-appropriate tolerances. Greedy text agreement alone does not prove all positions are correct, and a small numerical difference near tied logits can change a later sequence.

## Exercise and exit ticket

Submit a checkpoint compatibility ledger and the two full-model records defined in [model acceptance](../MODEL_ACCEPTANCE.md). Missing checkpoint access means this gate remains pending; it does not erase other learning progress or justify substituting a toy result.

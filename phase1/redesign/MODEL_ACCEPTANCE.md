# Mandatory model demonstrations and honest completion gates

## Exact text checkpoints

The required pair is **`meta-llama/Llama-3.2-1B`** (base checkpoint; completion demo) and **`Qwen/Qwen3-0.6B`** (chat demo, explicitly configured thinking mode). Llama-3.2-1B-Instruct is an optional additional demo, not a substitute for the base model. Neither required checkpoint is the course's vision model. [R12–R14](REFERENCES.md)

The naive model's learned positions, MHA, LayerNorm and GELU cannot load those weights correctly merely by changing dimension constants. Learners must explain architecture, state-dict names/shapes, tokenizer, dtype, positions and stopping behavior before claiming support.

## Important configuration exercise

The inspected Qwen3-0.6B configuration has `hidden_size=1024`, `num_attention_heads=16`, `num_key_value_heads=8` and an explicit `head_dim=128`. Thus the query projection width is `16×128=2048`; dividing hidden size by query-head count would incorrectly yield 64. That is a configuration observation at inspection time, not a permanent claim about any model named Qwen. Record the snapshot revision and read its actual file. [R13](REFERENCES.md)

The Llama config was not fetched in this session because access is gated. Do not fill its values from guesses. Authorized learners inspect the local approved snapshot and record the resolved revision. Do not put access tokens or model weights in the course repository.

## Evidence matrix

| Gate | What must be shown | Current supplement status |
|---|---|---|
| Mechanism code | Causal tests, cached-chunk equivalence and deterministic greedy agreement | Executed on the standalone tiny CPU lab. |
| Native model integration | Mini-vLLM forward/scheduler/cache, not `Transformers.generate()` as the demo engine | Prior 0.2.0 patch prepared separately; not published/integrated by this supplement. |
| Llama full checkpoint | Strict loading, completion, stopping, numerical reference and cache behavior | Not executed here. |
| Qwen full checkpoint | Strict loading, rendered chat, mode choice, stopping, numerical reference and cache behavior | Not executed here. |
| Real tokenizer | Exact model snapshot/template and no duplicate special tokens | Local inspection exercise supplied; full-tokenizer lab not executed here. |
| CUDA/ROCm | Actual numerical and lifecycle tests on recorded stack | Not executed here. |
| Vision understanding | An appropriate trained VLM and full preprocessing contract | Not claimed; vision lab is random-weight tensor mechanics only. |

## Required submission for each checkpoint

Record model/tokenizer revision, source commit, prompt or sanitized token IDs, chat-template/options when applicable, generation parameters, dtype, backend, device, output, finish reason and exact commands. Use teacher-forced logit comparisons over selected positions, then cached versus uncached comparisons and cold versus warm reuse. Greedy IDs alone can hide a numerical discrepancy; near-tied logits can also change an argmax without a large error. Pick tolerances deliberately for dtype and backend.

Test early EOS, maximum length, cancellation and invalid input. Record whether output token IDs include termination tokens and how text is decoded. A base model's unconstrained completion should not be graded as though it were an instruction-tuned assistant.

## Running the local configuration audit

From the supplement directory:

```bash
python -m labs.inspect_snapshot /path/to/approved/model-snapshot
# Optional, with Transformers installed and tokenizer files available locally:
python -m labs.inspect_snapshot /path/to/approved/model-snapshot --tokenize
```

The command never downloads weights and does not execute repository-supplied remote code. The tokenizer mode is an optional exercise, not a claim that dependencies are already installed. Inspect the supplied snapshot and provenance before using external artifacts.

## Relationship to the pretrained patch

The earlier `vllm-academy-pretrained-patch.zip` remains a separate implementation proposal. Its tests and historical validation are not the test results of this supplement. Integrate and review it separately; then attach full-model execution evidence before marking this gate complete. The present package deliberately avoids publishing claims that its 44 small CPU tests validate billion-parameter checkpoints.

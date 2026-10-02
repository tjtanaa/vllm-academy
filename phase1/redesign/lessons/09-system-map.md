# 09 — Open the complete inference-engine map

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

The learner has now built a model, a cache and a small scheduler. Return to the five boxes from lesson 00 and expand them into production responsibilities. This is the moment for the full atlas—not the first day.

## Follow the data, then name the component

Start with role-based messages. An API router validates the transport-level request and delegates to a serving adapter. Rendering resolves model input representation; multimodal processing may produce tensors and placeholder metadata. Engine input processing validates task/configuration constraints. The core and scheduler organize iterative work. Execution reaches workers, a selected runner and model-specific layers. Output processing returns tokens or other task results to an API response path. [R25–R30](../REFERENCES.md)

This is a logical map. Exact call order and deployment vary with offline/online entrypoint, task, renderer separation and runner selection. The lesson must not turn that overview into an unsupported universal call graph.

## Build a request ledger

For every boundary, record four fields: **object passed**, **owner**, **readiness condition**, **failure/cancellation action**. Add placement and expected cost only after those fields make sense.

Examples: renderer outputs are not merely strings; an execution plan is not a batch of raw JSON; a model's hidden states are not a final API response; sampled tokens are not necessarily printable characters yet. Memory allocated for state can exist before the state is ready to consume.

The model runner is also not the neural model. The inspected runner file explicitly aims to keep shared execution logic model-agnostic and model-specific behavior elsewhere. Model Runner V2 is an internal runner design, not evidence that the project or engine is called “vLLM V2.” [R30; source map](../SOURCE_MAP.md)

## Read only what answers a question

```bash
python -m labs.source_walk --checkout /path/to/pinned-vllm --entry api
python -m labs.source_walk --checkout /path/to/pinned-vllm --entry input
python -m labs.source_walk --checkout /path/to/pinned-vllm --entry runner
```

Read one at a time. For `api`, ask what is delegated and how output is framed. For `input`, ask which task parameters are accepted. For `runner`, ask which helpers carry shared versus model-specific responsibilities. The tool rejects a different checkout commit rather than printing confidently mislabeled line numbers.

Source entries marked “symbol search located” need further inspection before asserting detailed behavior. File existence does not prove runtime selection.

## Exercise and exit ticket

Take one completion request and one embedding request. Mark where their paths share responsibilities and where a sampling-versus-pooling distinction matters. Then explain why the renderer's CPU executor and the model executor share a word but not a responsibility.

Submit a completed request ledger with one error path and one abort path. The [atlas](../ARCHITECTURE_ATLAS.md) is a reference, not the answer to copy unchanged.

# Instructor guide and answer checkpoints

## Teach the invariant before the optimization

Ask the learner to predict an observable difference before running a cell. Ask them to explain a failure before showing the fix. Keep the actual source excerpt small enough to discuss in a few minutes. “Read scheduler.py” is not an assignment; “find the state that distinguishes allocated space from work already computed” is.

The course's 90-minute cycle is a planning proposal. Record actual stumbling points during the pilot: vocabulary, tensor shape, Python mechanics, checkpoint access, unclear ownership or source-navigation difficulty. Adjust the lesson rather than assuming all delays are lack of effort.

## Answer checkpoints

| Lesson | A satisfactory explanation | Misconception to catch |
|---|---|---|
| 00 | Model maps representations to outputs; engine and API organize the service. | A successful HTTP response proves numerical correctness. |
| 01 | Architectural advances address different limitations; objectives branch. | Every new model is just a larger version of its predecessor. |
| 02 | Messages are serialized using a model-specific contract before tokenization/processing. | The neural model directly reads Python message dictionaries. |
| 03 | Future-token mutations cannot change earlier causal logits. | Applying any triangular matrix yields correct cached attention. |
| 04 | Training targets are shifted; inference appends a newly selected token. | Teacher forcing and free-running generation are the same computation. |
| 05 | Qwen's explicit head_dim must be honored; native architectures differ from the toy. | Hidden width divided by head count is always the attention head width. |
| 06 | Newly sampled token state is not present until that token is executed. | Sampling a token automatically writes its KV. |
| 07 | A logical iteration may select multiple requests without physically batching their forwards. | An async API or a queue automatically gives continuous GPU batching. |
| 08 | Cached identity, live references and physical reuse are separate. | Request completion permits every related page to be overwritten immediately. |
| 09 | Renderer, worker executor and runner each have different contracts. | Every class or figure box is a separate process. |
| 10 | Protocol capability depends on selected model/task; events differ from network chunks. | Every framework endpoint works with the two text checkpoints. |
| 11 | Renderer scaling distributes requests; matches the downstream model contract. | A chat template is tensor-parallelized over GPUs. |
| 12 | Preprocessing produces ordered tensors and metadata; feature counts affect placeholders. | An image is exactly one ordinary text token. |
| 13 | A learned vision encoder/projector makes compatible features; a trained VLM adds learned semantics. | Random-weight shape correctness demonstrates image understanding. |
| 14 | Same image may reuse an encoder result, while different prior text changes contextual decoder KV. | All caches can use only the image hash. |
| 15 | R/E/P/D and TP/PP/DP/EP describe different placement axes. | Encoder output is interchangeable with decoder KV. |
| 16 | End-to-end delay has multiple owners; benchmark definitions and workload must be explicit. | A faster attention kernel guarantees better TTFT. |
| 17 | A bounded reproduction and test can be useful without a large patch. | A merged upstream PR is a requirement the course can guarantee. |

## Suggested fault-injection exercises

Remove the causal mask and watch the future-invariance test fail. Replace the cached-chunk offset mask with a top-left triangle and watch cached/dense comparisons fail. Change the renderer identity during JSON roundtrip. Supply one fewer image placeholder than features. Recycle a ready slot before the final reader releases it. Cut an SSE stream in the middle of a UTF-8 character. Each failure should be explained at the correct abstraction boundary.

Use only synthetic or appropriately sanitized inputs in public exercises. No activity needs private user prompts, credentials, remote template execution or a publicly exposed endpoint.

## Capstone rubric

Use a proposed 100-point rubric: computation and numerical evidence 25; request/component/data-contract understanding 25; state/lifetime correctness 20; experimental reasoning 15; communication and review quality 15. Require the two actual model-demo gates separately. Do not let a high score on prose compensate for an unexecuted model claim or memory ownership error.

A useful capstone package includes: one reproducible issue, a minimal failing test, a narrow change or evidence-based issue report, one before/after behavior explanation, exact source/model revisions, and limitations. Benchmark improvements require measured evidence, not just an architectural argument.

## Example oral examination

“An image chat request has a prefix hit. Why might TTFT still be high?” A strong answer asks **which cache hit**, then considers media preprocessing, encoder work, KV readiness, scheduling, graph warmup, queueing and output boundaries. It does not immediately prescribe a faster attention backend.

“Two renderer replicas produce different prompt IDs for identical messages. Where do you look?” Check model/tokenizer/template revisions, options, history resolution, truncation and processor behavior before touching the GPU kernel.

“A cold run and a warm run generate different text. Is prefix caching wrong?” First control sampling and rendered inputs, compare teacher-forced logits and cache metadata, and examine numerical tolerances. An uncontrolled text comparison cannot isolate the cause.

## Instructor validation record

The supplied CPU labs were run in this session; exact results are recorded separately. Real-checkpoint, GPU, multimodal semantic-quality, full production call-trace and learner-pilot validation remain open. Review the evidence file before quoting counts, versions or execution claims.

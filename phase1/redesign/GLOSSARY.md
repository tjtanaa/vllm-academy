# A small vocabulary for the whole course

| Term | Working meaning in these lessons |
|---|---|
| Tokenizer | Converts text to/from a model's token representation; not a language-model forward pass. |
| Chat template | Serialization rules for messages, control markers and generation boundaries. |
| Renderer | Constructs model input from a protocol-level request; can include tokenization and modality processing. |
| Derenderer | Converts generated tokens/task results into the expected response representation. |
| Processor | Model-specific input preparation; a multimodal processor also maintains item/placeholder correspondence. |
| Vision tower | A trained image-encoding neural component, distinct from resizing or decoding media. |
| Patch | A spatial portion of an image used to construct a sequence element in the chosen ViT example. |
| Projector / merger | Learned representation transformation or feature aggregation connecting model components. |
| Transfer connector | Interface coordinating data movement and its metadata/lifetime; not a neural projector. |
| Embedding | A vector representation; token embeddings, image features and API embedding outputs serve different roles. |
| Hidden state | An intermediate neural representation, not necessarily a response or reusable KV block. |
| Logits | Unnormalized output scores; vocabulary logits support next-token selection. |
| Prefill | Computation on known input history, possibly chunked. |
| Decode | Advancing generated history; not the same as text detokenization. |
| Computed token | A position whose required model execution has completed under the stated accounting convention. |
| Sampled token | A newly selected output ID; its own KV has not necessarily been computed yet. |
| KV cache | Stored attention keys and values for compatible previously computed positions. |
| Prefix cache | Reuse of compatible state from an already computed context prefix. |
| Block table | Logical-to-physical mapping for a request's paged state. |
| Readiness | Whether a consumer may use a result, independent of knowing its identity. |
| Ownership | Who must retain storage while it can still be read or written. |
| Scheduler | Chooses work under progress, availability and capacity constraints. |
| Engine core | Coordinates the iterative engine workflow. |
| Worker | Executes work for a configured device/rank or backend role. |
| Model executor | Dispatches model execution; different from a renderer's CPU task executor. |
| Model runner | Builds/executes per-step model inputs and handles shared execution state and helpers. |
| Continuous batching | Reconsidering request work across iterations rather than waiting for an entire fixed group to finish. |
| Tensor parallelism | Dividing tensor-level model work among participating workers. |
| Pipeline parallelism | Assigning model stages to different workers/stages. |
| Data parallelism | Replicating execution capacity and distributing requests/work. |
| Expert parallelism | Distributing expert components for applicable expert models. |
| Disaggregation | Placing formerly coupled responsibilities in separately scheduled/deployed components. |
| SSE | Server-Sent Events framing; events do not coincide necessarily with tokens or network reads. |
| TTFT | Time to first token at explicitly chosen request and observation boundaries. |
| ITL | Inter-token latency under a specified observation convention. |

These definitions are intentionally operational and introductory. The concrete APIs, representation types and concurrency semantics must be checked in the pinned implementation. Related primary reading: [R03, R11, R15, R19, R22–R30](REFERENCES.md).

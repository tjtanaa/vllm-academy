# 15 — Put the boundaries on machines

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

Only distribute a boundary after its local contract is understood. A network hop adds serialization, transfer, latency, failure and ownership questions; it does not make those concerns disappear behind an acronym.

## Separate placement from model parallelism

Use R for request rendering, E for vision/other encoder work, P for language-model prefill, and D for decode. A deployment can co-locate these responsibilities, split R from combined inference, separate E from P/D, or additionally separate P from D. Not every model or connector supports every combination. [R25, R27, R29](../REFERENCES.md)

TP partitions tensor operations across participating workers. PP partitions stages of a model. DP replicates work-serving capacity. EP places experts across workers for applicable expert models. These are different axes from deciding whether rendering or encoder work is a separate service.

The course teaches the contracts and cost hypotheses in Phase 1. Implementing distributed collectives or optimized transfer kernels is not required to understand the map.

## Label the transferred object

For remote rendering, retain model-consistent IDs, parameters and any required multimodal payload/metadata. For E→P separation, encoder features and corresponding positional/item information matter. For P→D separation, decoder KV representation and transfer state matter. Returning output may send token IDs to a derenderer or formatted data to the client.

Never write only “cache” on an arrow. A vision embedding and a decoder KV block have different shapes, semantics and consumers. A transport connector and a learned projection layer are also different abstractions.

## Hands-on design lab

Use figure 04 and create three versions on paper: co-located, R-separated, and R/E/P/D-separated. For every boundary, fill in source owner, destination owner, readiness signal, compatibility identity and failure behavior.

Replay `labs.render_contract` and `labs.cache_lifecycle` as local stand-ins for information preservation and lifetime requirements. These two tests do not validate throughput, RDMA behavior, GPU graph safety or any distributed deployment.

## Predict trade-offs

Separating CPU preprocessing may help when it constrains request admission, but it adds transport. Moving processed images can transmit more bytes than compressed input. Separating E can change encoder utilization and cache reuse. P/D separation can isolate unlike work but adds state-transfer costs. These are hypotheses to test, not universal speedup promises.

## Source detour and exit ticket

Read the pinned renderer document and encoder-disaggregation guide for the selected version. Check enablement and payload requirements before copying example commands. Keep a local-only or isolated lab deployment; production exposure needs separate security review.

Submit one placement decision with a reason it could help and a reason it could hurt. Explicitly state the model, workload and available transport assumptions needed to evaluate it.

# Curriculum

**Core:** chapters 00–11. **Electives/workshops:** chapters 12–17. Learning durations below are planning estimates, not task execution promises. The 12 core lessons are authored drafts awaiting human instructional review; the six electives are workshop briefs, not implemented toy features.

| Chapter | Part | Topic | Hardware | Learner artifact | Suggested effort |
|---|---|---|---|---|---|
| [00](course/part0/00-orientation.md) | 0 | Evidence, reproducibility and course scope | CPU | Learning contract and first trace | 60–90 min |
| [01](course/part0/01-first-server.md) | 0 | Platform setup and first server | CUDA or ROCm; reading-only alternative | Environment record and smoke output | 90–150 min |
| [02](course/part1/02-inference.md) | 1 | Autoregression, prefill and decode | CPU | Token/computed-state trace | 60–90 min |
| [03](course/part1/03-hardware.md) | 1 | Compute, bandwidth and timing | No GPU required | Bottleneck hypothesis and measurement plan | 60–90 min |
| [04](course/part1/04-kv-memory.md) | 1 | KV memory and address translation | CPU | Memory estimate and ownership diagram | 60–90 min |
| [05](course/part1/05-measurement.md) | 1 | Metrics and experiment design | CPU plan; GPU measurements optional | Reproducible benchmark protocol | 90–120 min |
| [06](course/part2/06-tiny-decoder.md) | 2 | Dense and incremental decoder | CPU | Logit-equivalence tests | 120–180 min |
| [07](course/part2/07-paged-kv.md) | 2 | Noncontiguous pages and safe lifetime | CPU | Allocator and lifetime tests | 120–180 min |
| [08](course/part2/08-scheduling.md) | 2 | Chunked prefill and logical scheduling | CPU | Dynamic-arrival trace and budget invariants | 120–180 min |
| [09](course/part2/09-prefix-cache.md) | 2 | Prefix identity, reuse and eviction | CPU | Cold/warm correctness and divergence tests | 120–180 min |
| [10](course/part2/10-engine-integration.md) | 2 | Integrate and stress the small engine | CPU | Capstone report and full test suite | 120–240 min |
| [11](course/part3/11-source-walkthrough.md) | 3 | Read immutable production source | No GPU required | Six-boundary source map | 90–150 min |
| [12](course/part3/12-backends-and-graphs.md) | 3 | Backend dispatch, compiler and graphs | GPU optional; required for performance | Correctness/dispatch/portability report | 120–180 min |
| [13](course/part3/13-quantization-and-speculation.md) | 3 | Quantization and speculative work | GPU optional; model-specific | Representation or verification-state report | 120–180 min |
| [14](course/part3/14-parallelism.md) | 3 | Placement and parallelism | Two GPUs optional | Rank diagram and communication ledger | 120–180 min |
| [15](course/part3/15-kv-transfer.md) | 3 | Offload/disaggregation contracts | Cluster optional | Transfer sequence and fault matrix | 120–180 min |
| [16](course/part3/16-hybrid-and-multimodal.md) | 3 | Hybrid states and multimodal identity | Source reading; GPU optional | State inventory and invalid-reuse example | 90–150 min |
| [17](course/part4/17-contributing.md) | 4 | Debug, profile and contribute | CPU or relevant target hardware | Reproducible finding and draft PR | 120–240 min |

## Three routes

**CPU-only contributor route:** 00, 02–11, then source-based exercises in 12–17. Read 01 to understand the real service boundary, but do not mark its GPU execution complete. Produce the integrated engine and a source-backed investigation.

**Serving engineer route:** 00–05, selected implementation lessons 06–11, then 12 and one domain workshop. Complete a real server smoke test and a controlled benchmark on an instructor-validated GPU environment.

**Future maintainer route:** the full core, then 12, 15 and 17, with 14 or 16 as an elective. Prioritize dispatch/lifetime reasoning, test quality and useful review evidence over model or PR counts.

## Eight-week cohort

| Week | Meeting A | Meeting B | Exit artifact |
|---|---|---|---|
| 1 | Orientation and environment | Inference and hardware | First trace, optional real-server smoke |
| 2 | KV memory | Measurement design | Memory ledger and experiment protocol |
| 3 | Dense decoder | Incremental cache | Numerical equivalence tests |
| 4 | Paged allocation | Ownership and eviction | Boundary and lifetime tests |
| 5 | Scheduling | Prefix reuse | Dynamic-arrival and cold/warm traces |
| 6 | Engine integration | Production source tour | Capstone and source map |
| 7 | Backends/graphs | One selected advanced workshop | Hardware or source-backed report |
| 8 | Debugging and contribution | Peer review and demonstrations | Reproducible finding and reviewed submission |

This schedule assumes preparation and coding between meetings. A shorter introductory study group should stop after the first six chapters instead of presenting every elective without evidence.

# 14 · Parallelism is a placement and communication choice

**Material status:** Advanced workshop brief. **Source-check date:** 2026-09-22.

The purpose of this workshop is to reason about what is partitioned and which data must move. It is not a claim that a particular parallel configuration is supported for every model or device.

## Learning objective and mental model

Tensor parallelism partitions tensor computations across ranks. Pipeline parallelism places different model stages on different ranks. Data-parallel replicas serve different work with replicated model capacity, subject to the system's routing and coordination. Expert parallelism distributes expert computation and introduces routing-related movement for MoE layers. These choices can interact; the names alone do not specify the actual topology.

Begin with a drawing of ranks, devices, process boundaries and links. Annotate model weights, active token tensors, KV state and collectives. For a single operation, identify which rank owns each output and what communication makes the result correct. A performance claim without the topology cannot distinguish compute scaling from communication effects.

## Memory arithmetic with assumptions

A tensor-parallel degree of N does not justify dividing every memory term by N. Some states may be replicated; head counts and architecture constraints affect partitioning; workspaces and buffers introduce additional costs. Use the simple KV estimator only as an unsharded dense-attention baseline, then inspect the selected model/backend's actual state placement.

For pipeline execution, reason about stage balance, in-flight work and bubbles. For expert execution, reason about imbalance and token routing, not just total parameter count. For serving replicas, compare aggregate capacity and tail latency under a specified routing policy.

## Optional two-device lab

On an instructor-validated runtime, compare `TP=1` with `TP=2` using `labs/serve.sh` only when that model supports the arrangement and fits the baseline. Preserve model revision, precision, workload and cache policy. Save topology and collective/backend logs. Report per-request latency, aggregate output throughput and failure counts rather than announcing a single scaling factor.

This shell variable only configures tensor parallelism. It does not instantiate a PP/DP/EP experiment. Those are additional release-specific labs to author after inspecting the corresponding deployment documentation and source; they are not delivered as working configurations in this package.

## Acceptance artifact

Submit a rank diagram, a memory ledger separating sharded and replicated terms, and one communication bottleneck hypothesis. Hardware-free learners can use a hypothetical topology clearly labeled as such. GPU execution and scaling measurements must remain `not_run` until actually performed.

## References

- [engine-core] [vllm/v1/engine/core.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/engine/core.py)
- [S3] [vLLM platform-specific GPU installation](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/)
- [S6] [vLLM serving benchmark CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/)

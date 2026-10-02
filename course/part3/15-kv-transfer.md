# 15 · Offloading and disaggregation need lifetime proofs

**Material status:** Advanced workshop brief. **Source-check date:** 2026-09-22.

This workshop treats external KV as a systems protocol rather than a “copy tensor” operation. No LMCache, Mooncake, MoRI, NIXL or other external connector is implemented or validated by the toy.

## Distinguish the goals

Prefix caching reuses previously computed input state. Offloading moves state to another memory/storage tier to trade device capacity against transfer and management cost. Prefill/decode disaggregation separates execution roles and transfers state between them. These mechanisms can be combined, but success in one does not prove correctness or benefit in another.

A connector interface does not guarantee a direct GPU-to-SSD path. Trace the actual data plane, including host staging, registration, copies, storage operations and transport. State what runs on the scheduler and what runs on workers. Treat transport completion and verified destination contents as separate evidence during debugging.

## Read the scheduler/worker contract

The inspected vLLM connector base documents scheduler-side matched-token queries, allocation-state updates and request completion. Worker-side operations initiate loads, wait for layer readiness, save layer state and report asynchronous completion. `request_finished()` may defer freeing blocks until transfer completion is reported. That is a lifetime decision, not just a metadata callback.

```text
Scheduler: discover reusable external state
    -> allocate/reserve destination blocks
    -> send transfer metadata to worker execution
Worker: initiate load
    -> establish layer readiness before use
    -> execute / initiate saves where appropriate
    -> report completed transfers
Scheduler + worker: release ownership only when safe
```

This is a logical teaching sequence; implementations can overlap work and have different layerwise paths. The interface alone is not an observed trace for a named connector.

## Performance model

For transfer size S and effective bandwidth B, a first lower-bound term is `S / B`. Add lookup, registration, staging, queueing and synchronization overheads as applicable, accounting for overlap instead of blindly adding concurrent stages. Compare the resulting critical path with recomputation and the capacity/throughput benefit of offloading. Higher cache hit rate is not sufficient evidence of better goodput.

Agentic workloads make reuse distance and session locality useful experimental axes. Construct repeated-turn and interleaved-session traces, vary time between reuses, and report the actual retained state and transfer path. Do not assume a session-aware policy is already implemented merely because a workload has session IDs.

## Fault-injection lab design

Specify tests for a missing block, partial load, timeout, cancellation while sending, eviction during an active transfer and stale completion metadata. Check destination bytes or model-level equivalence as appropriate, ownership/lifetime, and whether an error produces a defined fallback or clear failure. Never silently treat uninitialized state as a hit.

The optional cluster lab starts from one connector's release-matched official example and a known-good transport diagnostic. Name the exact connector revision, GPU/NIC topology and tier path. The base-class reading is supplied; connector-specific executable configurations and multi-node validation remain work to complete.

## Acceptance artifact

Submit a sequence diagram, buffer-ownership table, measured or explicitly hypothetical transfer cost model, and a fault matrix. A transport API returning success is not by itself proof that the model consumed the intended state safely.

## References

- [kv-connector] [vllm/distributed/kv_transfer/kv_connector/v1/base.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/distributed/kv_transfer/kv_connector/v1/base.py)
- [S9] [vLLM disaggregated prefill](https://docs.vllm.ai/en/latest/features/disagg_prefill/)
- [S4] [vLLM automatic prefix caching design](https://docs.vllm.ai/en/latest/design/prefix_caching/)

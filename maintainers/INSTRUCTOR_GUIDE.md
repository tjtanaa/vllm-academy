# Instructor guide

## The first cohort's contract

Teach a bounded, correct engine and a credible source-reading workflow. Do not promise a production vLLM reimplementation, a complete compatibility matrix or a merged upstream PR. The working implementation is a reference solution; the chapters are drafts for a human teaching/editorial review.

Each meeting should contain a prediction, a short explanation, a code/trace exercise and a falsification step. Use the eight-week schedule in `SYLLABUS.md`. A reasonable two-hour session allocates roughly 20 minutes to the problem, 25 to the mechanism, 50 to the exercise and 25 to discussion. This is a suggested teaching allocation, not a runtime guarantee.

## Before enrollment

Validate the CPU setup in a clean environment. Choose one immutable runtime/image/model combination for each GPU lane and actually run the serving and benchmarking scripts. Confirm student device access without modifying shared host drivers. Prepare predownloaded public models with documented revisions where licensing permits. Assign resource limits and cleanup rules for shared GPUs.

Do not make students debug packaging incompatibilities before seeing inference behavior. A prepared GPU environment is the initial baseline; source builds and backend experiments belong in a separate environment. Learners without GPU access must still be able to complete the numerical, memory, scheduler and source assignments.

## Teaching sequence and expected answers

**Inference bookkeeping:** after a next-token sample, the known token list can be longer than computed KV state. A subsequent forward computes the sampled token's K/V. The final output token may never need that forward when generation stops. Confusing those states causes both scheduling and cache-boundary errors.

**Memory example:** for 32 layers, 8 KV heads, head dimension 128 and 2 bytes per element, each token uses `2×32×8×128×2 = 131072` bytes of unsharded dense KV, or 128 KiB. At 8192 tokens that is 1 GiB. The example excludes scales, workspace, fragmentation and non-dense state, and is not a Qwen checkpoint specification.

**Address translation:** with B=4 and table `[7,2,11]`, logical position 5 maps to physical block 2, offset 1. The physical IDs need not be consecutive. State at a slot is usable only after the relevant writes are valid, not merely after allocation.

**Ownership:** cancellation releases request ownership, not every cache-index reference. Evicting an index entry releases index ownership, not active readers. A block can be reclaimed only after no owner still needs it. The toy and production encode this discipline differently.

**Prefix identity:** the same token block after a different parent context is not an equivalent attention state. Partial tails are private in the toy. For prompt length 8 and B=4, the toy conservatively reuses only 4 tokens so it recomputes enough to get the next-token logits. For length 9 it can reuse 8.

**Scheduling:** a bounded token-work trace proves budget compliance, not GPU throughput. The toy calls model work serially. Production has additional process, batching, speculative and asynchronous behavior.

**Benchmarking:** a larger throughput number can coexist with worse tail latency. Identical seeds can create repeated-prefix confounds. A warm kernel state and a warm prefix cache are different experimental conditions. `REQUEST_RATE=inf` with a cap is not an unconstrained open-loop arrival process.

**Source reading:** an existing runner file is not proof of runtime selection. Require learners to distinguish source inspection from execution evidence. The supplied source map is six responsibility boundaries, not a complete endpoint-to-device trace.

## Assessment

Use the rubric in `COURSE_BLUEPRINT.md`: correctness/invariants 35%, experiment/reproducibility 25%, production-source reasoning 20%, communication/review 20%. Require the learner to explain at least one failed hypothesis or missing test. Do not reward larger diffs, more expensive GPUs or more PRs.

A student who identifies an invalid assumption and stops a misleading benchmark has demonstrated useful engineering judgment. An honest `not_run` hardware cell is preferable to a guessed support claim.

## Peer review and maintenance

Assign one technical reviewer and one reproducibility reviewer to each lesson. Track source-pin changes separately from prose edits. Keep answers separate from student-facing exercises, and make access to reference solutions deliberate. Discuss upstream contributions before asking students to submit them; check for duplicate or already-fixed issues.

This course has no claimed official endorsement. Review the attribution/license and project name before public launch, and follow the target community's current contribution and conduct expectations.

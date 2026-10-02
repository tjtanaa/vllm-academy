# 17 — First useful contribution and the next phases

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

The final deliverable is not a badge for opening a PR. It is evidence that the learner can identify a problem, isolate the relevant contract, test a claim and communicate a bounded change.

## Begin with a problem small enough to explain

Good candidates include a missing validation case, a misleading version-specific explanation, an uncovered cancellation path, a wrong tensor-shape assumption, a processor/placeholder mismatch or an incomplete reproduction. Kernel changes are only one possible route.

Use the source map to identify ownership rather than spreading fixes across unrelated layers. A model-specific behavior should not automatically be added to a shared runner. An output-format issue should not automatically become a scheduler change.

## Capstone workflow

Write the smallest reproducible input and expected behavior. Record the precise source and model revisions. Add a test that fails for the claimed reason. Make a minimal change. Run relevant tests and record exactly what did and did not run. Explain the implementation boundary and any compatibility effect.

Review a peer's artifact before declaring your own finished. Ask whether the test isolates the bug or merely prints a plausible answer. Ask whether a claimed GPU improvement has raw measurements and a controlled workload.

This lesson deliberately does not freeze upstream contribution policy. Read the repository's current contribution requirements immediately before submitting. No automatic upstream issue or PR is created by the course.

## Hands-on review exercise

Select one deliberate bug from the labs: missing causal mask, wrong cached-chunk offset, mismatched renderer revision, silently dropped vision feature, early slot recycling or incomplete SSE framing. Write a reviewer comment that names the invariant, supplies a minimal failure and proposes a narrow test.

Then contrast the toy repair with a real source responsibility. Do not claim that the same code snippet can simply be pasted into production.

## Connect Phase 1 to Phase 2

Phase 2 asks why a production abstraction changes between exact versions. Use a before/after contract analysis: problem, mechanism, trade-off, test and hardware implications. New class names alone are not a meaningful version-history lesson.

## Connect Phase 2 to Phase 3

Phase 3 decides which changed ideas belong in the teaching engine. Options include a core adaptation, a small optional experiment, a source-only explanation or an explicit deferral. Keep one evolving implementation and stable reviewed cohort snapshots rather than copying an engine directory per upstream version.

## Completion and exit ticket

Submit the contribution artifact together with the model-demo records, request ledger, multimodal tensor/ownership explanation and numerical tests. A useful issue can pass when a PR is not yet justified; an upstream merge is not under the course's control.

A learner who explains every box but cannot tell when a buffer is safe to reuse still has an important gap. A learner with passing code but no understanding of the request contract also has more work to do. The Academy aims for both computation and systems understanding. [Instructor rubric](../INSTRUCTOR_GUIDE.md)

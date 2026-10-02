# Chapter title

**Status:** draft / reviewed / CPU-tested / GPU recipe, unverified / workshop brief.
**Author and reviewer:** fill before publication.
**Source pin and last checked date:** fill before publication.

Explain the problem in one concrete example and connect it to the preceding lesson.

## Learning objectives

Use observable actions: derive a memory term, trace a request, implement an invariant, reproduce a failure, or explain a tradeoff. “Understand everything about attention” is not assessable.

## Mental model

Name the inputs, outputs, owner of each state object, and scope of the simplified model. Include one original diagram or trace where it resolves an ambiguity.

## Derivation and implementation

Define symbols and tensor shapes before formulas. Show where the code enforces the claim. Label pseudocode and distinguish reference behavior from production behavior. Do not assert that a source path is a live runtime path without evidence.

## Reproducible lab

Record environment, model/source revisions, exact commands, input shapes, expected assertions, raw output locations, and failure modes. Require no hidden credentials or private datasets. Mark all unexecuted hardware recipes explicitly.

## Negative controls and tests

Include an invalid or boundary input, a falsifiable prediction and a regression test. For performance, define baseline, warmup, repetitions, failure accounting and quality/correctness gates.

## Production source bridge

Provide immutable source links, symbols, and the exact invariant each location illustrates. Explain one difference from the toy. Do not copy large upstream passages into the course.

## Hardware evidence

Separate the API/dispatch layer from backend/kernel support. Record CUDA and ROCm runs independently, including architecture and selected backend. `not_run` is a valid entry, not a defect to hide.

## Exercises and acceptance

State the submission artifact and passing criteria. Keep instructor answers in a separate guide. Add an optional extension only after the core is attainable.

## References

Use primary papers, official documentation and immutable source links actually used in the lesson. Record dates for mutable documentation. Attribute inspiration and preserve third-party license requirements for any later imported material.

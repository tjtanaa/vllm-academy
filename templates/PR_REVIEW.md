# Contribution / review evidence — template

## Problem and impact

User-visible problem:
Existing issue or related work checked:
Affected versions, models, shapes and hardware:
Expected versus actual behavior:
Minimal reproduction and exact environment:

## Proposed change

Scope and why this layer owns the fix:
Source path and immutable baseline:
Invariant being restored or optimization hypothesis:
Alternative considered and rejected:
Behavior intentionally not changed:

## Tests and measurement

Regression test failing before / passing after:
Numerical comparison and tolerance:
Boundary, cancellation or failure tests:
Relevant upstream tests run (separate from course tests):
CUDA status / ROCm status / selected execution path:
Benchmark methodology, raw results and regressions when relevant:
Untested conditions and why:

## Review questions

Can ownership outlive a request? Can asynchronous work still access freed state? Does a config flag prove that this backend ran? Are namespace/adapter/model identities complete? Is the timing boundary honest? Does the change preserve correctness outside the benchmark shape?

## Submission responsibilities

Re-read the target project's current contribution instructions. Check sign-off, formatting, tests and required AI-assistance disclosures. Do not submit a change you cannot explain and review. Do not expose sensitive prompts, keys or internal logs. A local investigation report is a valid course outcome even without an upstream PR.

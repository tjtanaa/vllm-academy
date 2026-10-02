# mini-vLLM evolution — <concept>

**Status:** proposal. **Current → proposed teaching version:** explicit values.
**Upstream refs:** exact commit(s) and symbols. **Phase 2 explanation:** link.
**Owner/reviewer:** unassigned until agreed.

## Learning value and scope

Which new production concept should a learner understand? Why is it worth introducing now? Choose core adaptation, optional experiment, source-only explanation or deferral. Set a readability/complexity budget and identify required prerequisites.

## Dataflow and invariant

Show the old and new toy dataflow and interfaces. Specify ownership, token accounting, ordering and failure/cancellation rules affected by the change. State what the toy deliberately does not reproduce from production.

## Implementation and regression plan

Identify files and the smallest coherent implementation steps. Retain a reference/oracle where possible. Include normal, boundary, cancellation, exhaustion and failure tests as applicable. A scheduler/lifetime change needs invariant tests, not just identical output for one prompt.

## Evidence and migration

Record the environment and raw results. Do not claim speedups without a benchmark. List lessons, exercises, instructor answers, diagrams, manifests and commands that need updates. Explain how existing cohort tags preserve old assignments.

## Acceptance

The mechanism is correct under stated assumptions, small enough to teach, source-linked, regression-tested and human-reviewed. New GPU/async/distributed claims need their own hardware evidence. Update `CHANGELOG.md`, `versions/manifest.json`, the code version and package version together when the teaching API changes.

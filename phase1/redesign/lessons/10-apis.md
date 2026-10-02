# 10 — APIs and the return path

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

An inference engine is not defined by a single HTTP endpoint. Separate **transport**, **protocol**, **model task**, **output policy** and **application orchestration** before comparing APIs.

## Compare requests that look similar but mean different things

A completion request supplies a sequence to continue. A chat request supplies messages requiring a model-compatible serialization contract. Responses-style interfaces may represent richer input/output items and state references. Embedding requests seek vectors rather than a sampled response. Speech endpoints require a compatible speech model and preprocessing. The framework's endpoint catalog does not make a text-only checkpoint support every task. [R26](../REFERENCES.md)

Give learners three artifacts: a completion prompt, a role-message request and an embedding input. Ask which operations are identical and which change. Do not suggest that adding a route name changes the model's training objective.

Streaming is independent of many of these distinctions. A service can return accumulated output or incremental events. Returning tool-call fields also does not, by itself, execute a tool; identify the application or service component responsible for that action.

## Follow the reverse path

Neural output can be vocabulary logits, hidden states or other model-specific outputs. Sampling/pooling and output processing turn it into the task result. Detokenization converts token IDs into text; protocol formatting supplies fields, finish reasons and stream framing. A selected stop condition and a disconnected client are different termination events.

The pinned chat router delegates to a handler and distinguishes error JSON, complete JSON and SSE output. Read those branches as a small concrete example, not a comprehensive compatibility claim for every endpoint.

## Run the framing lab

```bash
python -m labs.streaming
python -m pytest -q tests/test_mechanisms.py -k 'sse or stream'
```

A synthetic SSE response is split at arbitrary byte boundaries, including inside a multibyte UTF-8 character. The decoder must accumulate bytes and events correctly. A network chunk is not a model token, a character, a JSON object or necessarily a complete SSE event.

The lab is an in-memory parser, not an HTTP service and not a benchmark client. It includes keepalive comments and rejects an incomplete event rather than silently declaring successful completion.

## Source detour

Read `create_chat_completion` in the `api` map entry. Locate validation, cancellation wrapping, handler selection and response types. Find one branch where a request fails without invoking a useful model forward. That is a valid service responsibility, not wasted boilerplate.

## Exercise and exit ticket

Design a client-disconnect test: what work should be cancelled, who must be told, and what state cannot be freed until in-flight use ends? State which parts can be tested with a fake backend and which require integration.

Submit an API comparison using task, representation, state, streaming and applicability—not just URL names. [Atlas API matrix](../ARCHITECTURE_ATLAS.md)

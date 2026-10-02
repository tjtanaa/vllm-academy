# 07 — One model, many requests

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

A generation loop for one request does not yet solve serving. Multiple requests arrive and finish at different times, consume different amounts of state, and may be cancelled while other work is running.

## Start with a pencil-and-paper scheduler

Consider request A with an uncomputed six-token prompt and request B that is decoding. Give the iteration a four-token budget. One possible teaching policy executes one token for B and a three-token chunk for A. The next iteration re-evaluates remaining work and resource availability.

This is a proposed example, not an exact transcription of vLLM's scheduling algorithm. The point is that the unit of choice can be work within an iteration rather than an entire request from start to finish. Orca is a useful historical reading for iteration-level serving. [R22](../REFERENCES.md)

Now add a third request, an exhausted cache pool and a cancellation. Ask which decisions need an admission policy, which need memory state, and which need a completion callback. These questions motivate abstractions instead of presenting their class names first.

## Run the existing engine

From the **existing Academy checkout**, not the supplement directory:

```bash
python -m mini_vllm.demo
python -m pytest -q
```

Inspect `mini_vllm/engine.py`: request admission, step planning, model execution, output update and cleanup. The existing implementation chooses logical work for multiple requests but executes their forwards serially. That is not physically batched GPU execution.

From the supplement, read its pinned scheduler excerpt:

```bash
python -m labs.source_walk --checkout /path/to/pinned-vllm --entry scheduler
```

Find how request admission constraints differ from model-runner capacity. Deeper token accounting is a follow-on bounded reading, not something the initial constructor excerpt alone proves.

## State transitions and fairness

Draw `waiting → running → finished`, with cancellation and error paths. Then ask whether a request can starve under the teaching policy. A token budget limits work; it does not automatically guarantee fairness, latency objectives or successful admission under memory pressure.

An asynchronous HTTP handler is not itself a continuous-batching scheduler. Similarly, several CPU threads do not establish efficient accelerator batching. Separate concurrency at each boundary.

## Exercise and exit ticket

Submit a three-iteration trace containing one new arrival and one completion. Identify which state belongs to the scheduler versus the model's cached tensors. Add a cancellation and show who releases resources.

A passing answer explains why increasing a work budget might improve device efficiency while worsening some requests' latency. It does not assume throughput and latency always move together. [Source map](../SOURCE_MAP.md)

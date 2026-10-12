# Q9 · Mock Interview: rehearse the inference-engineer loop

**Needs:** Discord (a friend and a voice channel make it better) · **Time:** 30 min, once a week · **Episodes:** E25, plus every "Say it like a pro" · **XP:** +75 (plus up to +100 per `/mock`)
**[繁體中文](Q9-mock-interview.zh-TW.md)**

Inference-engineer interviews keep circling the same ideas: memory math, batching and scheduling, caching, parallelism, measurement, and one system-design question. Knowing the answer isn't enough; you have to *say* it clearly in two minutes. This lab is a weekly rehearsal loop.

## 1. Warm up with one question

Pick your level. Answer out loud **before** revealing anything, two minutes, timer on. Then reveal the key points, the follow-ups and the red flags.

```text
/interview level:Junior
/interview level:Mid kind:Design
```

> ✅ **Checkpoint:** you said an answer out loud and can name one key point you missed.

## 2. Learn the system-design skeleton

Most serving-design questions go best in the same five moves. Practice the skeleton until it's automatic.

```text
1. Clarify:  model, context, traffic (QPS, burstiness), SLOs (TTFT, ITL, p99), cost
2. Memory:   weights + KV × context × concurrency → GPUs and parallelism (E07, E19)
3. Engine:   batching, chunked prefill, prefix caching, quantization, spec decode (S2, S4)
4. Fleet:    routing (cache-aware), autoscaling (cold starts!), P/D split if needed (E20, E28)
5. Measure:  what you'd benchmark and alert on (E24)
```

> ✅ **Checkpoint:** you can write the five moves from memory.

## 3. Do the memory math on the spot

Every design answer leans on step 2. Rehearse with the calculator until you can do it on paper.

```text
/kvcalc model:llama-3.1-70b context:32768 gpu:H100 gpus:4 users:16
```

> ✅ **Checkpoint:** you predicted whether 16 users fit *before* the bot answered, and you were right (or you know why you weren't).

## 4. Run a full mock

Five questions, scored. Rate yourself honestly: "Partial" is the most useful button. The bot keeps your best score, and 80%+ earns 🎤 **Interview Ready**.

```text
/mock level:Mid
```

> ✅ **Checkpoint:** you finished a mock and wrote down the two weakest questions to review this week.

## 5. Patch your weak spots

For each weak question, open its linked episode, reread the "🎤 Say it like a pro" answer, and record yourself giving a 60-second version. Listen back. Cut filler words and add one concrete number.

```text
/episode episode:E17
```

> ✅ **Checkpoint:** your 60-second answer contains one mechanism, one number and one trade-off.

## 6. Prepare your project stories

Expect "tell me about something you built." Use your Q5 engine, Q7 benchmark or Q8 PR, structured as situation → what you did → measured result → what you'd do differently.

```text
"I benchmarked prefix caching on Qwen3-8B (Q7). TTFT p99 dropped X% on a 75%-shared-prefix workload,
but with no shared prefix there was no gain, so I'd only enable it where prompts actually share prefixes."
```

> ✅ **Checkpoint:** you have two stories, each under 90 seconds, each with a number in it.

## 7. Mock a human

Pair up in a voice channel. One person interviews using `/interview` questions and the follow-ups; the other answers with the camera on if you're brave. Swap after 15 minutes. Give each other one "keep" and one "change".

```text
#mock-interviews  ← post "LFG mock, Mid level, 21:00" and find a partner
```

> ✅ **Checkpoint:** you gave and received feedback once. Repeat weekly. Scores in `/profile` should climb.

## What you learned

- A strong answer has a mechanism, a number, a trade-off and a follow-up you saw coming.
- The design skeleton (clarify → memory → engine → fleet → measure) keeps you from rambling.
- Mocks are reps. Weekly reps beat one cram session.

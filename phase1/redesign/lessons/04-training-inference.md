# 04 — Training is not generation

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

The same model weights participate in two very different loops. Training measures an objective and updates parameters. Autoregressive generation chooses new tokens and extends an input history without updating those parameters.

An autoregressive text model factorizes sequence probability as `P(x_1,...,x_T) = product_t P(x_t | x_<t)`. This describes a conditional modeling objective; it does not specify an HTTP API, a cache allocator or an instruction-following policy. The training and generation loops use that conditional model differently.

## Work through a four-token example

For a sequence `[a,b,c,d]`, a next-token training example can use inputs `[a,b,c]` and targets `[b,c,d]`. Causal masking prevents each input position from reading future input tokens, while known targets supply the loss. Teacher forcing supplies the observed history rather than the model's previously generated mistakes.

In generation, the model processes an available history, selects a token from the last relevant logits, appends it and repeats. A token selected now does not retroactively appear in the forward pass that selected it. Later KV lessons depend on that distinction.

## Run a tiny training loop

```bash
OMP_NUM_THREADS=1 python -m labs.train_tiny
```

The lab fits a synthetic periodic sequence. Locate zeroing gradients, forward computation, shifted-target cross-entropy, backward computation and the optimizer step. Observe the initial and final **training** loss.

This is not evidence of general language understanding. There is no held-out natural-language evaluation, instruction-following benchmark or pretrained checkpoint here. A lower training loss demonstrates that this optimizer/model/target loop can fit the supplied exercise.

Now inspect `NaiveDecoder.generate`. It has no optimizer or backward call. Compare cached and uncached greedy outputs. Turning off gradient recording saves work and changes autograd behavior; it does not remove the dependency on preceding tokens.

## Sampling is its own policy

Logits are unnormalized vocabulary scores. Greedy selection takes an argmax. Temperature changes the distribution before sampling; top-k/top-p restrict the candidate distribution in different ways. These choices do not change the architecture's weight shapes, but they affect reproducibility of generated output.

The lab intentionally uses greedy generation. Full sampling options belong to the native pretrained-engine patch and must be tested there. Do not label a random-weight greedy loop a validated conversational assistant.

## Connect this to model history

A base causal checkpoint was not necessarily trained to follow chat instructions. Instruction-following post-training changes behavior through additional training, while few-shot prompts specify a task through context. Neither should be conflated with request scheduling or with a chat template's serialization job. [R06–R07](../REFERENCES.md)

## Exercise and exit ticket

Annotate which tensors need gradients during training and which state survives between generation iterations. Explain why `model.eval()` and disabling gradient recording are related to execution but are not the same operation.

Submit one shifted-label example, one generation iteration trace, and one limitation of the synthetic training result. Predict a failure caused by accidentally training on unshifted targets, then describe a test that would reveal it.

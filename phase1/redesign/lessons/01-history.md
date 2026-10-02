# 01 — History as design problems, not brand trivia

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

History is useful when it explains why an abstraction exists. Present several branching developments, not an inevitable march in which each new architecture makes every older one obsolete.

## A compact historical map

| Selected milestone | Problem to understand | Consequence for the course |
|---|---|---|
| Neural probabilistic language models, 2003 | Exact counts struggle to share statistical strength across related contexts. | Compare a count baseline with learned embeddings. [R01] |
| Attention for neural translation, 2014 preprint / 2015 conference | A fixed-vector summary can constrain access to an input sequence. | Explain selecting information from multiple positions. [R02] |
| Transformer, 2017 | Build sequence computation around attention rather than recurrence. | Trace attention and distinguish encoder from causal decoder. [R03] |
| Generative pretraining and BERT, 2018 | Different objectives yield different reusable capabilities. | Contrast causal continuation with bidirectional representations. [R04–R05] |
| GPT-3, 2020 | Tasks can be specified through context examples. | Prompt content changes behavior without necessarily updating weights. [R06] |
| Instruction-following post-training, 2022 | A next-token-trained model is not automatically a helpful assistant. | Distinguish base from instruction-tuned checkpoints. [R07] |
| ViT / CLIP / visual instruction models, 2020–2023 | Images need representations and a learned connection to language tasks. | Separate image encoding from text generation. [R19–R21] |
| Serving systems, 2022–2023 | Repeated computation, changing request lengths and state allocation waste resources. | Scheduling, persistent state and attention IO become distinct lessons. [R22–R24] |

All references are in [the source register](../REFERENCES.md). This selection is not an exhaustive LLM chronology. The dates identify papers, not the first-ever occurrence of every underlying idea.

Between feed-forward neural language models and attention-only architectures, recurrent and sequence-to-sequence models carry evolving hidden representations through a sequence. Attention in the translation setting makes encoder states available to a decoder rather than requiring all relevant input information to fit one fixed summary. This is the bridge to Q/K/V attention, not a claim that recurrence ceased to matter. [R02](../REFERENCES.md)

## Make a historical limitation tangible

```bash
python -m labs.bigram
```

The synthetic model sees histories `cats eat` and `dogs eat`. Its prediction only depends on the last word, so those histories produce the same distribution. Explain what information the implementation discarded. More data cannot make this particular conditional representation recover a distinction it never stores.

Then ask: would a larger context table help? Yes, but it changes the number of contexts the system must represent. Would embeddings alone solve all long-range reasoning? No. This is an entry into representation choices, not a proof that neural networks solve every language problem.

## Connect history to modern inference

Keep four activities separate: training updates weights; prompting supplies context; post-training changes an already trained model through further optimization; serving orchestrates execution for users. Retrieval and tool results can augment context without being equivalent to any of these weight updates.

An encoder used for embeddings is not a failed chatbot. A vision encoder is not automatically an image-captioning model. The task and training objective matter before an API is selected.

## Exercise and exit ticket

Choose three rows and write “problem → mechanism → remaining cost” for each. Propose one question a bigram model cannot distinguish, then show the exact line of code causing the limitation. Do not submit an unsupported timeline of parameter counts or leaderboard rankings.

A passing explanation connects the history to something the learner can inspect or measure in later lessons.

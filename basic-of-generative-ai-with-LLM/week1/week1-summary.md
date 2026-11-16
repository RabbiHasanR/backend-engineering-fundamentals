# Week 1 Summary: Quick Revision

> Short recall notes. For the full details, see [use-case-project-lifecycle-model-pre-training.md](use-case-project-lifecycle-model-pre-training.md). Tags like `L8` point to the lesson number.

---

## 1. Big Picture `L0 L1 L2 L3`
**Remember:** an LLM is a next-token predictor; every capability is built on that.

- **GenAI** = a subset of ML that learns statistical patterns from huge human-written text (trillions of words).
- **Foundation model** = a large pre-trained model. You **use it as-is or fine-tune it**; you rarely train one from scratch.
- **Emergent properties**: large models can also reason, break tasks down, and solve problems.
- **Interaction:** `Prompt → LLM → Completion`. The whole process is **inference**. The prompt must fit inside the **context window**.
- **Use cases:** chat, essays, summarization, translation (including natural language → code), NER and information retrieval, and connecting to external APIs or data (Week 3).
- **Size trade-off:** a large model gives broad knowledge; a small, fine-tuned model is strong on one focused task.
- Lab model: **FLAN-T5**.

---

## 2. Transformers `L4 L5 L6 L10`
**Remember:** "Attention Is All You Need" (2017). It is parallel, scales on GPUs, and gives every word context from every other word.

**Why not RNN?**

| | RNN | Transformer |
|---|---|---|
| Context | A few previous words | Whole sentence or document |
| Processing | Sequential | **Parallel** |
| Scaling | Compute explodes | Scales well on GPUs |

Language is hard because of **homonyms** ("bank") and **syntactic ambiguity** ("teacher taught the student with the book").

**Data flow:**
```
Text → Tokenize → Embedding + Positional encoding
     → ENCODER [Self-Attn → FFN] × N           (runs once)
     → DECODER [Masked Self-Attn → Cross-Attn → FFN] × N   (once per output token)
     → Linear (logits) → Softmax (probabilities) → pick token → loop until <end> → Detokenize
```
- **Tokenizer**: rule-based, not a neural network. Use the **same tokenizer** for training and inference.
- **Embedding** = a vector of meaning; similar words sit close together.
- **Positional encoding** keeps word order, which is needed because tokens are processed in parallel.
- **Multi-head attention** = 12–100 heads, each learning a different language aspect **on its own**, starting from random weights.
- **Cross-attention** = the decoder looks at the encoder output **inside every decoder layer**.
- Embedding, encoder, decoder, and softmax are all **one model**, trained together.

**The 3 model types (the most important table):**

| Type | Also called | Pre-training objective | Context | Best for | Examples |
|---|---|---|---|---|---|
| **Encoder-only** | Autoencoding | **MLM**: predict `<MASK>` | Bidirectional | Classification, sentiment, NER | BERT, RoBERTa |
| **Decoder-only** | Autoregressive | **CLM**: predict the next token | Unidirectional | Text generation, most tasks at scale | GPT, BLOOM, LLaMA |
| **Encoder-decoder** | Seq-to-seq | **Span corruption** (`<X>` sentinel) | Encoder both ways, decoder forward | Translation, summarization, Q&A | T5, FLAN-T5, BART |

> Most modern LLMs are **decoder-only**.

---

## 3. Prompting & In-Context Learning `L7`
**Remember:** put examples in the prompt; if 5–6 examples still fail, **fine-tune**.

| Type | Examples in prompt | Works for |
|---|---|---|
| Zero-shot | 0 | Large models |
| One-shot | 1 | Smaller models |
| Few-shot | 2+ (**mix the classes**) | Even smaller models |

- Prompt structure: **Instruction + Context + Output cue**.
- Limit: the **context window** caps how many examples fit.
- Flow: `Zero → One → Few-shot → still bad? → Fine-tune (Week 2)`.

---

## 4. Inference Configuration `L8`
**Remember:** these are settings chosen at **generation time** and are not learned. They control **length and creativity**.

| Setting | What it does |
|---|---|
| `max_new_tokens` | A **cap** on output length (it can stop earlier at `<end>`) |
| Greedy (default) | Always picks the top token: predictable, but can repeat |
| Random sampling | Picks by weight: varied, but can drift off-topic. Needs **`do_sample=True`** |
| `top_k` | Keep only the top **k** tokens (fixed count) |
| `top_p` | Keep the top tokens until their probabilities **sum to p** (count adapts) |
| `temperature` | **Reshapes** the distribution: `softmax(logits / T)` |

- **Temperature:** `T < 1` makes the distribution peaked and focused; `T = 1` leaves it unchanged; `T > 1` makes it flat and creative.
- **Pipeline order:** `Temperature → Top-k → Top-p → Sample → repeat until <end> or max`.
- ⚠️ top-k, top-p, and temperature **do nothing under greedy decoding**.
- Presets: factual or code → low T (0–0.3); chat → 0.7 with top_p 0.9; creative → 1.0+.
- In practice, tune **temperature + top-p** and leave top-k at its default.

---

## 5. Generative AI Project Lifecycle `L9`
**Remember:** Scope narrow → pick an existing model → adapt and align (a loop) → integrate.

```
1. SCOPE → 2. SELECT → 3. ADAPT & ALIGN (iterate) → 4. APP INTEGRATION
```

| Stage | Key point |
|---|---|
| **Scope** | **The most important step.** Many tasks or one task? A narrow scope saves cost. |
| **Select** | Use an existing base model. Pre-train only in special cases. |
| **Adapt & Align** | Prompt eng. → fine-tune (W2) → RLHF (W3), with **evaluation** at each step, in a loop |
| **Integrate** | Optimize for deployment; build infrastructure (W3) |

- Built-in LLM limits: **hallucination** and weak **math and complex reasoning**. These need extra infrastructure, not just training.

---

## 6. Pre-training & Compute `L10 L11 L12 L13 L14`
**Remember:** pre-training is expensive, so use **quantization**, **multi-GPU** training, **Chinchilla's 20× rule**, and pre-train from scratch only for unusual domains.

**Pre-training basics `L10`**
- **Self-supervised** learning on GB–PB of unstructured text; no labels are needed.
- **Data curation**: often only **1–3% of the scraped tokens** are kept.
- Choose a model on a **model hub** (Hugging Face) by reading its **model card** (use cases, training, limits).

**GPU memory & quantization `L11`**
- 1 parameter at FP32 = **4 bytes**, so 1B params ≈ **4 GB** just for the weights.
- Training (Adam states, gradients, activations) needs **≈ 6×**, so a 1B model at FP32 needs ≈ **24 GB**.

| Type | Bytes | Note |
|---|---|---|
| FP32 | 4 | Full precision |
| FP16 | 2 | Small range (±65,504) |
| **BFLOAT16** | 2 | **FP32 range, half the memory. The practical default** (FLAN-T5) |
| INT8 | 1 | −128 to 127, large precision loss |

- Quantization lowers the **precision**; the number of parameters stays the same.

**Multi-GPU `L12`**

| | DDP | FSDP |
|---|---|---|
| Model | **Full copy** on every GPU | **Sharded** (params, gradients, optimizer states) |
| Data | Split | Split |
| Use when | The model fits on one GPU | The model is **too big** for one GPU |
| Cost | Redundant memory | More GPU-to-GPU communication |

- FSDP is based on **ZeRO** (stages 1/2/3 shard optimizer states → plus gradients → plus params).
- **Sharding factor**: 1 behaves like DDP; the number of GPUs gives full sharding; values in between are hybrid.

**Scaling laws `L13`**
- Performance depends on **compute budget, dataset size, and parameter count**, each following a power law.
- Unit: **petaflop/s-day** ≈ 8 V100 or 2 A100 GPUs running for one day.
- **Chinchilla:** optimal training tokens ≈ **20 × parameters** (70B → 1.4T tokens).
- GPT-3 is **over-parameterized and under-trained**. A smaller model trained on more data can beat it.

**Domain adaptation `L14`**
- Pre-train from scratch **only** when the domain's language is unusual (law, medicine, finance).
- **BloombergGPT**: 50B params, **51% finance + 49% general** data, 569B tokens (below the Chinchilla optimum because finance data was scarce).

---

## 7. Gotchas I Clarified (My Q&A) `L6 L8`
- **Decoder input** = only its own generated tokens so far (`<start> I love…`). It sees **all** encoder vectors at every step through cross-attention.
- **Why cross-attention sits in the middle of the decoder layer:** the decoder first reads its own progress, then looks at the input.
- **N** = the number of stacked layers, fixed by the model design. It is **not** the input or output length.
- **Output length:** the model stops when it predicts **`<end>`**, a normal vocabulary token it learned during training, or at `max_new_tokens`.
- **KV cache:** past tokens' results are cached, so each step processes only the newest token.
- **Top-p** doesn't depend on top-k. You only set p, and the candidate count adapts ("capital of France" → only "Paris").
- **Model parameters** (learned weights) ≠ **configuration parameters** (generation settings). Inference never changes the weights.
- In the lecture, the FFN "produces logits"; in reality a **final linear layer** produces them.

---

## 8. Numbers to Remember

| Fact | Value |
|---|---|
| Transformer paper | 2017, "Attention Is All You Need" |
| Attention heads | 12–100 |
| Original embedding size / layers | 512 dims / 6 layers |
| Data kept after curation | 1–3% |
| Bytes per param (FP32 / BF16 / INT8) | 4 / 2 / 1 |
| Training memory | ≈ 6× the weight memory |
| 1B model training at FP32 | ≈ 24 GB |
| Chinchilla rule | 20 tokens per parameter |
| GPT-3 | 175B params, ≈ 3,700 petaflop/s-days |
| BloombergGPT | 50B params, 569B tokens, 51/49 data split |
| Few-shot limit before fine-tuning | 5–6 examples |

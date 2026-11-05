# Prerequisites

Study notes for reading **"Attention Is All You Need"** (Vaswani et al., 2017).

---

## 1. Embeddings

**Why:** a neural network only does math on numbers, so every word must become numbers.

| Method | Example | Problem |
| --- | --- | --- |
| Word IDs | cat=1, dog=2, apple=3 | Model treats IDs as quantities ("apple = 3 × cat") |
| One-hot | cat=[1,0,0], dog=[0,1,0] | Huge (37,000 numbers per word) and all words equally different (dot product 0, distance √2 for every pair) |
| **Embedding** | cat=[0.8, 0.9, 0.1] | ✅ Short, dense, **similar words get similar numbers** |

- **Similarity = dot product:** cat·dog = 1.38 (similar), cat·apple = 0.17 (different).
- **king − man + woman ≈ queen:** king − man leaves only "royalty"; add woman → royal woman.
- **Lookup table:** 37,000 rows (tokens) × 512 columns (numbers). Like `SELECT vector WHERE token_id = 42`.
- **512 (d_model)** is a **hyperparameter** chosen by the researchers (base 512, big 1024). Must divide by heads: 512 ÷ 8 = 64.
- **Learned:** start random → predict → measure error → backpropagation adjusts → repeat. Cat and dog end up close because they appear in similar sentences.
- **"the cat sat" → [3, 512]** = 3 words × 512 numbers. Every Transformer layer takes [n, 512] in and gives [n, 512] out; only the numbers change.

**Two limits of embeddings:**

| Problem | Example | Fixed by |
| --- | --- | --- |
| Meaning depends on **surrounding words** | river *bank* vs money *bank* | Self-attention |
| No **word order** | "dog bites man" vs "man bites dog" | Positional encoding |

> Embeddings give each word a starting meaning; attention turns it into a meaning based on context.

---

## 2. Seq2seq with RNNs

- **Seq2seq:** input sequence → output sequence (lengths and order can differ). "I love football" → "আমি ফুটবল ভালোবাসি".
- **RNN:** reads one word at a time, keeps a memory (**hidden state**). Like a loop with a running variable.
- **Encoder** compresses the input into hidden states (last one = **context vector**). **Decoder** generates output word by word from it, until `<END>`.

| Problem | What happens | Picture |
| --- | --- | --- |
| Bottleneck | Whole sentence in one fixed vector → long sentences lose info | A month of luggage in one small backpack |
| Forgetting | Early words fade over many steps (vanishing gradient) | Remembering "boy" 15 words later |
| Slow | h3 needs h2 needs h1 → no GPU parallelism | 50 blocking API calls in a row |

**Transformer idea:** remove the RNN, keep only attention → all words processed at once; any word reaches any word in one step. Trade-off: cost grows with n². It **kept** the encoder–decoder structure.

> ⚠️ Correction: Transformer needs positional encoding because it processes **all words at the same time**, not because of "one vector vs many". RNNs read in order, so order is built in.

---

## 3. Bahdanau Attention (2014)

Keep **all** encoder hidden states (h1, h2, h3) and let the decoder **look back** at them for each output word.

**Decoder inputs each step:** all hidden states (same every step) + its own memory + the previous word it wrote.

**3 steps before each output word:**
1. **Score** each hidden state against the decoder memory (later: dot product).
2. **Softmax** → percentages that add to 100% (attention weights).
3. **Weighted mix** → a custom context vector for this step.

| Step | Previous word | Attention (I / love / football) | Output |
| --- | --- | --- | --- |
| 1 | `<START>` | **90%** / 5% / 5% | আমি |
| 2 | আমি | 5% / 10% / **85%** | ফুটবল |
| 3 | ফুটবল | 5% / **88%** / 7% | ভালোবাসি |
| 4 | ভালোবাসি | — | `<END>` |

- The decoder loops over **output** words in **Bangla order**, not over input words.
- Order comes from the decoder's **learned Bangla grammar**; attention only says **where to look**.
- Fixed the bottleneck, but the encoder RNN was still slow.

**Database analogy:** a soft lookup returning a weighted mix of all rows.
**Query** = what the decoder looks for · **Keys** = what each word is about · **Values** = info that gets mixed → the paper's **Q, K, V**.

> The encoder says *what*; the decoder decides *in what order*; attention says *where to look*.

---

## 4. Four Tools Used Everywhere

| Tool | Job | In the paper |
| --- | --- | --- |
| Matrix multiplication | Does the work, fast and parallel | Q·Kᵀ, creating Q/K/V, feed-forward |
| Softmax | Scores → percentages | Attention weights, final word choice |
| Residual connection | Protects original info, helps deep training | "Add" in Add & Norm |
| Layer normalization | Keeps numbers stable | "Norm" in Add & Norm |

**Matrix multiplication** — many dot products at once. Shape rule: `[a, b] × [b, c] = [a, c]`, e.g. `[3, 512] × [512, 64] = [3, 64]`. `X × Xᵀ` gives every word-pair score in one step (= **Q·Kᵀ**). Like one batch query instead of N+1 queries.

**Softmax** — `e^x` for each number, then divide by the total.
`[0.5, 1.2, 3.3] → [5.1%, 10.3%, 84.5%]`. Handles negatives. Large scores get too extreme (`[10, 20, 30] → ~0%, ~0%, ~100%`) → the paper **divides by √d_k**.

**Residual connection** — `output = x + layer(x)`. The layer adds a small change (like a git patch). If it learns nothing, output = x. Requires the same shape → why everything stays [n, 512].

**Layer normalization** — rescale each word's vector to average 0, spread 1.
`[2, 4, 6, 8]` and `[200, 400, 600, 800]` both → `[−1.34, −0.45, 0.45, 1.34]`. Size removed, pattern kept (volume leveler). Paper: `LayerNorm(x + Sublayer(x))`.

**One encoder layer:**
```
x [n, 512] → Self-attention → + x → LayerNorm
           → Feed-forward   → + x → LayerNorm → [n, 512]
```

---

## 5. Attention Heads

- **Self-attention:** every word looks at all words in the **same** sentence and updates its vector.
- **One head** = one full run of score → softmax → weighted mix.
- **Problem with one head:** "The **animal** didn't cross the street because **it** was too **tired**." "it" needs both *animal* (what it refers to) and *tired* (what describes it). One set of percentages blurs them.
- **Solution:** 8 heads in parallel, each with its own W_Q, W_K, W_V, each learning a different relation. Like a code review team (security, performance, style).
- **Numbers:** each head uses `[n, 512] × [512, 64]` → 64 dims. Concatenate 8 × 64 = 512 → multiply by W_O → `[n, 512]`. Same cost as one big head.
- Nobody assigns roles; heads specialize through training.
- **Paper:** Section 3.2.2, Figure 2 (right), Table 3 rows (A): 1 head is clearly worse.

---







## The abstract in simple words

**The problem:** Before this paper, the best translation models used **RNNs** (or CNNs) with an **encoder and decoder**, and the best ones also added **attention** between them. (That's exactly the seq2seq + Bahdanau setup you just learned.)

**The new idea:** The authors built a new, simpler model called the **Transformer**. It uses **only attention**: no RNNs and no CNNs at all.

**Why it's better:**
1. **Better quality:** it translates more accurately.
2. **More parallel:** it can process all words at once on GPUs.
3. **Much faster to train.**

**The proof (results):**
- **English → German:** scored **28.4 BLEU**, beating the previous best by more than 2 points, even beating "ensembles" (several models combined).
- **English → French:** scored **41.8 BLEU**, a new record for a single model, after training for only **3.5 days on 8 GPUs**. That's a small part of what earlier top models cost to train.
- **A different task:** it also worked well on **English constituency parsing**, showing it isn't only good for translation.

## Words you might not know

| Word | Simple meaning |
|---|---|
| Sequence transduction | Turning one sequence into another, i.e. seq2seq (translation is an example) |
| Dispensing with | Removing, not using |
| Recurrence | The RNN way of working, one step after another |
| Convolutional (CNN) | Another type of network, mostly used for images, also tried for text |
| BLEU | A score (0–100) that measures how close a machine translation is to human translations. Higher is better; +2 is a big improvement |
| WMT 2014 | A standard translation competition dataset, so everyone compares fairly |
| Ensemble | Several models combined to vote together. Usually stronger than one model |
| State-of-the-art | The best result so far |
| Constituency parsing | Breaking a sentence into its grammar structure (which words form a phrase, e.g. "the red car") |
| Generalizes | Works well on other tasks too, not just the one it was built for |

## The abstract in one line

> **"We removed the RNN, used only attention, and got better translations, faster training, and a model that also works on other tasks."**

## Your Pass 1 check

From the abstract alone, you can already answer 4 of the 5 first-pass questions:

1. **Problem?** RNN-based translation models are slow and hard to parallelize.
2. **Main idea?** A model built only on attention: the Transformer.
3. **What's new?** No recurrence and no convolution at all.
4. **How do they prove it?** BLEU scores on two WMT translation tasks, plus training cost, plus a parsing task.
5. **Worth reading deeper?** That's for you to decide. (Hint: yes, this paper is the base of GPT, Claude and almost every modern LLM.)





## The introduction in simple words

The introduction has **4 small parts**. Here's each one.

### Part 1: RNNs were the best

RNNs, especially the improved versions **LSTM** and **GRU**, were the best methods for tasks like **language modeling** (predicting the next word) and **translation**. Many researchers kept working to make them even better.

### Part 2: But RNNs have a basic speed problem

An RNN works **one position at a time**. Each hidden state **h_t** is computed from the **previous hidden state h_(t−1)** plus the current word.

You already know this from our seq2seq lesson: h3 needs h2, and h2 needs h1. So the words of a sentence **can't be processed in parallel**.

This gets worse with **long sentences**. Long sentences use more GPU memory, so fewer sentences fit into one batch, and training gets even slower.

Other researchers tried **tricks** to make RNNs faster. These helped a bit, but the **core problem stayed**: the computation is still step by step.

### Part 3: Attention is great, but always paired with RNNs

**Attention** lets a model connect two words **no matter how far apart they are**. (Remember: in an RNN, "boy" fades after 15 steps. With attention, the decoder can look at "boy" directly.)

But in almost all existing models, attention was used **together with an RNN**, like Bahdanau attention. So the models were still slow.

### Part 4: Our solution, the Transformer

The Transformer **removes recurrence completely** and uses **only attention** to connect words across the input and output.

Results: **much more parallel**, and it reaches a **new best translation quality** after training for only **12 hours on 8 P100 GPUs**.

## One important idea: two kinds of parallelism

The phrase "precludes parallelization within training examples" is the key sentence of the introduction. There are two kinds of parallelism:

| Type | Meaning | Can an RNN do it? |
|---|---|---|
| **Across examples** (batching) | Process 32 sentences at the same time | ✅ Yes |
| **Within an example** | Process all words of **one sentence** at the same time | ❌ No, word by word |

So an RNN can only get speed from batching. But long sentences use more memory, so **fewer sentences fit in a batch**, and it loses that speed too. The Transformer can do **both** kinds of parallelism.

## Words you might not know

| Word | Simple meaning |
|---|---|
| [13], [7], [35] | Citation numbers: references to other papers. On a first pass, ignore them |
| Language modeling | Predicting the next word (what GPT does) |
| Symbol positions | Word positions in the sentence (word 1, word 2, ...) |
| Inherently sequential | Step by step by its basic nature; it can't be changed with small tricks |
| Precludes | Prevents, makes impossible |
| Batching | Processing many examples together at once |
| Factorization tricks / conditional computation | Methods others used to make RNNs faster. Not important for us |
| Integral part | An essential, core part |
| Dependencies | Connections between words (e.g. "it" depends on "animal") |
| Eschewing | Avoiding, not using (same meaning as "dispensing with" in the abstract) |
| Global dependencies | Connections between **any** words, near or far |
| P100 | An NVIDIA GPU model, powerful in 2017 |

## A small detail to notice

The abstract said **3.5 days**, and the introduction says **12 hours**. That's not a mistake. They're two different models: the **base model** trained in 12 hours, and the **big model** (for the English–French record) trained for 3.5 days. You'll see this in Section 5 and Table 3.

## The introduction in one line

> **"RNNs are good but slow because they work word by word. Attention is powerful but was always attached to an RNN. So we removed the RNN and used only attention."**




reading paper today again
# Lesson 0: Course Introduction

## Core Idea
- LLMs let developers build AI apps in **days or weeks instead of months**.
- Generative AI is a **general-purpose technology**, like electricity or deep learning, and is useful across many industries.
- There is high demand and a shortage of people who can build LLM applications.

## Main Framework
**Generative AI Project Lifecycle:**
Scope the problem → Select a model → Adapt/optimize → Deploy and integrate

## Key Terms
- **Transformer**: the architecture behind LLMs
- **In-context learning**: guiding the model with examples in the prompt
- **Prompt engineering**: designing inputs for better outputs
- **Inference parameters**: settings that control how text is generated
- **Instruction fine-tuning**: training a pre-trained model for specific tasks
- **PEFT**: efficient fine-tuning that updates only a small part of the model
- **RLHF**: aligning the model with human preferences, making it more helpful and less harmful



# Lesson 1: Week 1 Introduction

## What This Lecture Discusses
An overview of Week 1's two main topics:
1. **Transformer architecture**: how it works and why it became so successful.
2. **Generative AI Project Lifecycle**: how to plan and build a GenAI project.

## Core Idea
- **Transformers** come from the 2017 paper *"Attention Is All You Need"* and are still state of the art.
- **Why they took off:** attention runs **massively in parallel**, which suits GPUs and lets models scale.
- Transformers also power **vision** and other modalities, not just text.
- **Model size depends on the use case:**
  - **Large (100B+ parameters):** broad general knowledge across many tasks.
  - **Small (1–30B or under 1B):** can do very well on a **single focused task**.

## Main Framework
**Generative AI Project Lifecycle:** key decisions:
1. Use an **off-the-shelf foundation model** or **pre-train your own**?
2. **Fine-tune** it on your specific data?
3. Choose the **right model** and **right size** for the task.

## Key Terms
- **Self-attention**: lets the model understand relationships between words
- **Multi-headed self-attention**: several attention mechanisms in parallel, each learning different patterns
- **Foundation model**: a large pre-trained model used as a starting point
- **Pre-training**: training a model from scratch on huge amounts of data
- **Fine-tuning**: further training a pre-trained model on your own data
- **Parameters**: the model's learned weights, which indicate its size
- **Vision transformer**: a transformer applied to images









# Lesson 2: Generative AI & LLMs

## What This Lecture Discusses
- What generative AI and LLMs are, and how they learn
- Foundation models and their size (parameters)
- How we interact with LLMs: **prompts, context window, completions, inference**

## Core Idea
- **Generative AI** is a **subset of machine learning**. It creates content that mimics human ability by learning **statistical patterns** from massive amounts of human-generated data.
- LLMs are trained on **trillions of words** over weeks or months, using huge compute power.
- Large models show **emergent properties**: beyond language, they can break down complex tasks, reason, and solve problems.
- **More parameters means more "memory"**, which allows more sophisticated tasks.
- You can **use models as-is or fine-tune them**, so there's no need to train from scratch.
- **The new way of interacting:** instead of code with formal syntax, you give LLMs **natural-language instructions**.
- GenAI covers many modalities (image, video, audio, speech), but this course focuses on **text (natural language generation)**.
- The course lab model is **FLAN-T5**, an open-source model.

## Main Framework
**How an LLM interaction works:**
**Prompt** → passed to **LLM** → model **predicts next words** → **Completion**
*(This whole process is called **inference**.)*

## Key Terms
- **Generative AI**: ML that creates human-like content
- **Foundation / base model**: a large pre-trained model with billions of parameters
- **Parameters**: the model's "memory"; more parameters means more capability
- **Emergent properties**: abilities beyond basic language, such as reasoning and problem-solving
- **Prompt**: the text input you give the LLM
- **Context window**: the memory space available for the prompt (a few thousand words, varies by model)
- **Completion**: the model's output (original prompt + generated text)
- **Inference**: using the model to generate text




# Lesson 3: LLM Use Cases & Tasks

## What This Lecture Discusses
- LLMs can do much more than chat
- The different tasks LLMs can perform using **next-word prediction**
- How model **scale** affects language understanding

## Core Idea
- **Next-word prediction** is the base concept behind all LLM capabilities, not just chatbots.
- **LLMs can do many text tasks:**
  - **Essay writing** from a prompt
  - **Summarization**, for example summarizing a dialogue given in the prompt
  - **Translation** between languages (English → Spanish) or from **natural language to code** (e.g., "write Python to get the mean of each column")
  - **Information retrieval**, such as finding people and places in an article (**NER**)
  - **Augmenting LLMs** by connecting them to **external data sources and APIs**, which gives them knowledge they lack from pre-training and lets them interact with the real world *(Week 3)*
- **Bigger models (hundreds of millions → hundreds of billions of parameters) have better language understanding**, which helps them reason and solve tasks.
- **Smaller models can still do well** on specific, focused tasks when **fine-tuned** *(Week 2)*.
- The rapid progress of LLMs is mainly due to their **architecture (transformers)**.

## Main Framework
**Next-word prediction → many capabilities:**
Chat | Essay writing | Summarization | Translation | Code generation | Entity extraction | External data/API connection

**Model size trade-off:**
- **Large model** → broad, general language understanding
- **Small + fine-tuned model** → strong on a single focused task

## Key Terms
- **Next-word prediction**: the core mechanism behind LLM text generation
- **Summarization**: condensing text, such as a dialogue, into key points
- **Translation**: language to language, or natural language to code
- **Named Entity Recognition (NER)**: identifying people, places, and other entities in text; a type of word classification
- **Information retrieval**: extracting specific information from text
- **Augmenting LLMs**: connecting a model to external data or APIs to extend its knowledge and actions




# Lesson 4: Text Generation Before Transformers

## What This Lecture Discusses
- How older language models (**RNNs**) worked and why they were limited
- Why language is hard for machines (**ambiguity**)
- How the **transformer architecture (2017)** solved these problems

## Core Idea
- **Generative algorithms are not new.** Earlier models used **Recurrent Neural Networks (RNNs)**.
- **RNN limitations:**
  - Seeing only a few previous words leads to **poor predictions**.
  - To see more words, **compute and memory grow exponentially**.
  - Even when scaled, they **still couldn't see enough context** to predict well.
- **Good prediction needs context from the whole sentence, or even the whole document.**
- **Language is complex:**
  - **Homonyms**: one word, many meanings ("bank" as a river bank or a money bank)
  - **Syntactic ambiguity**: unclear sentence structure ("The teacher taught the student with the book." Who has the book?)
- **2017: "Attention Is All You Need"** (Google and University of Toronto) introduced the **transformer**, which changed everything.
- **Why transformers won:**
  1. **Scale efficiently** on multi-core **GPUs**
  2. **Process input in parallel**, which enables much **larger training datasets**
  3. **Learn to pay attention** to the **meaning of words**

## Main Framework
**RNN vs Transformer**

| | RNN | Transformer |
|---|---|---|
| Context | Only a few previous words | Whole sentence or document |
| Scaling | Compute/memory grow exponentially | Scales efficiently on GPUs |
| Processing | Sequential | Parallel |
| Understanding | Limited | Uses **attention** to understand meaning |

## Key Terms
- **RNN (Recurrent Neural Network)**: an older architecture that processes text sequentially; limited context
- **Next-word prediction**: predicting the next word from previous words
- **Homonym**: a word with multiple meanings
- **Syntactic ambiguity**: a sentence whose structure allows more than one meaning
- **Transformer**: the 2017 architecture behind modern LLMs
- **Attention**: the mechanism that lets the model focus on the meaning of and relationships between words
- **Parallel processing**: handling input data at the same time instead of one step after another










# Lesson 5: Transformer Architecture

## What This Lecture Discusses
- Why **self-attention** makes transformers powerful
- The high-level **structure of a transformer** (encoder + decoder)
- The **step-by-step flow of data** through a transformer: tokenization → embedding → positional encoding → self-attention → feed-forward → softmax

## Core Idea
- Transformers learn the **relevance and context of every word to every other word** in a sentence, not just neighboring words.
- **Attention weights** (learned during training) show how strongly each word relates to the others, no matter where they appear in the input.
- An **attention map** visualizes these weights. For example, "book" pays strong attention to "teacher" and "student".
- The transformer has two parts: an **encoder** and a **decoder**. They work together and share many similarities.
- **ML models work with numbers, not words**, so text must be converted to numbers first.
- **You must use the same tokenizer** for training and for generating text.
- **Embedding vectors encode meaning and context.** Words close together in embedding space are related, and the **angle** between vectors measures similarity.
- Since tokens are **processed in parallel**, **positional encoding** is needed to keep word order.
- **Multi-headed attention:** many attention heads (commonly **12–100**) learn **in parallel and independently**. Each learns a different aspect of language, such as people relationships, activities, or rhymes.
- **You don't decide** what each head learns. Heads start with **random weights** and learn on their own during training.
- The final output is a **probability for every token in the vocabulary**. The highest score is the most likely next token, but other selection methods exist *(covered later)*.

## Main Framework
**Transformer data flow (bottom → top):**
1. **Tokenization**: words → token IDs (numbers)
2. **Embedding layer**: token IDs → vectors (meaning and context)
3. **Positional encoding**: added to the embeddings to keep word order
4. **Self-attention layer (multi-headed)**: learns relationships between all tokens
5. **Feed-forward network**: processes each token's vector further (inside every layer)
6. **Linear layer → logits**: one raw score per vocabulary token
7. **Softmax layer**: converts logits to **probabilities** → predicts the next token

> **Note:** The lecture said the feed-forward network produces the logits. In reality, a **final linear layer** after the last decoder layer produces them.

## Where Each Step Happens

| Step | Encoder | Decoder |
|---|---|---|
| Embedding + positional encoding | ✅ | ✅ |
| Self-attention | ✅ | ✅ (**masked**) |
| Cross-attention | ❌ | ✅ (looks at the encoder output) |
| Feed-forward network | ✅ | ✅ |
| Linear + softmax | ❌ | ✅ (**only at the end**) |

- **Encoder** understands the input. It **runs once**, processing all tokens in parallel.
- **Decoder** generates the output. It **runs once per output token**, in a loop (**autoregressive**).

## Full Workflow: Input Text → Output Text
**Example:** "I love tea" → "J'aime le thé"

**Part 1: Prepare input**
1. **Tokenize:** "I love tea" → `[I] [love] [tea]` → token IDs
2. **Embed:** token IDs → vectors
3. **Add positional encoding:** keeps word order

**Part 2: Encoder (runs once)**

4. **Multi-headed self-attention:** each token attends to all other tokens
5. **Feed-forward network**
6. Steps 4–5 repeat **× N layers** → **encoder output** (one context vector per token, reused by the decoder)

**Part 3: Decoder (runs once per output token)**

7. **Input:** `<start>` + tokens generated so far → embedding + positional encoding
8. **Masked self-attention:** looks only at past tokens, never future ones
9. **Cross-attention:** looks at the encoder output
10. **Feed-forward network**
11. Steps 8–10 repeat **× N layers**

**Part 4: Predict**

12. **Linear layer → logits** (one score per vocabulary token)
13. **Softmax → probabilities**
14. **Select the next token** (highest probability or a sampling method)

**Part 5: Loop and output**

15. **Feed the token back** and repeat Steps 7–14: `<start>` → J' → aime → le → thé → `<end>`
16. **Detokenize:** token IDs → "J'aime le thé"

```
Text → Tokenize → Embed + Position
     → ENCODER [Self-Attention → FFN] × N   (once)
     → DECODER [Masked Self-Attn → Cross-Attn → FFN] × N   (per token)
     → Linear (logits) → Softmax → Pick token
     → Loop until <end> → Detokenize → Output Text
```

**Training vs inference:** during **training**, the decoder also runs in parallel because the correct output is known, and masking hides future tokens. The token-by-token loop happens only during **inference**.

## Single Model, Not Multiple Models
- **Embedding, encoder, decoder, and the final linear + softmax layers all belong to ONE model.** All their weights are **trained together** in one training process.
- The **tokenizer is not a neural network**. It's a rule-based tool plus a vocabulary file that **ships with the model** and must match it.
- Downloading a model (e.g., FLAN-T5 from Hugging Face) gives you **one set of model weights + tokenizer files**.

**Why the confusion about multiple models?**
- **Older NLP (Word2Vec):** embeddings were trained as a **separate model** and plugged in. Transformers learn embeddings **inside** the model.
- **RAG and vector search** use **separate embedding models** to create vectors for vector databases. That is a different use case from the embedding layer inside an LLM.

## Model Types: Not Every Model Has Both Encoder and Decoder

| Type | Has | Examples | Best for | Why |
|---|---|---|---|---|
| **Encoder-only** | Encoder | **BERT**, RoBERTa | Classification, sentiment analysis, NER | Sees the **whole input at once in both directions**, giving deep understanding; doesn't need to generate text |
| **Encoder-decoder** | Both | **T5, FLAN-T5**, BART | Translation, summarization | The input and output are **different sequences**: the encoder understands the input, and the decoder generates a new output |
| **Decoder-only** | Decoder | **GPT**, LLaMA, most modern LLMs | General text generation, chat | Predicts the **next token** from previous tokens; simple, **scales very well**, and handles almost any task as text generation |

> Most modern LLMs are **decoder-only**. With enough scale, next-token prediction alone can handle almost any task. The next lecture covers these model types in more detail.

## Key Terms
- **Self-attention**: learns how each word relates to every other word in the input
- **Attention weights**: learned values showing the importance of each word to the others
- **Attention map**: a diagram showing the attention weights between words
- **Encoder**: understands the input and runs once
- **Decoder**: generates output one token at a time
- **Tokenization**: converting words, or parts of words, into token IDs
- **Tokenizer**: performs tokenization; must be the same for training and generation; not a neural network
- **Embedding layer**: the first layer of the model; maps each token to a vector
- **Embedding vector**: the numeric representation of a token's meaning (512 dimensions in the original paper)
- **Word2Vec**: an earlier NLP algorithm that used separately trained embeddings
- **Positional encoding**: adds word-order information to the token vectors
- **Multi-headed self-attention**: multiple attention heads learning different language aspects in parallel
- **Masked self-attention**: decoder attention that cannot see future tokens
- **Cross-attention**: lets the decoder look at the encoder output
- **Feed-forward network**: a fully connected layer inside every encoder and decoder layer
- **Logits**: raw scores from the final linear layer, one per vocabulary token
- **Softmax**: normalizes logits into probabilities across the whole vocabulary
- **Autoregressive generation**: generating one token at a time, feeding each output back as input
- **Detokenization**: converting token IDs back into text
- **Encoder-only / decoder-only / encoder-decoder**: the three transformer model types
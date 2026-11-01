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
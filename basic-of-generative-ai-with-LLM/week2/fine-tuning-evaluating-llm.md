# Week 2 

# Lesson 1: Intro: Fine-tuning LLMs

## What the lecture discusses
An overview of Week 2: instruction fine-tuning, the problem of catastrophic forgetting, and parameter-efficient fine-tuning (PEFT), including LoRA. It also covers when developers move from prompting to fine-tuning.

## Core idea
A pre-trained base model knows a lot about the world, but it only learned to predict the next word, which is not the same as following instructions. Fine-tuning on a much smaller instruction dataset changes its behavior so it responds helpfully to prompts. Full fine-tuning is expensive, so PEFT methods give similar results at a fraction of the compute and memory.

## Main framework to remember
1. **Start with prompting.** Sometimes it is good enough.
2. **If prompting hits a performance ceiling, fine-tune.** There are two kinds worth doing:
   - **Instruction fine-tuning:** teaches the model to follow instructions in general.
   - **Task- or domain-specific fine-tuning:** a developer adapts the model to their own application.
3. **Prefer PEFT over full fine-tuning.** Full fine-tuning updates every parameter, so it is costly to train, store, and deploy. PEFT freezes the original weights and trains only a small number of added parameters.
4. **Weigh the model size.** A giant general model has many benefits, but a smaller fine-tuned model costs less and can run in your own environment if you need control over your data.

## Key terms
- **Base model:** the initially pre-trained model, with general knowledge but no instruction-following skill.
- **Instruction fine-tuning:** training on prompt–response examples so the model learns to follow instructions.
- **Catastrophic forgetting:** after fine-tuning on new data, the model loses much of what it knew before. You reduce it by fine-tuning across a broad range of instruction types, not just your one task.
- **Full fine-tuning:** updating all model weights, which is compute- and memory-expensive and gives a full-size model per task.
- **PEFT (parameter-efficient fine-tuning):** a set of methods that freeze the original weights and add small adaptive layers, giving a much smaller memory footprint and making it practical to train for multiple tasks.
- **LoRA:** a popular PEFT technique that uses low-rank matrices instead of updating the full weights, giving good performance with minimal compute and memory.




# Lesson 2: Instruction Fine-tuning

## What the lecture discusses
How to improve an existing model for your use case by fine-tuning it with instruction prompts: why in-context examples are not always enough, what instruction fine-tuning is, how to prepare the dataset, and how the training and evaluation loop works.

## Core idea
Fine-tuning is **supervised learning** on labelled **prompt–completion pairs**, each containing an instruction. It updates the model's weights so it gets better at generating completions for those tasks. The result is a new version of the base model, often called an **instruct model**.

## Main framework to remember

**Why not just use one-shot or few-shot prompting?**
- It doesn't always work for smaller models, even with five or six examples.
- Examples take up space in the context window, leaving less room for other useful information.

**Pre-training vs fine-tuning**

| | Pre-training | Fine-tuning |
|---|---|---|
| Learning type | Self-supervised | Supervised |
| Data | Vast amounts of unstructured text | Labelled prompt–completion pairs |

**Steps of instruction fine-tuning**
1. **Prepare the data.** Most public datasets are not formatted as instructions, so use prompt-template libraries to convert them (e.g. Amazon reviews → "Predict the associated rating: {review_body}").
2. **Split the data** into training, validation, and test sets.
3. **Pass training prompts to the LLM**, which generates completions.
4. **Compare** each completion with the label from the training data.
5. **Calculate the loss** with cross-entropy between the two token probability distributions.
6. **Update the weights** with backpropagation.
7. **Repeat** over many batches and several epochs.
8. **Evaluate:** the validation set gives validation accuracy during training; the test set gives the final test accuracy.

## Key terms
- **Instruction fine-tuning:** training with examples that show how the model should respond to a specific instruction (e.g. "Summarise the following text", "Translate this sentence").
- **Prompt–completion pair:** one labelled training example, made of the prompt with its instruction and the expected response.
- **Full fine-tuning:** fine-tuning where all the model's weights are updated. Like pre-training, it needs enough memory and compute for the gradients, optimisers, and other components.
- **Prompt-template library:** a collection of templates that turn existing datasets into instruction datasets for different tasks (classification, text generation, summarisation).
- **Cross-entropy loss:** the function used to measure the difference between the model's output token distribution and the training label's.
- **Instruct model:** the fine-tuned version of the base model.




# Lesson 3: Fine-tuning on a Single Task

## What the lecture discusses
Fine-tuning a pre-trained model for just one task, the risk of catastrophic forgetting that comes with it, and the options for avoiding it.

## Core idea
You can fine-tune a model on a single task with relatively few examples. Full fine-tuning changes the original weights, though, so the model can get better at the new task while losing its ability to do other tasks.

## Main framework to remember

**Single-task fine-tuning**
- About **500–1,000 examples** often give good performance. Pre-training used billions of pieces of text.
- Example: fine-tuning only for summarization.

**Downside: catastrophic forgetting**
- It happens because full fine-tuning modifies the original LLM weights.
- Example: after fine-tuning for sentiment analysis, the model can no longer do named entity recognition. It used to find "Charlie" as the cat's name, but now it confuses the entity and behaves as if it's doing the new task.

**How to deal with it (3 options)**
1. **Check whether it matters.** If you only need reliable performance on that one task, losing other skills may not be a problem.
2. **Multi-task fine-tuning.** Fine-tune on many tasks at once so the model keeps its general abilities. It needs about **50,000–100,000 examples**, so it costs more data and compute.
3. **PEFT (parameter-efficient fine-tuning).** Keep the original weights frozen and train only small task-specific adapter layers and parameters. This is more robust to forgetting because most pre-trained weights stay unchanged.

## Key terms
- **Single-task fine-tuning:** fine-tuning a model to improve on only one task.
- **Catastrophic forgetting:** performance on other tasks drops after full fine-tuning on a new task.
- **Multi-task fine-tuning:** fine-tuning on examples from many tasks at once to keep the model's general abilities.
- **PEFT:** a set of techniques that preserve the original weights and train only a small number of new parameters.
- **Adapter layers:** the small task-specific layers that PEFT trains.





# Lesson 4: Multi-task Instruction Fine-tuning

## What the lecture discusses
How multi-task fine-tuning works, the FLAN family of models (especially FLAN-T5), the SAMSum dataset and its prompt template, and how to fine-tune FLAN-T5 further for a specific domain with DialogSum.

## Core idea
Training on a mixed dataset that covers many tasks improves the model on all of them at the same time, which avoids catastrophic forgetting. Even a strong general instruct model like FLAN-T5 can then be fine-tuned again on **domain-specific data** so it does better on your own use case.

## Main framework to remember

**Multi-task fine-tuning**
- The dataset mixes many tasks, such as summarization, review rating, code translation, and entity recognition.
- Over many epochs, the losses across all examples update the weights, giving an instruction-tuned model that is good at many tasks.
- **Drawback:** it needs a lot of data, around **50,000–100,000 examples**.
- **Benefit:** the models are very capable and work well where good performance on many tasks is needed.

**FLAN models**
- FLAN = **Fine-tuned LAnguage Net**, a specific set of instructions used to fine-tune different models.
- FLAN fine-tuning is the last training step, so the paper calls it the "dessert" after the "main course" of pre-training.
- **FLAN-T5** is the FLAN version of T5, and **FLAN-PaLM** is the FLAN version of PaLM.
- FLAN-T5 is fine-tuned on **473 datasets across 146 task categories**, which makes it a good general-purpose instruct model.

**SAMSum dataset (used in FLAN-T5)**
- About **16,000 messenger-style conversations with summaries**, written by linguists.
- It trains the model to summarize dialogue, and it's part of the Muffin collection.
- Its prompt template uses **several phrasings of the same instruction** ("Briefly summarize that dialogue", "What is a summary of this dialogue?", and so on). This helps the model generalize.
- The dialogue goes into the template and the summary is the label.

**Domain-specific fine-tuning (example: customer service)**
- SAMSum is mostly casual chat between friends, so it doesn't match customer support language well.
- **DialogSum** has **13,000+ support-chat dialogues with summaries**, and FLAN-T5 has not seen it before.
- **Before fine-tuning**, FLAN-T5's summary of a hotel check-in chat was okay but missed key details and **invented information** (the hotel name and city).
- **After fine-tuning on DialogSum**, the summary was close to the human one: nothing made up, all important details kept, and both people named.
- **In practice**, your company's own internal data (e.g. real support chats) gives the best results.

## Key terms
- **Multi-task fine-tuning:** fine-tuning on examples from many tasks at once.
- **FLAN:** a set of instructions used for multi-task fine-tuning of models (FLAN-T5, FLAN-PaLM).
- **SAMSum:** a dialogue summarization dataset of casual messenger-style chats.
- **DialogSum:** a dialogue summarization dataset of support chats, used in this week's lab.
- **Prompt template with varied instructions:** different wordings of the same task to help the model generalize.
- **Hallucination (fabricated info):** the model adding details that aren't in the input. Here, domain fine-tuning removed it.









# Lesson 5: Scaling Instruct Models (FLAN paper)

## The one-line answer
In this paper, "scaling" doesn't mean scaling a server. It means **making instruction fine-tuning bigger** and checking whether the model gets smarter. They went bigger in **3 ways**, and all 3 helped: (1) more tasks, (2) a bigger model, (3) chain-of-thought data.

## First: Dataset vs Task vs Category

| Term | Meaning | Example |
|---|---|---|
| **Dataset** | Raw collection of examples | Amazon Reviews, SAMSum |
| **Task** | A specific job made from a dataset by adding an instruction | "Predict the star rating of this review" |
| **Category** | A group of similar tasks | Summarization, classification, translation |

**Key point:** one dataset can make **many tasks**. For example, Amazon Reviews can become:
- "Predict the rating" (classification)
- "Generate a 5-star review" (text generation)
- "Describe this review in one sentence" (summarization)

That's why the paper's training mix has **473 datasets → 1,836 tasks → 146 categories**.

**School analogy:** dataset = textbook, task = type of exercise, category = subject.

## The 3 ways they scaled it

**1. More tasks (up to 1,836)**
- They collected **more datasets**, turned them into **more tasks** with different instructions, and covered **many categories**.
- Analogy: a student who practices math, English, physics, and history does better on a surprise new subject than one who only practiced math.

**2. A bigger model (up to 540B parameters)**
- The **data stays the same**. Only the model gets bigger.
- They fine-tuned PaLM 540B and called the result **Flan-PaLM**.
- Finding: performance improved with both a larger model and more tasks.

**3. Chain-of-Thought (CoT) data added to training**
- They **added new CoT tasks** whose answers show step-by-step reasoning, not just the final answer. It's like adding "show your working" homework.
- Example:
  - Question: The cafeteria had 23 apples, used 20, then bought 6. How many now?
  - Normal answer: "9"
  - CoT answer: "23 − 20 = 3. They bought 6 more, so 3 + 6 = 9."
- Why it matters: older instruction fine-tuning made reasoning worse. Adding CoT data improved performance on all evaluations.

```
Datasets (473) → add instructions → Tasks (1,836) → grouped → Categories (146)

Scaling 1 → more datasets, tasks, and categories
Scaling 2 → same tasks, bigger model
Scaling 3 → add CoT tasks (step-by-step answers)
```

## Where the training data came from
- **Muffin:** dialogue tasks (like SAMSum) and program synthesis (writing code)
- **T0** and **Natural Instructions v2:** parts of other big task collections
- **New CoT tasks:** step-by-step reasoning examples

## What "held-out tasks" means
Some tasks were **kept hidden during training** and only used for testing.
- Analogy: a teacher keeps some exam questions secret. If the student still answers them well, they actually *learned* and didn't just memorize.
- This shows **generalization**: doing well on tasks the model never saw.

## Results
- **Better performance:** Flan-PaLM 540B beat PaLM 540B by **+9.4% on average** and reached **75.2% on MMLU** (state-of-the-art at the time).
- **Easier to use:** it can reason zero-shot, with no examples needed in the prompt.
- **Small models benefit too:** Flan-T5 performs strongly even against much larger models like PaLM 62B.

## Key terms
- **Dataset:** raw data examples.
- **Task:** a dataset combined with an instruction (a job for the model).
- **Category:** a group of similar tasks.
- **Scaling instruction fine-tuning:** more tasks, a bigger model, and CoT data.
- **Flan-PaLM:** PaLM 540B after FLAN instruction fine-tuning.
- **Chain-of-Thought (CoT):** answers that show reasoning steps.
- **Held-out tasks:** tasks hidden during training and used to test generalization.
- **Zero-shot reasoning:** solving a problem with no examples in the prompt.
- **MMLU:** a benchmark of exam-style questions across many subjects.

## How to remember it
> **More tasks + bigger model + step-by-step examples = a smarter model that also handles tasks it has never seen.**








# Lesson 6: LLM Evaluation Metrics: ROUGE and BLEU

## What the lecture discusses
How to measure whether a model, or a fine-tuned version of it, is performing well. It introduces two common metrics, **ROUGE** (for summarization) and **BLEU** (for translation), shows how they're calculated, and covers their weaknesses.

## Core idea
Traditional ML can use **accuracy** because its outputs are deterministic and either right or wrong. LLM outputs are **non-deterministic and language-based**, so evaluation is harder:
- "Mike really loves drinking tea" ≈ "Mike adores sipping tea". The words are different but the meaning is the same.
- "Mike does not drink coffee" vs "Mike does drink coffee". One word is different but the meaning is opposite.

We need an **automated, structured way** to compare model output with a human-written reference.

## Main framework to remember

**Basic terms**
- **Unigram** = 1 word, **bigram** = 2 words, **n-gram** = n words
- **Recall** = matches ÷ words in the **reference**
- **Precision** = matches ÷ words in the **generated output**
- **F1** = the harmonic mean of recall and precision = 2 × (P × R) ÷ (P + R)

**ROUGE example**
Reference: *"It is cold outside"* (4 words)
Output: *"It is very cold outside"* (5 words)

| Metric | What it matches | Recall | Precision | F1 |
|---|---|---|---|---|
| **ROUGE-1** | single words (4 matches) | 4/4 = 1.0 | 4/5 = 0.8 | 0.89 |
| **ROUGE-2** | word pairs (2 matches: "it is", "cold outside") | 2/3 = 0.67 | 2/4 = 0.5 | 0.57 |
| **ROUGE-L** | longest common subsequence (length 2) | 2/4 = 0.5 | 2/5 = 0.4 | 0.44 |

- **ROUGE-1** ignores word order.
- **ROUGE-2** captures a little word order, so its scores are lower and drop further for longer sentences.
- **ROUGE-L** uses the longest common sequence of words instead of a fixed n-gram size.

**ROUGE problems and fixes**

| Problem | Example | Result |
|---|---|---|
| Ignores meaning | "It is **not** cold outside" | Same score as the correct sentence |
| Repeated words | "cold cold cold cold" | Precision = 4/4 = 1.0 (perfect, but bad output) |
| Fix: **clipping** | Limit matches to how often the word appears in the reference ("cold" appears once) | Modified precision = 1/4 = 0.25 |
| Wrong word order | "outside cold it is" | Still a perfect score, even with clipping |

So the best n-gram size depends on the sentence, its length, and your use case.

**BLEU score**
- It's the **average precision across several n-gram sizes** (1-gram, 2-gram, 3-gram, and so on).
- It checks how many n-grams in the machine translation match the reference translation.
- Example:
  - Reference: "I am very happy to say that I am drinking a warm cup of tea."
  - Candidate: "I am very happy that I am drinking a cup of tea." BLEU = **0.495**
  - The closer the output is to the reference, the closer the score gets to **1**.
- Libraries like **Hugging Face** calculate both ROUGE and BLEU easily. This week's lab uses ROUGE to compare the model before and after fine-tuning.

**When to use what**
- **ROUGE:** summarization tasks
- **BLEU:** translation tasks
- Both are simple and cheap, so they're good for **quick checks while iterating**. **Don't use them alone for the final evaluation.**
- Only compare ROUGE scores **from the same task**. Scores from different tasks aren't comparable.
- For overall model evaluation, use **benchmarks** made by researchers (next video).

## Key terms
- **ROUGE:** Recall-Oriented Understudy for Gisting Evaluation. It compares a generated summary with a human reference summary.
- **BLEU:** Bilingual Evaluation Understudy. It compares a machine translation with a human reference translation.
- **ROUGE-1 / ROUGE-2:** ROUGE using unigrams or bigrams.
- **ROUGE-L:** ROUGE using the longest common subsequence (LCS).
- **Clipping:** limits a word's matches to the number of times it appears in the reference.
- **Non-deterministic:** the same input can produce different outputs.

**How to remember it:**
> **ROUGE = Recall = summaries. BLEU = translations. Both are quick checks, not final judges.**









# Lesson 7: LLM Benchmarks

## What the lecture discusses
Why simple metrics like ROUGE and BLEU aren't enough, how to choose evaluation datasets, and the main benchmarks used to measure and compare LLMs: GLUE, SuperGLUE, MMLU, BIG-bench, and HELM.

## Core idea
To evaluate an LLM **holistically**, use **benchmarks**: ready-made datasets and tests that researchers designed to check specific skills and risks. Test the model on data it **hasn't seen during training**, so you measure its real ability and not memorization.

## Main framework to remember

**How to choose an evaluation dataset**
- Pick datasets that **isolate specific skills**, such as reasoning or common sense.
- Include datasets that check **risks**, such as disinformation or copyright infringement.
- Make sure the model **didn't see the data in training**.

**The benchmarks**

| Benchmark | Year | What it tests | Remember |
|---|---|---|---|
| **GLUE** (General Language Understanding Evaluation) | 2018 | Basic language tasks such as sentiment analysis and question answering | Encourages models that generalize across tasks |
| **SuperGLUE** | 2019 | Harder tasks such as multi-sentence reasoning and reading comprehension | Successor to GLUE that fixes its limits |
| **MMLU** (Massive Multitask Language Understanding) | — | World knowledge and problem solving in elementary math, US history, computer science, law, and more | Made for modern LLMs and goes beyond language understanding |
| **BIG-bench** | — | 204 tasks: linguistics, math, biology, physics, common sense, social bias, software development, and more | Comes in **3 sizes** to keep inference costs manageable |
| **HELM** (Holistic Evaluation of Language Models) | — | **7 metrics across 16 core scenarios**, including **fairness, bias, and toxicity** | Goes beyond accuracy, is a "living" benchmark that keeps evolving, and improves transparency |

GLUE and SuperGLUE have **leaderboards** for comparing models. HELM has a **results page** where you can find models that suit your project.

**The "arms race"**
- As models get bigger, they start to **match human scores** on benchmarks like SuperGLUE.
- In general use, though, they still **aren't at human level**.
- So researchers keep building **harder benchmarks** (MMLU, BIG-bench) to keep up with new model abilities.

## Key terms
- **Benchmark:** a standard set of datasets and tasks used to measure and compare models.
- **Holistic evaluation:** judging a model on many skills and risks, not just one score.
- **Leaderboard:** a public ranking of models on a benchmark.
- **Unseen evaluation data:** test data the model didn't see in training, which gives an honest measurement.
- **Fairness, bias, toxicity:** safety-related metrics that HELM measures, which matter more as LLMs sound more human.
- **Inference cost:** the compute cost of running the model on all the benchmark tasks. This is why BIG-bench comes in 3 sizes.

**How to remember it:**
> **ROUGE/BLEU = quick checks. Benchmarks = full exams.**
> GLUE → SuperGLUE (language), MMLU → BIG-bench (knowledge and reasoning), HELM (accuracy + fairness + bias + toxicity).











# Lesson 8: Parameter-Efficient Fine-Tuning (PEFT): Introduction

## What the lecture discusses
Why full fine-tuning is so memory-hungry, how PEFT solves this by training only a small number of parameters, and the 3 main classes of PEFT methods: selective, reparameterization, and additive.

## Core idea
**Full fine-tuning** updates **every** weight, and it needs a lot of memory for training components beyond the model itself. **PEFT** keeps most or all of the original weights **frozen** and trains only a **small set** of parameters. That makes training cheaper (often one GPU is enough), reduces catastrophic forgetting, and makes it easy to adapt one model to many tasks.

## Main framework to remember

**Why full fine-tuning is expensive**
Memory is needed for much more than the model weights:
- Model weights (hundreds of GB for the largest models)
- Optimizer states
- Gradients
- Forward activations
- Temporary memory

These extra components can be **many times larger than the model**, which is too much for consumer hardware.

**Full fine-tuning vs PEFT**

| | Full fine-tuning | PEFT |
|---|---|---|
| Weights updated | All of them | A small subset or new parameters only |
| Trained parameters | 100% | Much smaller (sometimes just 15–20% of the original weights) |
| Hardware | Large compute | Often a **single GPU** |
| Catastrophic forgetting | More likely | **Less likely** (the original model is barely changed) |
| Storage for multiple tasks | A **full-size copy per task** (expensive) | **Small task weights** (as small as **MBs**) plus one shared original model |

**How PEFT handles multiple tasks**
- Train a small set of PEFT weights **for each task**.
- At inference, **combine** them with the original LLM weights.
- **Swap** the PEFT weights to switch tasks, using the same base model each time.

Example: one base LLM + a summarization adapter (MBs) + a translation adapter (MBs) + a Q&A adapter (MBs), instead of 3 full copies of the model.

**PEFT trade-offs**
Every method balances: parameter efficiency, memory efficiency, training speed, model quality, and inference cost.

**3 main classes of PEFT methods**

| Class | How it works | Example | Note |
|---|---|---|---|
| **1. Selective** | Fine-tune only a **subset of the original parameters** (certain layers, components, or parameter types) | — | Mixed performance and big trade-offs, so it's **not the course focus** |
| **2. Reparameterization** | Work with the original weights but train **new low-rank transformations** of them, which means far fewer parameters | **LoRA** | Next video |
| **3. Additive** | Keep **all original weights frozen** and **add new trainable components** | Adapters, soft prompts | See below |

**The 2 types of additive methods**
- **Adapters:** add new trainable **layers** inside the model, usually in the encoder or decoder after the attention or feed-forward layers.
- **Soft prompts:** keep the model architecture fixed and change the **input** instead, by adding trainable parameters to the prompt embeddings or retraining the embedding weights. The course covers **prompt tuning**, a soft prompt method, in this lesson.

## Key terms
- **PEFT (Parameter-Efficient Fine-Tuning):** fine-tuning that trains only a small number of parameters.
- **Frozen weights:** original model weights that are not updated during training.
- **Optimizer states, gradients, activations:** the extra memory needed during training, often bigger than the model itself.
- **Selective methods:** train a chosen subset of the existing parameters.
- **Reparameterization methods:** train low-rank versions of the weights (LoRA).
- **Additive methods:** add new trainable parts (adapters or soft prompts).
- **Adapter layers:** small new layers added inside the model.
- **Soft prompts / prompt tuning:** trainable parameters added to the input embeddings.

**How to remember it:**
> **Full fine-tuning = retrain the whole model, with a full copy per task. PEFT = freeze the model and train small add-ons you can swap per task.**
> The 3 classes: **Selective** (pick some weights), **Reparameterization** (LoRA), **Additive** (adapters and soft prompts).






# Lesson 9: LoRA (Low-Rank Adaptation)

## What the lecture discusses
How LoRA works inside the transformer, a worked example of how many parameters it saves, how to switch tasks with LoRA, how LoRA performs compared with full fine-tuning (using ROUGE), and how to choose the LoRA rank.

## Core idea
LoRA **freezes all the original weights** and adds **two small matrices (A and B)** next to a weight matrix. Only A and B are trained. Their product **B × A** has the **same shape** as the original weight matrix, so it can be **added to the original weights** for inference. You get similar performance to full fine-tuning while training far fewer parameters.

## Main framework to remember

**How LoRA works (step by step)**
1. **Freeze** the original LLM weights (W).
2. **Inject 2 small rank decomposition matrices**, A and B, alongside W.
3. **Train only A and B** with normal supervised learning.
4. For inference, **multiply B × A**, which gives a matrix the same size as W.
5. **Add** it to the original weights: **W_new = W + B × A**.
6. **Replace** W in the model with W_new.

The model keeps the **same number of parameters**, so there is **little to no extra inference latency**.

**Where to apply LoRA**
- Usually only to the **self-attention layers**, which is often enough for good results.
- It can also go on the feed-forward layers, but most LLM parameters are in attention, so that's where the biggest savings are.

**Worked example (from "Attention Is All You Need")**

| | Shape | Trainable parameters |
|---|---|---|
| Original weight matrix W | 512 × 64 | **32,768** |
| LoRA matrix A (rank = 8) | 8 × 64 | 512 |
| LoRA matrix B (rank = 8) | 512 × 8 | 4,096 |
| **LoRA total** | — | **4,608** |

**Result: 4,608 instead of 32,768 trainable parameters, an 86% reduction.**
Check: B × A = (512 × 8) × (8 × 64) = **512 × 64**, the same shape as W.

Because of this, LoRA can often run on a **single GPU** with no need for a distributed GPU cluster.

**Switching tasks with LoRA**
- Train **one small pair of A and B per task** (task A, task B, and so on).
- For task A: compute B × A, add it to the frozen W, and run inference.
- For task B: take task B's matrices, compute their product, add it to W, and update the model again.
- LoRA matrices need **very little storage**, so there's **no need to store many full-size LLM copies**.

**Performance (FLAN-T5, dialogue summarization, ROUGE-1)**

| Model | ROUGE-1 gain over base | Compute |
|---|---|---|
| FLAN-T5 base | baseline (fairly low) | — |
| Full fine-tuning | **+0.19** | High (all weights trained) |
| LoRA fine-tuning | **+0.17** | **Much lower** (few parameters trained) |

LoRA is **only slightly worse** than full fine-tuning but uses far less compute, so it's usually a **worthwhile trade-off**.

**How to choose the rank**
- **Smaller rank** means fewer trainable parameters and more compute savings, but it might hurt performance.
- In the original LoRA paper (Microsoft), the loss **plateaued for ranks above 16**. Bigger matrices didn't help.
- **Good range: rank 4 to 32.**
- Choosing the best rank is still **an active area of research**.

## Key terms
- **LoRA (Low-Rank Adaptation):** a reparameterization PEFT method that trains small low-rank matrices instead of the full weights.
- **Rank decomposition matrices (A and B):** the two small matrices whose product B × A matches the shape of the original weight matrix.
- **Rank (r):** the small shared dimension of A and B (for example, 8). It controls how many parameters are trained.
- **Frozen weights:** the original LLM weights, which are not updated.
- **Inference latency:** the time to produce an output. LoRA adds little to none because the parameter count stays the same.
- **Task switching:** swapping in a different pair of LoRA matrices for each task on the same base model.

**How to remember it:**
> **Freeze W, train small A and B, then add B × A back to W.**
> 86% fewer parameters, ROUGE almost as good as full fine-tuning (+0.17 vs +0.19), and rank 4 to 32 works well.






# Lesson 10: Prompt Tuning and Week 2 Recap

## What the lecture discusses
Prompt tuning, an additive PEFT method that trains extra "soft prompt" tokens instead of changing the model weights. It covers how prompt tuning differs from prompt engineering, how well it performs, and its interpretability. It ends with a recap of Week 2 and a mention of QLoRA.

## Core idea
Prompt tuning **freezes the whole LLM** and adds a small set of **trainable virtual tokens (a soft prompt)** in front of the input embeddings. Supervised learning finds the best values for these tokens for a task. Only a tiny number of parameters are trained, and the same LLM can handle many tasks by **swapping soft prompts**.

## Main framework to remember

**Prompt engineering vs prompt tuning**

| | Prompt engineering | Prompt tuning |
|---|---|---|
| What changes | The **words** of your prompt (manually) | **Trainable virtual tokens** added to the prompt (learned) |
| How | Try different phrases, add one-shot or few-shot examples | Supervised learning finds the best token values |
| Training | None | Yes, but only the soft prompt |
| Limits | Manual effort, uses up the context window, may still not perform well enough | Needs training, and the learned tokens are hard to interpret |

**How prompt tuning works**
1. The input text is turned into embedding vectors (the normal **"hard" tokens**).
2. A **soft prompt** of **20–100 virtual tokens** is **prepended** to them.
3. Each soft prompt vector has the **same length** as a normal token embedding.
4. The **LLM weights stay frozen**, and only the **soft prompt embeddings are updated** during training.

**Hard tokens vs soft tokens**
- **Hard tokens:** real words, each fixed at one location in the embedding space.
- **Soft tokens:** virtual tokens that can take **any value** in the continuous embedding space, so they aren't real words.

**Full fine-tuning vs prompt tuning**
- **Full fine-tuning:** updates the LLM weights, which means millions to billions of parameters.
- **Prompt tuning:** the LLM is frozen and only the soft prompt is updated, a **very small number of parameters**.

**Multiple tasks**
- Train **one soft prompt per task**.
- For inference, **prepend** that task's soft prompt to the input.
- To switch tasks, **change the soft prompt**. The **same LLM** is used for every task.
- Soft prompts are **very small on disk**, so this is extremely efficient and flexible.

**Performance (Lester et al., Google, measured on SuperGLUE)**

| Method | Result |
|---|---|
| Full fine-tuning (single task) | Best for small models |
| Multi-task fine-tuning | Strong |
| **Prompt tuning** | **Weaker for small models**, but **improves as model size grows** |
| Prompt engineering only | Lowest |

**Key finding:** at around **10 billion parameters**, prompt tuning becomes **as effective as full fine-tuning** and much better than prompt engineering alone.

**Interpretability issue**
- Soft tokens **don't match any real word** in the vocabulary.
- But their **nearest-neighbor words** form **tight semantic clusters** related to the task. So the soft prompts learn **word-like meanings**.

## Week 2 recap
1. **Instruction fine-tuning** adapts a foundation model with prompt–completion examples. A few hundred examples can be enough for a specific task.
2. **Prompt templates and datasets** were used to train FLAN-T5.
3. **Evaluation:** metrics (ROUGE, BLEU) and benchmarks (GLUE, SuperGLUE, MMLU, BIG-bench, HELM).
4. **PEFT** reduces compute and memory. The two methods covered:
   - **LoRA:** trains low-rank matrices and updates the weights efficiently. It's **the most widely used in practice** because it performs close to full fine-tuning.
   - **Prompt tuning:** trains soft prompt tokens and leaves the model untouched.
5. **QLoRA = LoRA + quantization** (from Week 1), which **reduces memory even further**.

## Key terms
- **Prompt tuning:** an additive PEFT method that trains soft prompt tokens while the LLM stays frozen.
- **Soft prompt:** the set of trainable virtual tokens prepended to the input embeddings.
- **Virtual tokens:** learned vectors in the embedding space that aren't real words.
- **Hard tokens:** normal word tokens with fixed embedding positions.
- **Prepend:** add to the front of the input.
- **Semantic clusters:** groups of words with similar meaning near the soft tokens.
- **QLoRA:** LoRA combined with quantization for lower memory use.

**How to remember it:**
> **Prompt engineering = you change the words. Prompt tuning = the model learns extra virtual tokens.**
> LLM frozen, 20–100 soft tokens, one soft prompt per task, as good as full fine-tuning at around 10B parameters.
> **Week 2 summary:** Instruction fine-tuning → Evaluate (ROUGE/BLEU and benchmarks) → Make it cheap with PEFT (LoRA, prompt tuning, QLoRA).
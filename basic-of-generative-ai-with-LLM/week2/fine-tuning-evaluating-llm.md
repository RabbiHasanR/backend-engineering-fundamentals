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



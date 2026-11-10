# =============================================================================
# LAB 1: Dialogue Summarization with FLAN-T5
# Course: Generative AI with Large Language Models (Week 1)
#
# GOAL:
#   Summarize conversations with the FLAN-T5 model and see how
#   1) prompt engineering (zero-shot, one-shot, few-shot) and
#   2) generation configuration (greedy, temperature, top-k, top-p)
#   change the model's output.
#
# HOW TO RUN IN GOOGLE COLAB:
#   - Runtime -> Change runtime type -> T4 GPU (optional, but faster)
#   - Copy each "# %%" section into its own Colab cell and run them in order.
#     (Colab also understands "# %%" markers if you open this file in some editors.)
#
# NOTE ON EXPECTED OUTPUTS:
#   The outputs shown in comments are EXAMPLES. Exact numbers and model text
#   may differ slightly because of library versions and random sampling.
# =============================================================================


# %% ---------------------------------------------------------------------------
# STEP 1: Install libraries
# -----------------------------------------------------------------------------
# - transformers : Hugging Face library for models + tokenizers
# - datasets     : Hugging Face library to load public datasets
# - PyTorch (torch) is already installed in Colab
#
# In Colab, run this line WITH the "!" at the start (it runs a shell command):
#
#   !pip install -q transformers datasets
#
# (-q = quiet mode, shows less install text)
#
# EXPECTED OUTPUT:
#   A few install lines, or nothing if the packages are already installed.


# %% ---------------------------------------------------------------------------
# STEP 2: Import libraries and choose the device (GPU or CPU)
# -----------------------------------------------------------------------------
import torch                                   # PyTorch: runs the model math
from datasets import load_dataset              # loads public datasets from Hugging Face
from transformers import (
    AutoModelForSeq2SeqLM,   # loads an encoder-decoder model (like FLAN-T5)
    AutoTokenizer,           # loads the matching tokenizer
    GenerationConfig,        # holds generation settings (max tokens, temperature, ...)
)

# Use the GPU ("cuda") if one is available, otherwise use the CPU.
# The model and its input must later be on the SAME device.
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# EXPECTED OUTPUT:
#   Using device: cuda      <- if you selected a GPU runtime
#   Using device: cpu       <- if no GPU is available


# %% ---------------------------------------------------------------------------
# STEP 3: Load the DialogSum dataset
# -----------------------------------------------------------------------------
# DialogSum = public dataset of conversations. Each example has:
#   - "dialogue" : the conversation between #Person1# and #Person2#
#   - "summary"  : a summary written by a HUMAN (our "baseline" to compare against)
# It is split into train / validation / test sets.
dataset = load_dataset("knkarthick/dialogsum")
print(dataset)

# EXPECTED OUTPUT (approximately):
#   DatasetDict({
#       train: Dataset({
#           features: ['id', 'dialogue', 'summary', 'topic'],
#           num_rows: 12460
#       })
#       validation: Dataset({
#           features: ['id', 'dialogue', 'summary', 'topic'],
#           num_rows: 500
#       })
#       test: Dataset({
#           features: ['id', 'dialogue', 'summary', 'topic'],
#           num_rows: 1500
#       })
#   })


# %% ---------------------------------------------------------------------------
# STEP 4: Look at some sample conversations
# -----------------------------------------------------------------------------
# example_indices = ROW NUMBERS in the test set.
# dataset["test"][40] means "conversation number 40 from the test set".
# 40 and 200 are just good examples chosen by the course; you can change them.
example_indices = [40, 200]
dash_line = "-" * 100

for i, index in enumerate(example_indices):
    print(dash_line)
    print("Example", i + 1)
    print(dash_line)
    print("INPUT DIALOGUE:")
    print(dataset["test"][index]["dialogue"])
    print(dash_line)
    print("BASELINE HUMAN SUMMARY:")
    print(dataset["test"][index]["summary"])
    print()

# EXPECTED OUTPUT (shortened):
#   ------------------------------------------------------------------
#   Example 1
#   ------------------------------------------------------------------
#   INPUT DIALOGUE:
#   #Person1#: What time is it, Tom?
#   #Person2#: Just a minute. It's ten to nine by my watch.
#   #Person1#: Is it? I had no idea it was so late. I must be off now.
#   ...
#   ------------------------------------------------------------------
#   BASELINE HUMAN SUMMARY:
#   #Person1# is in a hurry to catch a train. Tom tells #Person1# there
#   is plenty of time.
#
#   Example 2
#   INPUT DIALOGUE:
#   #Person1#: Have you considered upgrading your system?
#   #Person2#: Yes, but I'm not sure what exactly I would need.
#   ... (talk about a painting program, faster processor, CD-ROM drive) ...
#   BASELINE HUMAN SUMMARY:
#   #Person1# teaches #Person2# how to upgrade software and hardware in
#   #Person2#'s system.


# %% ---------------------------------------------------------------------------
# STEP 5: Load the FLAN-T5 model and its tokenizer
# -----------------------------------------------------------------------------
# model_name = model ID on the Hugging Face Hub (huggingface.co/google/flan-t5-base)
model_name = "google/flan-t5-base"

# AutoModelForSeq2SeqLM:
#   - "Auto"    -> reads config.json and picks the correct class (T5) automatically
#   - "Seq2Seq" -> encoder-decoder model (input sequence -> output sequence)
#   - "LM"      -> includes the final linear + softmax layer to predict tokens
# from_pretrained -> downloads the TRAINED weights (first time only, then cached)
# .to(device)     -> moves the model to the GPU/CPU
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

# AutoTokenizer: loads the SAME tokenizer that was used to train this model.
# The tokenizer is NOT a neural network (rule-based + vocabulary), so it always
# runs on the CPU and is never moved with .to(device).
# use_fast=True -> faster tokenizer implementation (written in Rust)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

# Count the model's parameters (learned weights). ":," adds commas.
print("Parameters:", f"{model.num_parameters():,}")

# EXPECTED OUTPUT:
#   (download progress bars the first time: config.json, model.safetensors, ...)
#   Parameters: 247,577,856      <- about 250 million parameters


# %% ---------------------------------------------------------------------------
# STEP 6: Test the tokenizer (text -> numbers -> text)
# -----------------------------------------------------------------------------
sentence = "What time is it, Tom?"

# ENCODE: split text into tokens and convert each token to an ID.
# return_tensors="pt" -> return PyTorch tensors (the model only accepts tensors).
# Result is a dict: {"input_ids": ..., "attention_mask": ...}
encoded = tokenizer(sentence, return_tensors="pt")

# input_ids has shape [1, number_of_tokens] (a batch of 1 sentence).
# [0] removes the batch wrapper -> just the list of IDs.
token_ids = encoded["input_ids"][0]

# DECODE: convert IDs back to text.
# skip_special_tokens=True -> remove special tokens like </s> (end of sequence)
decoded = tokenizer.decode(token_ids, skip_special_tokens=True)

print("ENCODED (token IDs):", token_ids.tolist())
print("TOKENS:", tokenizer.convert_ids_to_tokens(token_ids))
print("DECODED:", decoded)

# EXPECTED OUTPUT (approximately):
#   ENCODED (token IDs): [363, 97, 19, 34, 6, 3059, 58, 1]
#   TOKENS: ['▁What', '▁time', '▁is', '▁it', ',', '▁Tom', '?', '</s>']
#   DECODED: What time is it, Tom?
#
#   - "▁" marks the start of a new word (where a space was)
#   - "</s>" (ID 1) is the end-of-sequence token, added automatically
#   - decode() with skip_special_tokens=True removes "</s>"


# %% ---------------------------------------------------------------------------
# STEP 7: Helper functions
# -----------------------------------------------------------------------------
def generate(prompt, generation_config=None, max_new_tokens=50):
    """Send a prompt to the model and return the generated text (completion).

    Flow: tokenize prompt -> move IDs to device -> model.generate() -> decode.
    """
    # Tokenize the prompt and move the token ID tensors to the same device
    # as the model (the tokenizer creates tensors on the CPU by default).
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Default config = greedy decoding with a cap of max_new_tokens.
    if generation_config is None:
        generation_config = GenerationConfig(max_new_tokens=max_new_tokens)

    # INFERENCE: the encoder reads the prompt once, then the decoder generates
    # tokens one by one until </s> or max_new_tokens.
    output_ids = model.generate(inputs["input_ids"], generation_config=generation_config)

    # output_ids[0] = first (only) result in the batch. Decode to clean text.
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)


def show(i, prompt, output, index):
    """Print the prompt, the human baseline summary, and the model output."""
    print(dash_line)
    print("Example", i + 1)
    print(dash_line)
    print("PROMPT:\n" + prompt)
    print(dash_line)
    print("BASELINE HUMAN SUMMARY:\n" + dataset["test"][index]["summary"])
    print(dash_line)
    print("MODEL GENERATION:\n" + output)
    print()

# EXPECTED OUTPUT:
#   (nothing - this cell only defines functions)


# %% ---------------------------------------------------------------------------
# STEP 8: Summarize WITHOUT any prompt engineering
# -----------------------------------------------------------------------------
# We pass ONLY the raw dialogue. The model doesn't know what task we want,
# so the "summary" is usually poor (it often just repeats one line).
for i, index in enumerate(example_indices):
    dialogue = dataset["test"][index]["dialogue"]
    output = generate(dialogue)
    show(i, dialogue, output, index)

# EXPECTED OUTPUT (model generation part only):
#   Example 1 -> MODEL GENERATION: Person1: It's ten to nine.
#   Example 2 -> MODEL GENERATION: #Person1#: I'm thinking of upgrading my computer.
#
#   -> Not a real summary. Important details are missing.


# %% ---------------------------------------------------------------------------
# STEP 9: Zero-shot inference WITH an instruction
# -----------------------------------------------------------------------------
# ZERO-SHOT = no examples, only an instruction + the input.
# Prompt structure:
#   Instruction  : "Summarize the following conversation."
#   Input/context: the dialogue
#   Output cue   : "Summary:" (tells the model where its answer goes)
for i, index in enumerate(example_indices):
    dialogue = dataset["test"][index]["dialogue"]
    prompt = f"""Summarize the following conversation.

{dialogue}

Summary:
"""
    output = generate(prompt)
    show(i, prompt, output, index)

# EXPECTED OUTPUT (model generation part only):
#   Example 1 -> MODEL GENERATION: The train is about to leave.
#   Example 2 -> MODEL GENERATION: #Person1#: I'm thinking of upgrading my computer.
#
#   -> Slightly different, but still not much better.


# %% ---------------------------------------------------------------------------
# STEP 10: Zero-shot with a DIFFERENT prompt template
# -----------------------------------------------------------------------------
# FLAN-T5 was trained with templates like "Dialogue: ... What was going on?".
# Changing the wording of the prompt can change the result.
# Trying different wordings = PROMPT ENGINEERING.
for i, index in enumerate(example_indices):
    dialogue = dataset["test"][index]["dialogue"]
    prompt = f"""Dialogue:

{dialogue}

What was going on?
"""
    output = generate(prompt)
    show(i, prompt, output, index)

# EXPECTED OUTPUT (model generation part only):
#   Example 1 -> MODEL GENERATION: Tom is late for the train.
#   Example 2 -> MODEL GENERATION: #Person1#: You could add a painting program to your
#                software. #Person2#: That would be a bonus.
#
#   -> A little better: it picks up some of the meaning, but still not great.


# %% ---------------------------------------------------------------------------
# STEP 11: Function to build one-shot / few-shot prompts (in-context learning)
# -----------------------------------------------------------------------------
# IN-CONTEXT LEARNING = put examples of the task INSIDE the prompt.
#   example_indices_full       -> conversations shown WITH their correct summary
#   example_index_to_summarize -> the conversation the model must summarize
#
# Final prompt looks like:
#   Dialogue: <conv A>  What was going on? <summary A> </s>
#   Dialogue: <conv B>  What was going on? <summary B> </s>   (few-shot only)
#   Dialogue: <target>  What was going on?                    <- model answers here
def make_prompt(example_indices_full, example_index_to_summarize):
    prompt = ""

    # Add each complete example (dialogue + human summary).
    for index in example_indices_full:
        dialogue = dataset["test"][index]["dialogue"]
        summary = dataset["test"][index]["summary"]
        # </s> = FLAN-T5's end-of-sequence token; it separates the examples
        prompt += f"""Dialogue:

{dialogue}

What was going on?
{summary}
</s>

"""

    # Add the target dialogue WITHOUT its summary - the model must write it.
    dialogue = dataset["test"][example_index_to_summarize]["dialogue"]
    prompt += f"""Dialogue:

{dialogue}

What was going on?
"""
    return prompt

# EXPECTED OUTPUT:
#   (nothing - this cell only defines a function)


# %% ---------------------------------------------------------------------------
# STEP 12: ONE-SHOT inference
# -----------------------------------------------------------------------------
# ONE-SHOT = 1 complete example (dialogue 40 + its summary),
#            then ask the model to summarize dialogue 200.
example_indices_full = [40]
example_index_to_summarize = 200

one_shot_prompt = make_prompt(example_indices_full, example_index_to_summarize)
output = generate(one_shot_prompt)
show(0, one_shot_prompt, output, example_index_to_summarize)

# EXPECTED OUTPUT (model generation part only):
#   BASELINE HUMAN SUMMARY:
#   #Person1# teaches #Person2# how to upgrade software and hardware in
#   #Person2#'s system.
#   MODEL GENERATION:
#   #Person1# wants to upgrade his system. #Person2# wants to add a painting
#   program to his software. #Person1# wants to add a CD-ROM drive.
#
#   -> Better: it now writes a summary in the same STYLE as the example.


# %% ---------------------------------------------------------------------------
# STEP 13: FEW-SHOT inference
# -----------------------------------------------------------------------------
# FEW-SHOT = several complete examples (here 3: dialogues 40, 80, 120),
#            then ask the model to summarize dialogue 200.
example_indices_full = [40, 80, 120]
example_index_to_summarize = 200

few_shot_prompt = make_prompt(example_indices_full, example_index_to_summarize)

# Check the prompt length in tokens. FLAN-T5's context window is 512 tokens.
print("Prompt length (tokens):", len(tokenizer(few_shot_prompt)["input_ids"]))

output = generate(few_shot_prompt)
show(0, few_shot_prompt, output, example_index_to_summarize)

# EXPECTED OUTPUT:
#   Prompt length (tokens): ~800-900
#   Token indices sequence length is longer than the specified maximum
#   sequence length for this model (... > 512). Running this sequence through
#   the model will result in indexing errors
#     -> This WARNING is expected: the prompt is bigger than the context window.
#        In real projects, filter out inputs longer than 512 tokens.
#   ...
#   MODEL GENERATION:
#   #Person1# wants to upgrade his system. #Person2# wants to add a painting
#   program to his software. #Person1# wants to upgrade his hardware.
#
#   -> Similar to one-shot. More examples do not always help.
#      Rule of thumb: above 5-6 examples you gain little. If it still fails,
#      FINE-TUNE the model instead (Week 2).


# %% ---------------------------------------------------------------------------
# STEP 14: Experiment with GENERATION CONFIGURATION (inference parameters)
# -----------------------------------------------------------------------------
# These settings control HOW the next token is picked from the softmax output.
# They are NOT learned weights; you choose them at inference time.
#
#   max_new_tokens : maximum number of tokens to generate (a cap, not exact)
#   do_sample=False: GREEDY decoding -> always the highest-probability token
#                    -> same output every run, may repeat
#   do_sample=True : RANDOM SAMPLING -> pick tokens randomly, weighted by probability
#                    (required for temperature / top_k / top_p to take effect)
#   temperature    : reshapes probabilities. Low (0.1) = focused/conservative,
#                    high (2.0) = flat/creative/wild. HF allows roughly 0.1 to 2.0 here.
#   top_k          : sample only from the k most likely tokens
#   top_p          : sample only from the top tokens whose total probability reaches p
#
# Pipeline inside generate(): temperature -> top_k -> top_p -> random pick -> repeat
configs = {
    "Greedy (default)": GenerationConfig(max_new_tokens=50),
    "Sampling, temperature=0.1": GenerationConfig(max_new_tokens=50, do_sample=True, temperature=0.1),
    "Sampling, temperature=0.7": GenerationConfig(max_new_tokens=50, do_sample=True, temperature=0.7),
    "Sampling, temperature=2.0": GenerationConfig(max_new_tokens=50, do_sample=True, temperature=2.0),
    "Sampling, top_k=10": GenerationConfig(max_new_tokens=50, do_sample=True, top_k=10),
    "Sampling, top_p=0.5": GenerationConfig(max_new_tokens=50, do_sample=True, top_p=0.5),
    "All together (temp=0.7, top_k=50, top_p=0.9)": GenerationConfig(
        max_new_tokens=50, do_sample=True, temperature=0.7, top_k=50, top_p=0.9
    ),
}

print("BASELINE HUMAN SUMMARY:\n" + dataset["test"][example_index_to_summarize]["summary"])
print(dash_line)

for name, config in configs.items():
    output = generate(one_shot_prompt, generation_config=config)
    print(f"[{name}]\n{output}\n")

# EXPECTED OUTPUT (example - sampled results CHANGE every run):
#   [Greedy (default)]
#   #Person1# wants to upgrade his system. #Person2# wants to add a painting program...
#     -> identical every time you run the cell
#
#   [Sampling, temperature=0.1]
#   #Person1# wants to upgrade his system. #Person2# wants to add a painting program...
#     -> almost the same as greedy (very conservative)
#
#   [Sampling, temperature=0.7]
#   #Person1# suggests #Person2# upgrade the software and add a CD-ROM drive.
#     -> some variety, still sensible
#
#   [Sampling, temperature=2.0]
#   #Person2# considers a painting idea, upgrading faster processing hardware...
#     -> wild / sometimes odd wording
#
#   [Sampling, top_k=10] / [Sampling, top_p=0.5] / [All together ...]
#     -> varied but mostly sensible summaries
#
#   TIP: Run this cell several times and compare. Greedy never changes;
#        sampled outputs do.


# %% ---------------------------------------------------------------------------
# STEP 15: Playground - try your own experiments
# -----------------------------------------------------------------------------
# Change the index, the prompt wording, or the generation settings and
# compare the model's output with the human summary.
index = 300  # any number from 0 to len(dataset["test"]) - 1

my_prompt = f"""Summarize the following conversation in one sentence.

{dataset['test'][index]['dialogue']}

Summary:
"""

my_config = GenerationConfig(max_new_tokens=60, do_sample=True, temperature=0.7, top_p=0.9)

print("HUMAN:", dataset["test"][index]["summary"])
print("MODEL:", generate(my_prompt, generation_config=my_config))

# EXPECTED OUTPUT (example):
#   HUMAN: <the human-written summary of conversation 300>
#   MODEL: <the model's one-sentence summary - changes each run because of sampling>


# =============================================================================
# KEY TAKEAWAYS FROM THIS LAB
# -----------------------------------------------------------------------------
# 1. No prompt            -> poor output (model doesn't know the task)
# 2. Zero-shot + wording  -> small improvements; wording matters (prompt engineering)
# 3. One-shot / few-shot  -> better output by showing examples (in-context learning)
# 4. More shots != always better; >5-6 shots rarely helps -> consider fine-tuning
# 5. Watch the context window (512 tokens for FLAN-T5)
# 6. Generation config: greedy = deterministic; sampling + temperature/top-k/top-p
#    = more variety/creativity
# 7. Prompt engineering is the cheapest FIRST step to evaluate any new model
# =============================================================================
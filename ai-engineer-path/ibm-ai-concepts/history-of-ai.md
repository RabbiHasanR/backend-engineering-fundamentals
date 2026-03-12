# 📘 A Brief History of Artificial Intelligence

> 💡 **AI has been evolving for over 70 years — from rule-based programming to generative chatbots — and is accelerating faster than ever toward general intelligence.**

---

## 📅 Meta Info

| Field        | Details                          |
|-------------|----------------------------------|
| Topic        | History & Evolution of AI        |
| Difficulty   | Beginner                         |
| Key Language | Conceptual (no coding language)  |
| Video Series | Part 1 of 2                      |

---

## 🗂️ Table of Contents

- [The Turing Test (1950)](#the-turing-test-1950)
- [The Term "AI" is Coined (1956)](#the-term-ai-is-coined-1956)
- [Lisp — First AI Programming Language (Late 1950s)](#lisp--first-ai-programming-language-late-1950s)
- [ELIZA — First Chatbot (1960s)](#eliza--first-chatbot-1960s)
- [Prolog — Programming in Logic (1970s)](#prolog--programming-in-logic-1970s)
- [Expert Systems (1980s)](#expert-systems-1980s)
- [Deep Blue Beats Kasparov (1997)](#deep-blue-beats-kasparov-1997)
- [Machine Learning & Deep Learning (2000s)](#machine-learning--deep-learning-2000s)
- [Watson Wins Jeopardy! (2011)](#watson-wins-jeopardy-2011)
- [Generative AI & Foundation Models (2022)](#generative-ai--foundation-models-2022)
- [Agentic AI (2025)](#agentic-ai-2025)
- [The Future: AGI & ASI](#the-future-agi--asi)

---

## 🔹 The Turing Test (1950)

### 📌 What is it?
The Turing Test was proposed by Alan Turing — the father of computer science — as a way to measure whether a computer could be considered "intelligent." A human types messages through a keyboard and receives replies from either another human or a computer, separated by a wall. If the human cannot tell which one is the computer, the machine is judged to be intelligent.

### 🌍 Real-World Analogy
Imagine texting a stranger, not knowing if they're a person or an AI assistant. If you finish the conversation genuinely unsure, that AI has passed the Turing Test. It's like a costume contest for minds — if the disguise is perfect, the costume wins.

### 💻 Concept Example
```
Human types: "What's your favorite movie?"
Response from ???: "I love Inception — the layered storytelling is fascinating."
Human thinks: "That sounds human... but is it?"
→ If the human can't decide = Turing Test passed
```

### ⚠️ Common Mistakes
- Thinking the Turing Test means a computer IS truly intelligent — it only means it *seems* intelligent to a human
- Confusing the Turing Test with actual consciousness or emotion
- Assuming any modern chatbot has "passed" it in a rigorous scientific sense

### 🧠 Memory Trick
> **"T" for Test, "T" for Typing through a wall — if you can't Tell, it Triumphs.**

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What is the Turing Test? | A test where a human tries to distinguish between a computer and a person through typed conversation — if they can't tell, the AI is considered intelligent |

---

## 🔹 The Term "AI" is Coined (1956)

### 📌 What is it?
The term "Artificial Intelligence" was officially coined in 1956, six years after Turing's test. This marked the formal beginning of AI as a recognized field of study and research.

### 🌍 Real-World Analogy
Think of it like when a new sport gets an official name and rulebook. People were already kicking balls around before soccer was "soccer," but giving it a name gave it an identity, funding, and direction.

### ⚠️ Common Mistakes
- Assuming AI started in 2022 with ChatGPT — the field is nearly 70 years old
- Mixing up "coined" (named) with "invented" (built)

### 🧠 Memory Trick
> **"56 = AI's birth certificate year. Think: Eisenhower was president, and so was AI born."**

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| When was "Artificial Intelligence" as a term coined? | 1956 |

---

## 🔹 Lisp — First AI Programming Language (Late 1950s)

### 📌 What is it?
Lisp (short for **List Processing**) was one of the first programming languages used for AI development. It was first implemented on an IBM 704. Lisp relied heavily on **recursion** — a technique where a function calls itself — making it powerful but complex. Critically, to make the AI "smarter," you had to manually write more code. The system didn't learn on its own.

### 🌍 Real-World Analogy
Lisp is like a cookbook where, to add a new recipe, a chef has to physically write it in. The cookbook doesn't learn new recipes by watching you cook — a human has to add every single one.

### 💻 Code Example
```lisp
; A simple recursive function in Lisp — factorial of n
; (Recursion: the function calls itself until it hits the base case)

(defun factorial (n)
  (if (<= n 1)        ; Base case: stop when n is 1 or less
      1               ; Return 1
      (* n (factorial (- n 1)))))  ; Otherwise, multiply n × factorial(n-1)

; (factorial 5) → 5 × 4 × 3 × 2 × 1 = 120
```

### ⚠️ Common Mistakes
- Confusing recursion with loops — recursion calls the same function again; loops repeat a block
- Thinking Lisp "learned" — it didn't. Smarter = more code written by humans
- Underestimating how difficult recursive systems are to debug

### 🧠 Memory Trick
> **LISP = "Lists In Stacked Parentheses" — and to teach it new tricks, you had to List more Instructions.**

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What was Lisp, and what was its key limitation? | An early AI programming language using recursion; to make it smarter, humans had to manually add more code — it could not learn on its own |

---

## 🔹 ELIZA — First Chatbot (1960s)

### 📌 What is it?
ELIZA was the world's first chatbot, created in the 1960s. It was designed to mimic a psychologist — responding to what you said with open-ended follow-up questions like "And how do you feel about that?" It gave people the first experience of *feeling* like they were talking to an intelligent being, and introduced a crude form of **Natural Language Processing (NLP)** — meaning you could speak to it naturally rather than typing rigid commands.

### 🌍 Real-World Analogy
ELIZA is like those "active listening" scripts therapists use — repeat the key words back, ask open-ended questions. It *sounds* deep and understanding, but it's really just following a formula. A skilled therapist does the same thing but actually understands you; ELIZA only pretended to.

### 💻 Concept Example
```
User:   "I've been feeling really stressed lately."
ELIZA:  "Why do you think you've been feeling really stressed lately?"

User:   "My boss doesn't respect me."
ELIZA:  "Tell me more about your boss."

→ ELIZA echoes your words back as questions — no real understanding, but felt natural!
```

### ⚠️ Common Mistakes
- Thinking ELIZA actually understood language — it was pattern matching with mirrors
- Confusing ELIZA with modern LLMs like ChatGPT, which have actual deep understanding
- Underestimating its historical importance — it was the first NLP system people could *feel*

### 🧠 Memory Trick
> **ELIZA = "Every Line Is Zapped with a question Again" — it just asked your words back at you.**

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What was ELIZA and why was it significant? | The first chatbot (1960s), modeled after a psychologist; it introduced crude NLP and gave users the first illusion of talking to an intelligent machine |

---

## 🔹 Prolog — Programming in Logic (1970s)

### 📌 What is it?
Prolog (short for **Programming in Logic**) emerged in the 1970s as another AI language. Instead of recursion like Lisp, Prolog used **rules and relationships**. You'd define a set of facts and rules, and then ask the system to run **inferences** (logical deductions) against them. But like Lisp, making it smarter still required humans to write more rules manually.

### 🌍 Real-World Analogy
Prolog is like a law book. The lawyers (programmers) write down all the rules. When a case (query) comes in, the judge (Prolog) reads the rules and makes a decision. But if a new type of crime emerges that isn't in the rulebook, the judge is helpless — someone has to add the new law first.

### 💻 Code Example
```prolog
% Define facts (relationships)
parent(tom, bob).       % Tom is Bob's parent
parent(bob, ann).       % Bob is Ann's parent

% Define a rule
grandparent(X, Z) :-    % X is Z's grandparent IF...
    parent(X, Y),       % X is Y's parent AND
    parent(Y, Z).       % Y is Z's parent

% Query: Who is Ann's grandparent?
% ?- grandparent(Who, ann).
% Result: Who = tom ✅
```

### ⚠️ Common Mistakes
- Confusing Prolog with procedural languages — Prolog describes *what* is true, not *how* to compute it
- Thinking Prolog could learn — every new rule had to be hand-coded
- Forgetting that both Lisp and Prolog shared the same core limitation: no self-learning

### 🧠 Memory Trick
> **Prolog = "PRO-gramming in LOGic" — you write the logic, it does the deduction. But it can't write its own logic.**

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What was Prolog's approach to AI? | Using rules and logical inference rather than recursion; still required humans to manually add rules to improve intelligence |

---

## 🔹 Expert Systems (1980s)

### 📌 What is it?
Expert Systems were AI programs in the 1980s designed to encode the knowledge of human experts (doctors, lawyers, engineers) into rule-based systems. They could give advice in specific domains. Businesses were hugely excited — it seemed like AI was finally practical. But they turned out to be **brittle**: they couldn't adapt or learn, and they failed outside their narrow ruleset. The hype far exceeded the reality.

### 🌍 Real-World Analogy
An expert system is like a very detailed FAQ page. As long as your problem is covered, you get a great answer. But the moment your question is slightly unusual or outside the FAQ scope, it's useless. Real experts handle edge cases; expert systems couldn't.

### 💻 Concept Example
```
Expert System for Medical Diagnosis:

Rule 1: IF fever AND cough → possible flu
Rule 2: IF fever AND rash → possible measles
Rule 3: IF chest pain AND shortness of breath → possible heart issue

User input: "I have a fever and unusual fatigue"
→ System: "No matching rule found." ← Brittle! Can't reason about new symptoms
```

### ⚠️ Common Mistakes
- Confusing the 1980s AI boom with actual success — there was enormous hype but limited real-world payoff
- Thinking expert systems were "intelligent" — they were still just elaborate if/then trees
- Missing the lesson: narrow, rigid rule systems always hit a wall

### 🧠 Memory Trick
> **Expert Systems = "Expert in One Thing, Useless Everywhere Else" — great inside the box, lost outside it.**

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| Why did Expert Systems fail to deliver? | They were brittle — could not adapt or learn beyond their hard-coded rules, failing when problems fell outside their narrow domain |

---

## 🔹 Deep Blue Beats Kasparov (1997)

### 📌 What is it?
In 1997, IBM's chess-playing computer **Deep Blue** defeated Garry Kasparov, the reigning world chess champion — the best human chess player alive. This was a landmark moment because chess was seen as the ultimate test of human strategic intelligence, creativity, and planning. Most thought no computer could ever beat a grandmaster. It proved them wrong and reignited excitement in AI.

### 🌍 Real-World Analogy
Imagine the best sprinter in the world being beaten by a machine in a footrace. Not a slight edge — a decisive defeat. It made people realize: if machines can master chess at a grandmaster level, what else might they eventually master?

### ⚠️ Common Mistakes
- Thinking Deep Blue "understood" chess the way humans do — it used massive computational search trees, not intuition
- Assuming it was a general intelligence — Deep Blue could only play chess, nothing else
- Forgetting this happened in *1997* — many people think AI milestones are all recent

### 🧠 Memory Trick
> **Deep Blue: "Deep" search, "Blue" chip computing — it thought deeper and faster than any human could.**

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What did Deep Blue accomplish in 1997? | IBM's AI defeated world chess champion Garry Kasparov — the first time a computer beat the world's best chess player |

---

## 🔹 Machine Learning & Deep Learning (2000s)

### 📌 What is it?
The 2000s saw the rise of **Machine Learning (ML)** and **Deep Learning (DL)** — a fundamental shift from *programming* AI to *teaching* it. Instead of writing rules, you'd feed the system massive amounts of data and let it find patterns on its own.

- **Machine Learning**: Pattern recognition at scale — show it thousands of cat photos, it learns what "cat" looks like
- **Deep Learning**: Simulates human brain structure using **neural networks** — multiple layers of processing that can recognize incredibly complex patterns (faces, speech, language)

This is still the foundation of AI today.

### 🌍 Real-World Analogy
Old AI: Teaching a child by writing down every rule ("if four legs + fur + meows = cat").
Machine Learning: Showing a child 10,000 pictures of cats until they just *know* what a cat looks like — without ever writing a rule.

### 💻 Concept Example
```python
# Conceptual ML workflow (using sklearn-style pseudocode)

# Step 1: Gather labeled training data
data = [
    {"pixels": [cat_image_1], "label": "cat"},
    {"pixels": [dog_image_1], "label": "dog"},
    # ... thousands more examples
]

# Step 2: Train the model — it finds patterns automatically
model.fit(training_images, training_labels)

# Step 3: Predict on new data
prediction = model.predict(new_image)
# → "cat" (model recognized the pattern, no human-written rules!)
```

### ⚠️ Common Mistakes
- Thinking ML is just "more rules" — it's fundamentally different; rules emerge from data
- Confusing ML (pattern matching) with DL (neural-network-simulated brain layers)
- Forgetting that quality + quantity of training data is everything in ML

### 🧠 Memory Trick
> **ML = "Machines Learning from Examples." DL = "Deep layers mimicking brain cells."**
> Think: ML is a student studying flashcards; DL is a brain forming memories.

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What is the key difference between old AI programming and Machine Learning? | Old AI: humans write rules. ML: the system learns rules from patterns in data — no manual rule-writing required |

---

## 🔹 Watson Wins Jeopardy! (2011)

### 📌 What is it?
In 2011, IBM's **Watson** AI played the TV game show *Jeopardy!* against two of its all-time champions — and won three nights in a row. This was harder than chess because:
1. Questions are in **natural language** full of puns, idioms, and figures of speech
2. The topic domain is **infinitely broad** (history, science, pop culture, etc.)
3. Watson had to be **fast** (Jeopardy! rewards speed) and **confident** (wrong answers lose points — so it had to calculate its own certainty)

### 🌍 Real-World Analogy
Chess has a finite board with fixed rules. Jeopardy! is the whole world poured into a question. "It's raining cats and dogs" doesn't mean animals are falling. Watson had to understand nuance, metaphor, and context — not just look things up.

### 💻 Concept Example
```
Jeopardy! clue: "This man was the first U.S. President to be impeached."
→ Watson must:
  1. Parse natural language (what's being asked?)
  2. Resolve ambiguity (impeached ≠ removed from office)
  3. Search its knowledge base
  4. Calculate confidence: "Am I 85%+ sure? Then buzz in."
  5. Answer: "Andrew Johnson" ✅
```

### ⚠️ Common Mistakes
- Thinking Watson was just Googling answers in real time — it was NOT connected to the internet
- Underestimating why language is so hard for computers (idioms, sarcasm, wordplay)
- Missing the confidence-calculation aspect — Watson had to know *how sure* it was before answering

### 🧠 Memory Trick
> **Watson Won on Wit — Words With All Their Twists and nuance.**
> "If chess = math, then Jeopardy! = poetry."

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| Why was Watson's Jeopardy! victory harder than Deep Blue's chess victory? | Because Jeopardy! requires natural language understanding, a near-infinite knowledge domain, speed, and confidence calibration — far more complex than chess |

---

## 🔹 Generative AI & Foundation Models (2022)

### 📌 What is it?
Around 2022, **Generative AI** based on **Foundation Models** became mainstream. These are enormous AI systems trained on vast amounts of internet text, images, and data. Unlike previous AI, they can *generate* new content — text, images, audio, and video — that didn't exist before. This was the moment AI "got real" for most people, bringing chatbots like ChatGPT into everyday life.

Key abilities:
- Write reports, summarize emails, answer almost any question
- Generate realistic images from descriptions
- Create audio and video — including **deepfakes**

### 🌍 Real-World Analogy
Previous AI was a specialist doctor — great in one area. Generative AI is like a brilliant generalist who's read every book ever written and can write, draw, compose music, and hold a brilliant conversation on any topic. The catch? It can also forge signatures convincingly.

### 💻 Concept Example
```
Prompt: "Write a professional email declining a meeting politely."

Generative AI Output:
"Thank you for the invitation. Unfortunately, I have a prior commitment 
at that time and will be unable to attend. I'd love to reconnect — 
would another time work for you?"

→ Not retrieved from a database. Genuinely generated, original text.
```

### ⚠️ Common Mistakes
- Thinking the AI "knows" things — it predicts likely next tokens based on patterns, not facts
- Ignoring deepfake dangers — the same tech that writes poems can fabricate a video of anyone
- Assuming it's always right — hallucination (confident wrong answers) is a real problem

### 🧠 Memory Trick
> **GEN-AI = "GENius that never existed" — it creates things that were never in its training data.**
> Foundation model = the giant base everything is built on, like a foundation of a house.

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What made Generative AI a turning point in 2022? | It could generate new text, images, audio, and video — not just retrieve or classify — making AI feel accessible and versatile to everyday users |

---

## 🔹 Agentic AI (2025)

### 📌 What is it?
**Agentic AI** refers to AI systems that operate with greater **autonomy** — you give them a goal, and they figure out *how* to accomplish it by using tools, services, and APIs on their own. Rather than answering a question, an agent might browse the web, write code, send an email, book a meeting, and file a report — all to accomplish your stated objective.

### 🌍 Real-World Analogy
Previous AI = a very smart assistant who answers your questions when you ask.
Agentic AI = a very capable employee you give a project to, and they handle everything end-to-end without needing hand-holding at every step.

### 💻 Concept Example
```
User goal: "Plan my team's quarterly review meeting."

Agentic AI autonomously:
  1. Checks everyone's Google Calendar for availability
  2. Books the conference room via calendar API
  3. Drafts and sends the invite email
  4. Creates a shared agenda doc
  5. Sets a reminder 24 hours before
  → All done. No step-by-step instructions needed.
```

### ⚠️ Common Mistakes
- Confusing agentic AI with simple chatbots — agents *act*, not just *respond*
- Underestimating risks of AI with broad autonomy (what if it makes a wrong decision on your behalf?)
- Thinking agents are pure science fiction in 2025 — they're real and being deployed now

### 🧠 Memory Trick
> **Agent = Actor. Give it a goal, it acts. AGENT = "Autonomous Goal-Executing iNTelligence."**

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What is Agentic AI? | AI that operates autonomously to achieve goals, using tools and services without needing step-by-step human instruction |

---

## 🔹 The Future: AGI & ASI

### 📌 What is it?
The video lays out three tiers of AI intelligence:

| Level | Name | Definition |
|-------|------|------------|
| Current | **ANI** (Artificial Narrow Intelligence) | AI that excels at specific tasks (chess, language, image recognition) |
| Next | **AGI** (Artificial General Intelligence) | AI as smart or smarter than humans in *every* area |
| Beyond | **ASI** (Artificial Super Intelligence) | AI that *far exceeds* all human intelligence across all domains |

We are currently in the ANI era. AGI and ASI remain theoretical but are the subject of massive research and debate.

### 🌍 Real-World Analogy
ANI = a world-class chess player who can't cook.
AGI = a Renaissance genius who can do anything a human can.
ASI = something beyond human comprehension — imagine Einstein multiplied by a million, running at the speed of a computer.

### ⚠️ Common Mistakes
- Thinking current AI is AGI — it's not; today's AI is still narrow
- Dismissing AGI as impossible — many leading AI researchers believe it may arrive within decades
- Confusing ASI with "evil AI" from movies — the safety concerns are real but more nuanced

### 🧠 Memory Trick
> **ANI → AGI → ASI = "Narrow → General → Super"**
> Think of it as climbing a mountain: we're at base camp (ANI), summit is AGI, and beyond the summit is ASI.

### ⚡ Flashcard
| Question | Answer |
|----------|--------|
| What are ANI, AGI, and ASI? | ANI = narrow task AI (current); AGI = human-level across all domains; ASI = superhuman intelligence far beyond all humans |

---

## 🔗 Concept Map

```
AI EVOLUTION TIMELINE
═══════════════════════════════════════════════════════

[1950] Turing Test ──────────────────────────────────────┐
       "Can a machine fool a human?"                      │
                                                          │
[1956] "AI" is Named ─────────────────────────────────   │
       Field gets its identity                            │
                                                          ▼
[1950s–80s] PROGRAMMED AI ERA
   ├── LISP (late 1950s) ─── recursion, IBM 704
   ├── ELIZA (1960s) ──────── first chatbot, crude NLP
   └── Prolog (1970s) ──────── logic rules & inference
         │
         └──► All share the same flaw:
              SMARTER = MORE HUMAN-WRITTEN CODE
                    │
                    ▼
[1980s] Expert Systems ──────── brittle, over-hyped, failed
         Promised intelligence, delivered rigid rules
                    │
                    ▼
[1997] Deep Blue ────────────── first major AI milestone
         Beats world chess champion Kasparov
                    │
                    ▼
[2000s] Machine Learning + Deep Learning
         THE BIG SHIFT: Systems LEARN from DATA
         ├── ML = pattern matching at scale
         └── DL = neural networks simulate the brain
                    │
                    ▼
[2011] Watson ───────────────── natural language milestone
         Beats Jeopardy! champions
         First major NLP + confidence + speed victory
                    │
                    ▼
[2022] Generative AI ────────── AI goes mainstream
         Foundation models → ChatGPT, DALL-E, etc.
         Generates text, images, audio, deepfakes
                    │
                    ▼
[2025] Agentic AI ───────────── AI gains autonomy
         Agents pursue goals, use tools, act independently
                    │
                    ▼
[FUTURE]
   ├── AGI: Human-level across all domains
   └── ASI: Far beyond all human intelligence

KEY THEME: PROGRAMMED → LEARNED → GENERATIVE → AUTONOMOUS
```

---

## 1. 📋 Full Topic List

1. The Turing Test (1950)
2. The Coining of "Artificial Intelligence" (1956)
3. Lisp — First AI Programming Language (late 1950s)
4. ELIZA — First Chatbot (1960s)
5. Prolog — Logic-Based AI Language (1970s)
6. Expert Systems and the 1980s AI Boom (1980s)
7. Deep Blue vs. Kasparov (1997)
8. Machine Learning and Deep Learning (2000s)
9. IBM Watson and Jeopardy! (2011)
10. Generative AI and Foundation Models (2022)
11. Agentic AI (2025)
12. AGI and ASI — The Future

---

## 2. 🧠 Memory Tricks Summary

| Concept | Mnemonic |
|---------|----------|
| Turing Test | "T" for Typing through a wall — if you can't Tell, it Triumphs |
| AI coined (1956) | Eisenhower was president — so was AI "born" |
| Lisp | "Lists In Stacked Parentheses" — to teach it, list more instructions |
| ELIZA | "Every Line Is Zapped with a question Again" |
| Prolog | "PRO-gramming in LOGic" — you write logic, it deduces |
| Expert Systems | "Expert in One Thing, Useless Everywhere Else" |
| Deep Blue | "Deep" search + "Blue" chip — deeper than any human |
| ML vs DL | ML = flashcard student; DL = brain forming memories |
| Watson/Jeopardy! | "If chess = math, then Jeopardy! = poetry" |
| Generative AI | "GENius that never existed" — creates novel output |
| Agentic AI | "Autonomous Goal-Executing iNTelligence" |
| ANI → AGI → ASI | "Narrow → General → Super" — climbing a mountain |

---

## ✅ Key Takeaways

- [ ] AI is 70+ years old — it didn't start with ChatGPT
- [ ] Early AI (Lisp, Prolog) was *programmed* — smarter = more human-written code
- [ ] ELIZA (1960s) was the first chatbot; it used pattern-matching to mimic understanding
- [ ] Expert Systems (1980s) promised a lot but were too brittle to deliver
- [ ] Deep Blue (1997) was the first AI to beat a world chess champion
- [ ] Machine Learning was a fundamental shift: systems *learn from data* instead of following rules
- [ ] Watson (2011) showed AI could handle natural language, breadth, speed, and confidence
- [ ] Generative AI (2022) made AI mainstream — it creates text, images, and audio
- [ ] Agentic AI (2025) adds autonomy — AI acts toward goals without step-by-step instruction
- [ ] We are currently in the ANI era; AGI and ASI remain future milestones

---

## ✅ Quick Summary (Under 200 Words)

AI's history spans over 70 years, evolving in distinct eras. In the 1950s, Alan Turing proposed the Turing Test as a measure of machine intelligence, and the term "AI" was coined in 1956. Early AI was entirely **programmed** — languages like Lisp (recursion-based) and Prolog (logic-based) required humans to manually write every rule. ELIZA, the first chatbot, gave users a taste of conversational AI in the 1960s.

The 1980s brought Expert Systems — promising but brittle. Then in 1997, IBM's Deep Blue beat world chess champion Kasparov, reigniting AI optimism. The real revolution came with **Machine Learning** and **Deep Learning** in the 2000s — systems that learn from data instead of following pre-written rules. In 2011, Watson's Jeopardy! victory showed AI mastering natural language.

2022 was AI's mainstream moment: **Generative AI** powered by Foundation Models could write, draw, compose, and even create deepfakes. By 2025, **Agentic AI** gave systems real-world autonomy. The road ahead leads toward **AGI** (human-level intelligence) and eventually **ASI** (superhuman intelligence) — the ultimate destinations of this remarkable 70-year journey.

---

## ❓ Practice Questions

1. **(MCQ)** Who proposed the Turing Test, and in what year?
   - A) John McCarthy, 1956
   - B) Alan Turing, 1950 ✅
   - C) Alan Turing, 1956
   - D) Marvin Minsky, 1965

2. **(True/False)** Lisp and Prolog could both learn from data and improve themselves without human intervention.

3. **(Short Answer)** What was ELIZA, and what made it significant for the history of AI?

4. **(MCQ)** What was the core limitation shared by both Lisp and Prolog?
   - A) They were too slow for modern computers
   - B) They could not handle mathematical operations
   - C) Making them smarter required manually adding more code ✅
   - D) They required an internet connection

5. **(True/False)** Deep Blue beating Kasparov in 1997 demonstrated that AI had achieved Artificial General Intelligence.

6. **(Short Answer)** Why was Watson's victory on Jeopardy! considered *harder* to achieve than Deep Blue's chess victory?

7. **(MCQ)** What distinguishes Generative AI from earlier AI systems?
   - A) It uses more rules than previous systems
   - B) It can only generate images, not text
   - C) It can create new content (text, images, audio) that didn't previously exist ✅
   - D) It requires real-time internet access to function

8. **(Short Answer)** What is the difference between ANI, AGI, and ASI? Give a one-sentence definition of each.

---

### 📖 Answer Key

1. **B** — Alan Turing, 1950
2. **False** — Both Lisp and Prolog required humans to manually write more code to improve intelligence; they could not self-learn
3. ELIZA was the first chatbot (1960s), modeled on a psychologist using simple pattern-matching to mimic conversation. It was significant because it introduced the first crude Natural Language Processing and gave people the experience of *feeling* like they were talking to an intelligent system.
4. **C** — Making them smarter required manually adding more code
5. **False** — Deep Blue was narrow AI that could only play chess; it had no general intelligence
6. Jeopardy! required natural language understanding including idioms, puns, and figures of speech; covered an infinitely broad domain of knowledge; demanded both speed and confidence calibration (wrong buzzes lose points) — all far more complex than chess's fixed rules
7. **C** — It can create new content (text, images, audio) that didn't previously exist
8. ANI (Artificial Narrow Intelligence) = AI that excels at specific tasks but nothing outside them. AGI (Artificial General Intelligence) = AI as smart as or smarter than humans in all areas. ASI (Artificial Superintelligence) = AI that far exceeds all human intellectual capabilities across every domain.

---

## 📖 Glossary

| Term | Definition |
|------|------------|
| Turing Test | A test of machine intelligence: if a human can't distinguish a computer from a person in typed conversation, the machine is considered intelligent |
| Recursion | A programming technique where a function calls itself; used heavily in Lisp |
| Lisp | Early AI programming language (late 1950s) using list processing and recursion |
| ELIZA | First chatbot (1960s), mimicked a psychologist using simple pattern matching |
| Natural Language Processing (NLP) | AI capability to understand and process human language |
| Prolog | AI programming language (1970s) using logical rules and inference |
| Expert Systems | 1980s AI systems encoding domain expertise as rules; brittle and limited |
| Deep Blue | IBM's chess AI (1997) that beat world champion Garry Kasparov |
| Machine Learning (ML) | AI that learns patterns from data rather than following human-written rules |
| Deep Learning (DL) | Advanced ML using neural networks that mimic the structure of the human brain |
| Neural Network | A computing structure of layered nodes that mimics how human neurons process information |
| Watson | IBM's AI (2011) that won Jeopardy! by mastering natural language and broad knowledge |
| Generative AI | AI that creates new content (text, images, audio) trained on foundation models |
| Foundation Model | A massive AI model trained on enormous datasets that serves as a base for many applications |
| Deepfake | AI-generated realistic impersonation of a real person in video or audio |
| Agentic AI | AI that acts autonomously toward goals using tools and services without step-by-step instruction |
| ANI | Artificial Narrow Intelligence — current AI, expert in specific tasks only |
| AGI | Artificial General Intelligence — hypothetical AI matching or exceeding human intelligence in all areas |
| ASI | Artificial Superintelligence — hypothetical AI far surpassing all human cognitive capabilities |

---

*Notes generated from video transcript: "A Brief History of AI" (Part 1 of 2)*
**1. Core Focus: LLM APIs for Developers**

* Instead of using the ChatGPT web interface for one-off tasks, developers can use **LLM APIs** to rapidly build software applications.
* **Key Use Cases:** Summarizing, inferring, transforming, expanding, and building chatbots.

**2. Base LLMs vs. Instruction-Tuned LLMs**

| Feature | Base LLM | Instruction-Tuned LLM |
| --- | --- | --- |
| **How it works** | Predicts the next most likely word based on internet training data. | Fine-tuned on instructions and refined using **RLHF** (Reinforcement Learning from Human Feedback). |
| **Behavior** | Completes text patterns (e.g., Q: *"What is the capital of France?"* $\rightarrow$ A: *"What is France's population?"*). | Follows instructions and answers directly (e.g., Q: *"What is the capital of France?"* $\rightarrow$ A: *"Paris."*). |
| **Best for** | Raw text completion. | **Practical software applications** (safer, more helpful, honest, and harmless). |

**3. Core Prompting Mental Model & Principles**

* **Treat the LLM like a smart new graduate:** Assume it is intelligent but knows nothing about your specific task. When it fails, your instructions were likely too vague.
* **Principle 1: Be Clear and Specific:** Explicitly define the **focus** (e.g., scientific work vs. personal history), **tone** (e.g., professional journalist vs. casual note), and provide relevant **reference text/context** in advance.
* **Principle 2: Give the LLM Time to Think:** Structure prompts so the model can reason through the task (covered in the next lesson).




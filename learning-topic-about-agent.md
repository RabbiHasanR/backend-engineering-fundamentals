
## 1. Agents in production (beyond the demo stage)

**What it means:** Companies have moved past proofs of concept. They now run several specialized agents that work together inside real software processes.

**Topics to study:**
- **Agent basics:** an LLM running in a loop that calls tools: think → act (tool call) → observe the result → repeat. Search for *ReAct pattern* and *tool use / function calling*.
- **Multi-agent architectures:** how work is split across roles.
  - *Orchestrator–worker* (supervisor) pattern. A "Principal Agent" or "Tech Lead Agent" plans the work and hands pieces to worker agents.
  - *Role-specialized agents*, such as a coding agent, a QA/reviewer agent, and a planner agent.
  - **Agent as consumer:** an agent acts as the *client* of your APIs or services, instead of a human or a frontend. This changes how you design APIs: they need to be machine-readable, well documented, and predictable.
- **Agent protocols:**
  - **MCP (Model Context Protocol):** a standard way to expose tools and data to agents.
  - **A2A (Agent-to-Agent protocol):** how agents talk to each other.
- **Human-in-the-loop:** approval steps before risky actions.

## 2. The setup around the model matters more than the model itself

**What it means:** A cheaper model with a well-built system around it often beats an expensive model with a poor one.

**Topics to study:**
- **Context engineering:** deciding exactly what goes into the model's context window, such as instructions, relevant documents, and the results of earlier tool calls, and leaving the rest out. This is the most important skill in this list.
- **RAG (Retrieval-Augmented Generation):** fetching relevant information from documents or databases and putting it into the context.
- **Structured outputs / contracts:** forcing the model to return valid JSON that matches a schema, then validating it. Search for *JSON schema output* and *Pydantic + LLM*.
- **Feedback loops:** the agent checks its own work using tests, linters, validators, or another agent, then fixes errors. Search for *self-correction* and *evaluator-optimizer pattern*.
- **Model routing:** using a cheap model for easy steps and a strong model only for hard ones.
- **Evals (evaluations):** automated tests that measure whether the agent does its job well. Without evals you cannot tell whether a change helped.

## 3. Code is easy now, but the bottleneck has moved

**What it means:** AI writes code fast. The slow parts are now everything else, which is why many companies don't yet see a big return on investment.

**Topics to study (mostly concepts and discussion, not tools):**
- **New bottlenecks:** code review, testing and verification, unclear requirements, integration, deployment, and knowing *what* to build.
- **Verification is the new bottleneck:** how teams handle reviewing large amounts of AI-generated code.
- **Measuring AI productivity:** why "lines of code" is misleading. Look into *DORA metrics* and research on AI developer productivity.
- **Theory of Constraints:** speeding up one step doesn't speed up the whole system. This is the background idea behind this point.

## 4. Old engineering ideas are important again

**What it means:** Agents work best when the system is clearly defined. Good specs and schemas let you give an agent exactly the context it needs in fewer tokens, which is cheaper and more reliable.

**Topics to study:**
- **Spec-driven development:** write a clear specification first, then let the agent build from it.
- **Schemas and contracts:** OpenAPI specs, JSON Schema, Protobuf/gRPC, and database schemas. A precise schema is compact context for an agent.
- **Event-driven design:** services communicate through events. Agents can react to events instead of polling. You already know Redis Streams, which is a good base for this.
- **Durable workflows / durable execution:** long-running agent tasks must survive crashes, retries, and restarts without losing progress. Study **Temporal**, and compare it with Celery, which you already use. Also look at *LangGraph checkpointing*, *idempotency*, and the *saga pattern*.
- **Token efficiency techniques:** prompt caching, context compression and summarization, giving the agent only the parts of a codebase or document it needs, and putting tools behind a small, clear interface.

## 5. Why agents fail

**What it means:** Many sessions were about the ways agents break in production.

**Common failure modes to study:**
- **Context problems:** too much context ("context rot"), missing context, or stale information.
- **Hallucinated tool calls:** wrong arguments or calls to tools that don't exist.
- **Infinite loops and runaway cost:** the agent keeps retrying and burning tokens.
- **Error compounding:** small mistakes across many steps add up to a wrong result.
- **Multi-agent coordination failures:** agents misunderstand each other or duplicate work.
- **Prompt injection:** malicious text in tool results or web pages hijacks the agent. This is a major security topic.
- **Non-determinism:** the same input gives different outputs, which makes testing hard.

**Related defenses to study:**
- **Guardrails:** checks before and after model calls.
- **Agent observability:** tracing every step, tool call, token count, and cost. Your OpenTelemetry and Grafana experience transfers well here; look into *OpenTelemetry GenAI semantic conventions* and *Langfuse*.
- **Budgets and limits:** caps on steps, tokens, and time.

---

## Suggested study order

1. **Agent basics:** the agent loop, tool calling, and structured outputs. Build a tiny agent yourself in Python.
2. **Context engineering and RAG**
3. **Evals and observability**
4. **Durable workflows and event-driven design** (Temporal, LangGraph)
5. **Multi-agent patterns and MCP**
6. **Failure modes, guardrails, and prompt injection**
7. **The ROI and bottleneck discussion**, mostly reading articles

**Good starting resources:**
- Anthropic's article *"Building effective agents"*
- Anthropic's posts on *context engineering* and on building multi-agent research systems
- The Temporal docs on durable execution
- The LangGraph tutorials






**Prompt Writing Guidelines**

**Principle 1: Write clear and specific instructions**
- Clear doesn't mean short. Longer prompts often give the model more context and better results.
- **Use delimiters** (```, """, < >, XML tags, section titles) to mark which part of the prompt is input text. This also helps block prompt injection.
- **Ask for structured output** (JSON, HTML) so you can parse it in code.
- **Ask the model to check conditions first.** If an assumption isn't met, tell it what to say instead (e.g. "No steps provided"). Plan for edge cases.
- **Few-shot prompting:** show one or more examples of the task done correctly so the model copies that style.

**Principle 2: Give the model time to think**
- If the model rushes to a wrong answer, ask it to reason step by step before the final answer.
- **Specify the steps** (Step 1, Step 2…) for complex tasks.
- **Define an exact output format** (e.g. Text / Summary / Translation / Output JSON) so results are predictable and easy to parse.
- **Make it solve the problem itself before judging.** For example, have it work out its own solution and then compare it with the student's, instead of just evaluating the student's answer.

**Model limitations**
- **Hallucination:** the model doesn't know where its knowledge ends and can invent realistic-sounding facts, such as describing a fake product.
- **Reducing hallucination:** when answering from a document, ask it to first pull out relevant quotes and then answer using only those quotes, so the answer can be traced to the source.




**Iterative Prompt Development**

**Core idea**
- You rarely get the final prompt right on the first try, and that's fine. What matters is having a good process for improving it.
- Lists of "perfect prompts" aren't very useful. No single prompt fits every task; build one for your own use case.

**The loop**
1. Start with an idea of the task.
2. Write a first prompt that is clear, specific, and gives the model time to think.
3. Run it and look at the result.
4. Figure out what went wrong: unclear instructions, or not enough thinking time?
5. Refine the prompt and repeat until it works.

**Tricks from the example (product description from a fact sheet)**
- **Control length:** "use at most 50 words," "at most 3 sentences," or "at most 280 characters."
  - Models are approximate at word counts and weaker at character counts, because they read text as tokens.
- **Set the audience and focus:** e.g. "for furniture retailers, focus on technical details and materials."
- **Ask for specific details:** e.g. "include every 7-character product ID."
- **Request formatting:** e.g. "add a dimensions table and format everything as HTML."
- When you add new instructions, keep the old ones you still need. The example accidentally dropped the 50-word limit and the output got long again.

**Scaling up**
- Early on, iterating against one example is enough.
- For mature applications, test the prompt against many examples (10 to 100+) and check average and worst-case performance to make the final improvements.

**Key takeaway**
- Good prompt engineering isn't about knowing the perfect prompt. It's about steadily refining toward the result you need.








**Summarizing with Prompts **

**Why it matters**
- There's too much text to read. LLM summaries let you skim far more content, such as many product reviews on an e-commerce site.

**Prompt tricks**
- **Limit the length:** e.g. "summarize in at most 30 words." You can also limit sentences or characters.
- **Use delimiters** around the text to summarize, so the model knows exactly what to work on.
- **Set the purpose or audience:** tell it who the summary is for, so it puts the most relevant details first.
  - For the shipping department: "focus on shipping and delivery."
  - For the pricing department: "focus on price and perceived value."
- **Summarize vs. extract:**
  - A *summary* still includes other details besides the focus area.
  - Use *"extract"* when you want only the relevant information, e.g. "extract only the shipping-related feedback."

**Using it in a workflow**
- Put multiple reviews in a list and loop over them with the same prompt (e.g. "at most 20 words each").
- This is useful for a **dashboard**: show short summaries of hundreds of reviews and let users click through to the full original.

**Key takeaway**
- Tailor the prompt to the purpose: control length, name the audience, and choose between *summarize* and *extract* depending on how focused you want the output.







**Inferring with Prompts**

**What "inferring" means**
- The model takes text as input and analyzes it: sentiment, emotions, names, labels, topics.
- **Big advantage over traditional ML:** no labeled data, training, or deploying separate models. One model and one API handle many tasks, using only prompts.

**Prompt tricks for developers**
- **Constrain the output for easy parsing:** e.g. "answer in a single word: positive or negative" instead of a full sentence.
- **Limit list size:** e.g. "include no more than five items."
- **Ask yes/no classification questions:** e.g. "Is the writer expressing anger?" This is useful for flagging upset customers for support.
- **Extract specific fields as JSON:** e.g. keys "Item" and "Brand," which load straight into a Python dict.
- **Specify data types:** e.g. "format anger as a boolean" so you get `false`, not `"false"`.
- **Combine many extractions in one prompt:** get sentiment, anger, item, and brand in a single call instead of 3–4 separate calls. This saves cost and latency.
- **Infer topics:** e.g. "determine five topics, each 1–2 words, comma-separated."

**Zero-shot classification**
- Give a fixed list of topics and ask which ones appear in the text, returning 0/1 for each topic.
- This works with no labeled training examples, which is why it's called zero-shot.
- **Use case:** an alert system, e.g. print "ALERT: New NASA story!" when the topic matches.

**Production tip**
- A list output like `[1, 0, 1]` is **brittle**, because LLM output can be inconsistent.
- For production, **ask for JSON** so parsing is reliable.

**Key takeaway**
- Tasks that once took days or weeks of ML work can now be built in minutes with prompts. Design your outputs (single words, booleans, JSON) so your code can process them reliably.






**Transforming with Prompts**

**What "transforming" means**
- Converting input text into a different form: another language, another tone, another format, or corrected grammar.
- Many tasks that once needed painful regex code can now be done with a few prompts.

**1. Translation**
- Translate directly: e.g. "Translate the following English text to Spanish."
- **Detect the language:** e.g. "Tell me what language this is."
- **Translate into several languages at once:** e.g. French, Spanish, and even "English pirate."
- **Formal vs. informal:** ask for both forms in languages where register depends on the listener.
- **Universal translator workflow:** loop over user messages, detect each language, then translate to the target languages (e.g. English and Korean).
- **Tip:** to get just the language name instead of "This is French," say "respond with only one word" or ask for JSON.

**2. Tone transformation**
- Rewrite for a different audience: e.g. "Translate from slang to a business letter."

**3. Format conversion**
- Convert between JSON, HTML, XML, Markdown, and so on.
- **Describe both input and output formats** in the prompt: e.g. "Translate this Python dictionary from JSON to an HTML table with column headers and a title."

**4. Spelling and grammar checking**
- "Proofread and correct the following text." This is especially useful when writing in a non-native language.
- **Handle the no-error case:** e.g. "If you don't find any errors, say 'No errors found'."
- **Show the changes:** use a diff tool (e.g. the `redlines` Python package) to compare the original with the corrected text.
- Iterate on the prompt until it behaves reliably every time.

**5. Combining multiple transformations**
- One prompt can do several things together: e.g. proofread, make it more compelling, follow APA style, target an advanced reader, and output in Markdown.

**Developer tips**
- Use delimiters (```, """, < >). Any is fine as long as the separation is clear.
- Constrain output (one word, JSON) when code will process it.
- Loop over inputs with the same prompt for batch processing.

**Key takeaway**
- Clearly state the source, the target (language, tone, format, style), and any edge-case handling. The model handles the rest.








**Expanding with Prompts**

**What "expanding" means**
- Turning short input (instructions, a topic list) into longer text, such as an email or essay.
- **Good uses:** brainstorming partner, personalized replies.
- **Responsible use:** don't use it for harmful things like mass spam.

**Example: AI customer-service email reply**
- **Assign a role:** e.g. "You are a customer service AI assistant."
- **Use delimiters** around the customer review.
- **Add conditional logic in the prompt:**
  - Positive or neutral sentiment: thank the customer.
  - Negative sentiment: apologize and suggest contacting customer service.
- **Ask for specific details:** e.g. "use specific details from the review" so the reply feels personal.
- **Set tone and length:** e.g. "concise and professional tone."
- **Be transparent:** sign as "AI customer agent." Users should know when text is AI-generated.
- **Chain tasks:** first extract sentiment (as in the inferring lesson), then write the reply. Or do both in one prompt.

**Temperature parameter**
- Controls the **randomness or exploration** of the model's output.
- **Temperature 0:** always picks the most likely next word, so the same prompt gives the same output.
  - Use it for **reliable, predictable** applications (the recommended default).
- **Higher temperature (e.g. 0.7):** sometimes picks less likely words, so outputs differ on every run.
  - Use it for **creative** tasks where you want variety.
- At higher temperatures the model is more creative but also more "distractible," and responses diverge more as they get longer.

**Key takeaway**
- For generated text, give a role, conditions, tone, and transparency rules in the prompt, and choose the temperature based on whether you need consistency or creativity.









**Building a Chatbot with Prompts**

**Chat completions format**
- Chat models take a **list of messages** as input and return one **assistant message** as output.
- The format suits multi-turn conversations, but it also works for single-turn tasks.

**Message roles**
- **System:** sets the overall behavior and persona (e.g. "You are an assistant that speaks like Shakespeare").
  - It's like whispering in the assistant's ear: it guides responses without the user seeing it.
  - It lets the developer frame the conversation without making the instruction part of the chat.
- **User:** the person's messages.
- **Assistant:** the model's replies. The response object has `role: assistant` and `content`.

**Context and memory**
- Each API call is **stateless**. The model doesn't remember earlier calls.
- To make it "remember," **send the full conversation history** (all previous user and assistant messages) with every call.
- Example: when the name "Isa" was in earlier messages, the model knew it; without that history, it didn't.

**Building OrderBot (pizza ordering)**
- Keep a `context` list: **append every user message and assistant reply** and send the growing list on each call.
- The **system prompt defines the whole workflow:**
  - Greet, collect the order, ask pickup or delivery.
  - Summarize the order and ask if anything else is needed.
  - Get the address if it's a delivery, then collect payment.
  - Clarify all options, extras, and sizes so each item is uniquely identified.
  - Respond in a short, friendly, conversational style.
  - **Include the menu** (the knowledge it needs) right in the system message.

**Converting the conversation to structured output**
- At the end, add one more instruction (system or user message): "Create a JSON summary of the order," listing the fields (pizza, toppings, drinks, sides, total price).
- The resulting JSON can go straight to an order system.

**Temperature tips**
- **Low temperature** for structured or predictable output, such as the JSON summary or a customer-service bot.
- **Higher temperature** for more varied, creative conversation.

**Key takeaway**
- The system message is your main control tool: persona, rules, workflow steps, and knowledge. Always pass the full context to keep the conversation coherent, and end with a structured-output instruction when code needs the data.
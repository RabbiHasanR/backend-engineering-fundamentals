
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
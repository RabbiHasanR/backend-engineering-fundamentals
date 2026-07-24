YAGNI = your aren't gonna nead it


1. What Is the YAGNI Principle?
“Always implement things when you actually need them, never when you just foresee that you need them.” — Ron Jeffries, co-founder of Extreme Programming

YAGNI is a principle that encourages you to resist the temptation to build features or add flexibility until you are absolutely sure you need them.

In simple terms: Don’t build for tomorrow. Build for today.

The principle comes from Extreme Programming (XP), one of the earliest Agile methodologies. XP was built around the idea that software requirements change constantly, so spending time building for predicted futures is wasteful. Instead, you deliver the simplest thing that works right now, and you iterate from there.

YAGNI fits perfectly into this philosophy: if you don't know for certain that a feature is needed, don't build it. When the need actually arises, you'll have far better information about what to build and how to build it.

This doesn't mean you write sloppy code or ignore good design. It means you don't add layers of abstraction, extra interfaces, or speculative features until a real requirement justifies them. There's a big difference between writing clean, well-structured code for today's needs and over-engineering for tomorrow's imagined ones.



Why Premature Work Is Harmful
You might think, "What's the harm in being prepared?" Quite a lot, actually. Every line of speculative code carries hidden costs that compound over time.

1. Wasted Time and Effort
Every hour spent building features that are not needed is time not spent building what actually matters. In the image upload example, the developer spent time writing CloudStorageAdapter, MediaHandlerFactory, and IStorageProvider before even one user uploaded a profile photo. That's development time, code review time, and testing time, all spent on features with zero users.

2. Increased Complexity
Extra flexibility adds more moving parts. It becomes harder to understand, test, and modify your code. A new developer joining the team sees the MediaProcessingEngine with its factory and provider interfaces and assumes there's a reason for all that complexity. They're afraid to simplify it because they think "someone must have needed this." The speculative code becomes permanent by accident.

3. Delayed Value
By working on "someday" features, you delay shipping the features users need today. If the simple image uploader could have been done in an afternoon but the overengineered version took a week, you've delayed value delivery by four days, all for features nobody asked for.

4. Higher Maintenance Costs
Even unused features have a cost. They can introduce bugs, require updates when dependencies change, and get in the way of refactoring. When you want to upgrade your storage library, you now have to update both LocalStorage and CloudStorageAdapter, even though nobody uses the cloud adapter. Dead code is not free. It's debt.



4. When to Bend the Rule
Like all principles, YAGNI has exceptions. Sometimes, planning ahead is justified. The key is distinguishing between speculative features (driven by "what if") and known constraints (driven by real requirements, regulations, or contractual obligations).

Security and Compliance
If you're building a system that handles financial data, health records, or personal information, you may need audit trails, encryption, and access controls from day one. These aren't speculative features. They're legal requirements.

Architecture with Known Long-Term Constraints
If you're building a system that has contractual SLAs for uptime, or you know from the start that it must handle cross-region replication, some architectural decisions need to be made early. Retrofitting high availability into a system that wasn't designed for it is far more expensive than building it in from the start.

Reusable Libraries or Frameworks
If you're building a library that other teams will depend on, some flexibility is expected. API design for libraries requires more upfront thought because breaking changes affect many consumers. But even here, start with a minimal API and expand it based on actual usage patterns.

The common thread in all these exceptions: the need is known and concrete, not imagined. You're not guessing that you might need audit logging. You know you need it because the law says so.
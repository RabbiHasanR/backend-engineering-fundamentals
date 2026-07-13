Example 1:

"In my experience, most of my conflicts have been about technical decisions, never personal — and I actually think healthy debate makes the product better. Let me share a recent example.
I was leading a team of two junior engineers building a task management service. My project manager gave us a database design with three separate tables for three types of tasks. I disagreed with this approach. As a senior backend engineer, I felt one table with a 'type' column was the right design — it's simpler to develop, easier to maintain, and much more flexible when we add or remove features in the future.
At first, we both held our positions and the discussion got a bit heated. So I stepped back, and later I came to him with a calm mind — but this time, instead of pushing my solution, I asked him why he wanted three tables. That changed everything.
He explained his concern: the service would handle a huge volume of tasks, and his long-term plan was to make it multi-tenant, where each company gets its own task management. He was worried a single table wouldn't scale.
Once I understood his real concern, I could address it directly. I showed him that a single table with proper indexing and partitioning can easily handle millions of rows with fast queries. And for scaling later, sharding is much easier from one table — but merging three tables back into one would be very painful. I also proposed that for multi-tenancy, we could give each company its own database using the same single-table schema.
He agreed, and we went with the single-table design. It worked well in production.
The big lesson for me: when I disagree, my first job is not to prove I'm right — it's to understand the other person's reasoning. Most conflicts happen because two people are solving two different problems without realizing it. Once we aligned on the actual problem, the solution became obvious to both of us."





Example 2:

"Most of my conflicts have been technical, never personal — and I believe respectful debate usually leads to a better solution. Let me give you a recent example.
I was working on building a CI/CD pipeline for one of our services. One of my teammates wanted to automate everything through this pipeline — not just code integration and deployment, but also infrastructure setup: creating EC2 instances, configuring the database, installing Node, Python, and other packages and tools.
I disagreed with this approach. In my view, CI/CD has one clear purpose — continuous integration, testing, and deployment of code. If we mix infrastructure provisioning and configuration into it, the pipeline becomes heavy, complex, and hard to maintain. And when a pipeline tries to do everything, it usually ends up doing its main job poorly.
At first, we went back and forth, and honestly he had a fair point — he wanted everything automated in one place so nothing would be manual. I agreed with his goal, just not his method. So instead of only saying 'no,' I proposed an alternative: we keep the pipeline focused on build, test, and deploy, and we handle infrastructure with the right tool for that job — Terraform, which is the industry standard for provisioning and configuration. That way, everything is still automated, just separated by responsibility.
I walked him through the benefits: the pipeline stays fast and simple, infrastructure changes are version-controlled separately, and if something breaks, it's much easier to debug because each tool has one clear responsibility.
He agreed, and we implemented it that way. The pipeline stayed clean and easy to maintain, and infrastructure changes became safer and repeatable.
What I learned is that in most conflicts, both people actually want the same outcome — in this case, full automation. The disagreement is usually about the method. So I try to first agree on the shared goal, then discuss the best way to reach it. That turns a conflict into a design discussion."
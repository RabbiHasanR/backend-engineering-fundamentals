LSP is about Behavior: Can I swap a superclass with its subclass without the application crashing or behaving unexpectedly?

ISP is about Architecture: Am I forcing a client to depend on methods it doesn't need and will never use?



applying solid principles to services:

This actually a very interesting topic. I have noticed that as microservices have taken hold, many engineers are finding that object-oriented languages and design practices have become less useful (assuming their services are reasonably small and self-contained), and are shifting to languages like Go, Rust and others which they feel are less burdensome and easier to work with. The organizing principles around good design of large OO systems don’t seem as important at that scale.

But those principles are actually still very important; they just have relocated to the connections between services. Essentially what has happened is that the composition of large systems is shifting from large object-oriented monoliths to a large network of cooperating services.

Now instead of asking “how big should my class be?” people are asking “how big should my service be?” Instead of asking “how can I safely substitute one implementation of a class with another?” we ask “how do I refactor and evolve my services without breaking my clients?” It is the same problems and questions with a different implementation model.

With this in mind, let’s see if we can map the SOLID principles from classes to services…
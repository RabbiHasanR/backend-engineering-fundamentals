Interfaces: 

An interface is a contract: methods without implementation
Many classes can implement in differently
Depend on the interface not the concrete class
This gives you polymorphism and dependency injection
Result: code that is easy to extend, test and change


Program to an interface not an implementation.

1. What is an Interface?
At its core, an interface is a contract: a list of methods that any implementing class must provide. It specifies a set of behaviors that a class agrees to implement but leaves the details of those behaviors up to each implementation.

In other words:

An interface defines the "what", while classes provide the "how".


2. Key Properties of Interfaces
Interfaces are more than just method declarations, they are the foundation of flexible software design.

Here are their most important characteristics:

a) Defines Behavior Without Dictating Implementation
An interface only declares what operations are expected. It doesn’t define how they are carried out.

This gives freedom to implementers to provide their own version of the logic, while still honoring the same contract.

b) Enables Polymorphism
Different classes can implement the same interface in different ways.This allows your code to work with multiple implementations interchangeably.

c) Promotes Decoupling
Code that depends on interfaces is insulated from changes in the concrete classes that implement them.

This makes your code easier to:

Extend (add new implementations without modifying existing ones),
Test (mock interfaces in unit tests),
Maintain (fewer ripple effects from code changes).



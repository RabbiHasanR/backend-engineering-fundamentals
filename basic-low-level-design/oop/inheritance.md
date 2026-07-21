Inheritance:

A subclass inherits the parents fields and methods

It can override behavior and add new behavior

Models is-a relationships and remove duplication

Watch out for deep trees and the diamond problem

Use it for true is-a; otherwise compose


Keep shared behavior in a parent. Add specialization in children. Keep your hierarchies shallow.




Inheritance

Inheritance allows one class (called the subclass or child class) to inherit the properties and behaviors of another class (called the superclass or parent class).

In simpler terms:

Inheritance enables code reuse by letting you define common logic once in a base class and then extend or specialize it in multiple derived classes.

This leads to cleaner, modular, and more maintainable software.








1. Why Inheritance Matters
Inheritance offers several benefits that make it a powerful design tool in OOP.

1. Code Reusability
It embodies the DRY (Don't Repeat Yourself) principle. Common logic is written once in the parent class and shared across all subclasses reducing redundancy.

2. Logical Hierarchy
It creates a clear and intuitive hierarchy that model real-world “is-a” relationships like ElectricCar is a Car or Admin is a User.

3. Ease of Maintenance
If a bug is found or a change is needed in the shared logic, you only need to fix it in one place, the superclass. All subclasses automatically inherit the fix.

4. Polymorphism
Inheritance is a prerequisite for polymorphism, allowing objects of different subclasses to be treated as objects of the superclass.



2. How Inheritance Works
When a class inherits from another:

The subclass inherits all non-private fields and methods of the superclass.
The subclass can override inherited methods to provide a different implementation.
The subclass can also extend the superclass by adding new fields and methods.
This allows for both reuse and customization.









3. Types of Inheritance
Not all inheritance hierarchies look the same. There are several common patterns, each with its own structure and trade-offs.

Single Inheritance is the simplest form: one child class extends one parent class. The ElectricCar extends Vehicle relationship is single inheritance. This is the most common pattern and the one supported by all major languages.

Multi-level Inheritance is when a child class itself becomes a parent. For example, Vehicle -> Car -> ElectricCar. Each level adds more specialization. This is fine in moderation, but deep chains (5+ levels) become fragile and hard to understand.

Hierarchical Inheritance is when multiple child classes extend the same parent. Our vehicle example, where both ElectricCar and GasCar extend Vehicle, is hierarchical inheritance. This is extremely common and perfectly natural.


Multiple Inheritance is when a child class extends more than one parent. This is where things get complicated. Only C++ and Python support multiple inheritance directly. Java, C#, and TypeScript do not. The reason? The diamond problem.

Imagine ElectricCar extends both Vehicle and Machine. Both Vehicle and Machine have a start() method. When you call electricCar.start(), which version runs? The one from Vehicle? The one from Machine? Both?

C++ handles this with virtual inheritance, which is complex and error-prone. Python handles it with the Method Resolution Order (MRO), a well-defined algorithm (C3 linearization) that determines which parent's method takes priority. Java and C# sidestep the problem entirely by only allowing single class inheritance, you can implement multiple interfaces, but extend only one class.



4. When to Use Inheritance
Inheritance is powerful, but it should be used intentionally, only when it truly models a real-world relationship. Getting this decision wrong early in your design leads to code that's hard to change, hard to test, and hard to reason about.

Here's a practical checklist.

Use inheritance when:
There is a clear "is-a" relationship (e.g., Dog is an Animal, Car is a Vehicle). If you can't say "X is a Y" naturally, inheritance is probably the wrong tool. These relationships belong in composition.
The parent class defines common behavior or data that children should share. For example, all vehicles have a startEngine() method, so putting it in the parent avoids duplicating it across every vehicle type.
The child class does not violate the behavior expected from the parent. If someone has a Vehicle reference pointing to an ElectricCar, every Vehicle method should still work as expected.
You want to promote code reuse through shared logic and structure, and the hierarchy is shallow (2-3 levels at most).
Avoid inheritance when:
The relationship is "has-a" or "uses-a" rather than "is-a". A Car has an Engine, it is not an Engine. A Printer uses a Logger, it is not a Logger.
You want to combine behaviors from multiple sources dynamically. Inheritance locks you into a single parent at compile time, while composition lets you mix and match components freely.
You need runtime flexibility to swap behaviors. With composition, you can inject different implementations (swap a FileLogger for a ConsoleLogger). With inheritance, the parent relationship is fixed.
You want to avoid tight coupling between child and parent internals. Changes to a parent class ripple down to every child in the hierarchy, which is risky in large codebases.
When in doubt, start with composition. You can always refactor toward inheritance later if a genuine "is-a" hierarchy emerges. Going the other direction, untangling a deep inheritance tree into composition, is much harder.
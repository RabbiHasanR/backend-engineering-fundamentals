Polymorphism:

Same method call, different behavior per object

Overloading is resolved at compile time

Overriding is resolved at runtime

Program to a base type: the real type dispatches

Add new types without changing the caller



One interface, many behaviors, chosen at runtime.



Polymorphism

Polymorphism allows the same method name or interface to exhibit different behaviors depending on the object that is invoking it.

The term "polymorphism" comes from Greek and means "many forms." In programming, it allows us to write code that is generic, extensible, and reusable, while the specific behavior is determined at runtime or compile-time based on the object’s actual type.

Polymorphism lets you call the same method on different objects, and have each object respond in its own way.

You write code that targets a common type, but the actual behavior is determined by the concrete implementation.



Why Polymorphism Matters
 Here are four concrete benefits that polymorphism provides.

Encourages loose coupling: You interact with abstractions (interfaces or base classes), not specific implementations.
Enhances flexibility: You can introduce new behaviors without modifying existing code, supporting the Open/Closed Principle.
Promotes scalability: Systems can grow to support more features with minimal impact on existing code.
Enables extensibility: You can “plug in” new implementations without touching the core business logic



How Polymorphism Works
Polymorphism in OOP comes in two forms: compile-time (decided before the program runs) and runtime (decided while the program runs). Both allow the same method name to behave differently, but the mechanism is fundamentally different.


1. Compile-time Polymorphism (Method Overloading)
Compile-time polymorphism, also called method overloading, happens when you have multiple methods with the same name in the same class but with different parameter lists.

The compiler determines which version to call based on the number, types, or order of arguments at the call site. The decision is made before the program runs.

```python
# Python does NOT support method overloading natively.
# If you define multiple methods with the same name, only the last one survives.
# The standard workaround is to use default arguments or *args.

class Calculator:
    def add(self, *args):
        return sum(args)


calc = Calculator()
print(calc.add(2, 3))        # 5
print(calc.add(2.5, 3.5))    # 6.0
print(calc.add(1, 2, 3))     # 6
```

The compiler resolves which add() to call based on the arguments. Pass two ints, you get add(int, int). Pass two doubles, you get add(double, double). Pass three ints, you get add(int, int, int). No runtime decision needed.


2. Runtime Polymorphism (Method Overriding / Dynamic Dispatch)
Runtime polymorphism is the more powerful and more important form. It happens when a child class overrides a method defined in its parent class, and the decision of which version to call is made at runtime based on the actual type of the object, not the declared type of the reference.
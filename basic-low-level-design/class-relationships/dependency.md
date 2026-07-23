1. What is Dependency?
A Dependency exists when one class relies on another to fulfill a responsibility, but does so without retaining a permanent reference to it.

This typically happens when:

A class accepts another class as a method parameter.
A class instantiates or uses another class inside a method.
A class returns an object of another class from a method.
Key Characteristics of Dependency
Short-lived: The relationship exists only during method execution.
No ownership: The dependent class does not store the other as a field.
"Uses-a" relationship: The class uses another to accomplish a task, but does not retain it.


Real-World Analogy

Imagine a Chef preparing a meal.

The chef picks up a Knife to chop vegetables.
Once the chopping is done, the knife is put away or reused elsewhere.
The chef doesn’t necessarily own the knife or keep it stored long-term.
This represents a dependency. The chef depends on the knife only during the cooking process.



4. Recognizing Dependencies in Code
Dependencies can appear in several common forms within a class:

As Method Parameters
This is the most common and most recognizable form of dependency. The dependent class receives another class as a parameter, uses it during the method, and lets it go.

```python
class ReportGenerator:
    def generate(self, source):
        data = source.fetch_all()
        # Format data into report...
        return formatted_report
```

ReportGenerator depends on DataSource, but doesn't store it. The DataSource comes in, gets used, and is gone once generate() returns.


As Local Variables
Sometimes a class creates another class inside a method, uses it, and discards it. The created object never escapes the method scope.

```python
class OrderProcessor:
    def process(self, order):
        formatter = JsonFormatter()
        json = formatter.format(order)
        # Send json to external API...
```

OrderProcessor depends on JsonFormatter, but the formatter is a local variable. It's created inside the method and disappears when the method ends. No field, no structural link.

As Return Types
A method can return an object of another class, creating a dependency on that type even if the class doesn't store it.

```python
class UserFactory:
    def create_user(self, name, email):
        return User(name, email)
```
UserFactory depends on User because it creates and returns User objects, but it doesn't store any User as a field. The factory's job is to produce users, not to hold onto them.

As Static Method Calls
A class can depend on another class by calling its static methods. There's no object reference at all, just a class-level dependency.
```python
class PasswordService:
    def verify(self, input_text, hash_value):
        return HashUtils.sha256(input_text) == hash_value
```

PasswordService depends on HashUtils, but there's no instance of HashUtils stored anywhere. The dependency is purely at the class level through a static call.



5. Dependency Injection (DI)
In real-world applications, classes often depend on other classes to get their work done.

A UserService might rely on a DatabaseClient to fetch users, or a NotificationService might rely on an EmailSender to send messages.

But how should these dependencies be provided?

You could let the class create its own dependencies internally but that leads to tight coupling, making your code rigid and hard to test.

A better approach is to inject those dependencies from the outside.

This is called Dependency Injection (DI), one of the most powerful principles in modern software design.

Dependency Injection is a design technique where a class receives the objects it depends on, instead of creating them itself.

This leads to:

Better testability: You can inject mock dependencies during unit tests.
Greater modularity: Swap implementations (e.g., EmailSender → SMSSender) without changing core logic.
Loose coupling: Classes only depend on abstract contracts (interfaces), not concrete implementations.
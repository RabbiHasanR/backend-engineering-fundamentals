# The Definitive Guide to Python Decorators

**Table of Contents**

1. [Core Concepts: The Foundation](https://www.google.com/search?q=%231-core-concepts-the-foundation)
2. [What is a Decorator?](https://www.google.com/search?q=%232-what-is-a-decorator)
3. [Types of Decorators](https://www.google.com/search?q=%233-types-of-decorators)
4. [Advanced Mechanics](https://www.google.com/search?q=%234-advanced-mechanics)
5. [Under the Hood: Memory & Closures](https://www.google.com/search?q=%235-under-the-hood-memory--closures)
6. [Real-World Use Cases (Scenarios)](https://www.google.com/search?q=%236-real-world-use-cases-scenarios)
7. [Interview Preparation Guide](https://www.google.com/search?q=%237-interview-preparation-guide)

---

## 1. Core Concepts: The Foundation

To understand decorators, you must accept three truths about Python functions:

### A. Functions are First-Class Objects

In Python, functions are just like variables (integers, strings). You can pass them as arguments, return them from other functions, or assign them to variables.

```python
def shout(text):
    return text.upper()

# 1. Assign to variable
yell = shout 

# 2. Pass as argument
def greet(func):
    print(func("hi"))

greet(yell) # Output: HI

```

### B. Nested Functions

You can define a function inside another function. The inner function is hidden from the global scope.

### C. Closures (The Magic Sauce)

A **closure** occurs when a nested function "remembers" variables from its enclosing scope, even after the outer function has finished executing. This is the mechanism that allows decorators to work.

---

## 2. What is a Decorator?

A decorator is a design pattern that allows you to **dynamically add functionality** to a function (or class) without changing its source code.

### The Syntax Sugar

The `@` symbol is merely a shortcut (syntactic sugar).

**This code:**

```python
@my_decorator
def say_hello():
    print("Hello")

```

**Is exactly equivalent to this code:**

```python
def say_hello():
    print("Hello")

say_hello = my_decorator(say_hello)

```

### The Basic Skeleton

Every basic decorator follows this structure:

1. **Outer Function:** Accepts the function you want to decorate (`func`).
2. **Inner Function (Wrapper):** The logic you want to add. It calls `func()`.
3. **Return:** The outer function returns the `wrapper`.

```python
def simple_decorator(func):
    def wrapper():
        print("Before the function runs")
        func()
        print("After the function runs")
    return wrapper

```

---

## 3. Types of Decorators

### A. Decorator with Arguments (Parametrized)

If you want to pass settings to the decorator (e.g., `@repeat(5)`), you need **three** layers of functions.

```python
def repeat(times):
    # Layer 1: Accepts arguments
    def decorator(func):
        # Layer 2: Accepts the function
        def wrapper(*args, **kwargs):
            # Layer 3: The logic
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hi {name}")

```

### B. Class-Based Decorators (Classes as Decorators)

Instead of a function, you can use a class. This is useful if your decorator needs to maintain complex state (like a count). You must implement `__call__`.

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.num_calls = 0

    def __call__(self, *args, **kwargs):
        self.num_calls += 1
        print(f"Call #{self.num_calls}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    pass

```

### C. Class Decorators

These decorate an entire **Class** definition, not just a function. They typically modify attributes or methods of the class.

```python
def add_timestamp(cls):
    cls.created_at = "2023-10-27"
    return cls

@add_timestamp
class User:
    pass

print(User.created_at) # Output: 2023-10-27

```

---

## 4. Advanced Mechanics

### Chaining Decorators

You can stack multiple decorators. They are applied from **bottom to top**.

```python
@bold   # Applied 2nd
@italic # Applied 1st
def text():
    return "Hello"

```

Equivalent to: `bold(italic(text))`

### Preserving Metadata (`functools.wraps`)

By default, a decorator "hides" the original function's name and docstring. Always use `functools.wraps` to fix this.

```python
import functools

def explicit_decorator(func):
    @functools.wraps(func) # <--- CRITICAL
    def wrapper(*args, **kwargs):
        """Wrapper docstring"""
        return func(*args, **kwargs)
    return wrapper

@explicit_decorator
def my_func():
    """Original docstring"""
    pass

print(my_func.__name__) # Prints "my_func" (Correct). 
# Without @wraps, it would print "wrapper".

```

---

## 5. Under the Hood: Memory & Closures

This section explains how Python manages memory for decorators.

### The Stack vs. The Heap

1. **The Stack:** When `my_decorator(func)` is called, a stack frame is created. The local variable `func` exists here.
2. **The Heap:** The function object itself lives here.

### The "Cell" Object

When the stack frame for `my_decorator` is destroyed (when it returns), the variable `func` *should* disappear. However:

1. Python detects that the inner `wrapper` function refers to `func`.
2. It creates a **Cell Object** on the Heap.
3. This Cell stores the reference to the original function.
4. The `wrapper` has a hidden attribute `__closure__` that points to this Cell.

This is why the original function is not garbage collected: **The Wrapper keeps it alive via the Closure Cell.**

```python
# Inspecting the memory
def make_closure(x):
    def inner():
        print(x)
    return inner

fn = make_closure(10)
# You can actually see the hidden cell!
print(fn.__closure__[0].cell_contents) # Output: 10

```

---

## 6. Real-World Use Cases (Scenarios)

### Scenario A: Execution Timer (Performance Testing)

```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

```

### Scenario B: Authentication Guard (Security)

```python
current_user = {"role": "guest"}

def require_admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if current_user["role"] != "admin":
            raise PermissionError("Admins only!")
        return func(*args, **kwargs)
    return wrapper

```

### Scenario C: Memoization (Caching)

Useful for expensive recursive functions (like Fibonacci).

```python
def memoize(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

```

---

## 7. Interview Preparation Guide

### Top 5 Interview Questions

1. **What is a decorator exactly?**
* *Answer:* It is a callable (function or class) that takes a function as input and returns a replacement function (usually a wrapper) to extend behavior without modifying the original source code.


2. **What happens if you don't use `@functools.wraps`?**
* *Answer:* The decorated function loses its metadata (`__name__`, `__doc__`). Debugging becomes difficult because tracebacks will show `wrapper` instead of the actual function name.


3. **Explain "Closure" in the context of decorators.**
* *Answer:* A closure is a function object that remembers values in enclosing scopes even if they are not present in memory. In decorators, the closure allows the `wrapper` to access the original `func` even after the decorator setup logic has finished.


4. **Can you decorate a class?**
* *Answer:* Yes. A class decorator takes the class object `cls`, modifies it (e.g., adds methods or attributes), and returns it.


5. **What is the difference between `@staticmethod` and `@classmethod`?**
* *Answer:* `@staticmethod` works like a regular function (no `self` or `cls` argument). `@classmethod` receives the class (`cls`) as the first argument, allowing access to class state but not instance state.



### Tricky Scenario: "Side Effects"

**Q:** When does the code *inside* the decorator (but outside the wrapper) run?
**A:** It runs at **Import Time** (when Python reads the file), not at **Runtime** (when the function is called).

```python
def my_dec(func):
    print("I run immediately!") # <--- Runs at import
    def wrapper():
        print("I run when called!")
        func()
    return wrapper

@my_dec
def foo():
    pass
# Output (just by running the script): "I run immediately!"

```
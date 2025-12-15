
### **What is `defaultdict`?**

`defaultdict` is a subclass of the built-in `dict` class. It is available in the `collections` module.

The key difference is that a standard dictionary raises a `KeyError` if you try to access or modify a key that doesn't exist. A `defaultdict`, however, will automatically create a default value for that key if it is missing, using a factory function you provide.

### **How It Works Under the Hood**

When you initialize a `defaultdict`, you pass a callable (a function or a class) as the first argument. This is stored in an attribute called `default_factory`.

1.  **Accessing a Missing Key:** When you try to access `d[key]` and the key is missing, Python calls the dictionary's `__missing__(key)` method.
2.  **Triggering the Factory:** For a standard `dict`, `__missing__` simply raises a `KeyError`. For `defaultdict`, the `__missing__` method calls the `default_factory` (with no arguments).
3.  **Insertion:** The value returned by `default_factory` is inserted into the dictionary for that key.
4.  **Return:** The new value is returned to you.

If `default_factory` is `None`, `defaultdict` behaves exactly like a standard dictionary and raises a `KeyError` for missing keys.

-----

### **Basic Syntax**

```python
from collections import defaultdict

# Syntax: defaultdict(default_factory)
d = defaultdict(int) 
```

### **Common Examples**

#### **1. Default Value as Integer (Counting)**

This is the most common use case. When you access a missing key, `int()` is called, which returns `0`. This is perfect for counters.

```python
from collections import defaultdict

# Standard dict way (requires checking if key exists)
text = "banana"
counts = {}
for char in text:
    if char in counts:
        counts[char] += 1
    else:
        counts[char] = 1

# defaultdict way
counts = defaultdict(int)
for char in text:
    counts[char] += 1 # If 'b' is missing, counts['b'] becomes int() -> 0, then add 1

print(dict(counts)) 
# Output: {'b': 1, 'a': 3, 'n': 2}
```

#### **2. Default Value as List (Grouping)**

When accessing a missing key, `list()` is called, returning an empty list `[]`. You can immediately append to it.

```python
from collections import defaultdict

data = [('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]
grouped_data = defaultdict(list)

for color, number in data:
    grouped_data[color].append(number)

print(dict(grouped_data))
# Output: {'yellow': [1, 3], 'blue': [2, 4], 'red': [1]}
```

#### **3. Default Value as Set (Unique Grouping)**

Using `set` as the factory ensures that the grouped values are unique.

```python
from collections import defaultdict

data = [('A', 'user1'), ('B', 'user2'), ('A', 'user1'), ('A', 'user3')]
unique_visitors = defaultdict(set)

for page, user in data:
    unique_visitors[page].add(user)

print(dict(unique_visitors))
# Output: {'A': {'user1', 'user3'}, 'B': {'user2'}}
```

-----

### **Advanced: Custom Default Factory**

You are not limited to built-in types like `int` or `list`. You can use a lambda or a custom function.

**Example: Default value is "N/A"**

```python
def default_value():
    return "N/A"

d = defaultdict(default_value)
d['name'] = 'Alice'

print(d['name'])   # Output: Alice
print(d['age'])    # Output: N/A (Created automatically)
```

**Example: Using Lambda**

```python
# Default value is always 100
d = defaultdict(lambda: 100)
print(d['score']) # Output: 100
```

-----

### **Important "Gotcha": The `__missing__` Method**

The `default_factory` is **only** called when you access items using `__getitem__` (brackets `[]`). It is **not** called for `.get()`.

```python
d = defaultdict(int)

# This triggers the factory
print(d['missing_key']) # Output: 0 (and 'missing_key': 0 is added to dict)

# This DOES NOT trigger the factory
print(d.get('another_missing_key')) # Output: None
print('another_missing_key' in d)   # Output: False
```

### **Summary Comparison**

| Feature | Standard `dict` | `collections.defaultdict` |
| :--- | :--- | :--- |
| **Missing Key Access** | Raises `KeyError` | Calls `default_factory` & inserts value |
| **Instantiation** | `d = {}` or `dict()` | `d = defaultdict(factory)` |
| **Methods** | Standard methods | Same standard methods + `__missing__` |
| **Best For** | General mapping | Counting, Grouping, Accumulating |


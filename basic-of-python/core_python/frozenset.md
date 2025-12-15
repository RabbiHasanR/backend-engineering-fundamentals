### 1\. What is a `frozenset`?

A `frozenset` is an **immutable**, **unordered** collection of unique elements.

  * **Immutable:** Once created, you cannot add, remove, or update elements.
  * **Hashable:** Because it is immutable, it has a hash value. This allows it to be used as a **key in a dictionary** or an **element in another set** (which a standard `set` cannot do).
  * **Unordered:** Like a standard set, it does not record element position or insertion order.

**Analogy:** Think of a `set` like a whiteboard where you can write and erase names. A `frozenset` is like a stone tablet; once the names are carved, they are permanent.

-----

### 2\. Methods & Complexity Analysis

Below is the complexity for every method available to `frozenset`.

  * **$n$**: Number of elements in the frozenset (`self`).
  * **$m$**: Number of elements in the other set (`other`).

| Method | Description | Time Complexity (Avg) | Space Complexity |
| :--- | :--- | :--- | :--- |
| **`copy()`** | Returns a reference to itself (optimization). | $O(1)$ | $O(1)$ |
| **`difference(...)`** (`-`) | Returns new set with elements in `self` but not in `other`. | $O(n)$ | $O(n)$ |
| **`intersection(...)`** (`&`) | Returns new set with elements common to both. | $O(\min(n, m))$ | $O(\min(n, m))$ |
| **`union(...)`** (`\|`) | Returns new set with elements from both. | $O(n + m)$ | $O(n + m)$ |
| **`symmetric_difference(...)`** (`^`) | Returns elements in either set, but not both. | $O(n + m)$ | $O(n + m)$ |
| **`isdisjoint(...)`** | Returns `True` if no common elements. | $O(\min(n, m))$ | $O(1)$ |
| **`issubset(...)`** (`<=`) | Returns `True` if all elements of `self` are in `other`. | $O(n)$ | $O(1)$ |
| **`issuperset(...)`** (`>=`) | Returns `True` if all elements of `other` are in `self`. | $O(m)$ | $O(1)$ |
| **`__hash__()`** | Computes the hash value (cached after first call). | $O(n)$ (first call)<br>$O(1)$ (subsequent) | $O(1)$ |
| **`__contains__`** (`in`) | Checks if a value exists in the set. | $O(1)$ | $O(1)$ |
| **`__iter__`** | Iterates over the set. | $O(n)$ | $O(1)$ |

> **Note on `copy()`:** Since `frozenset` is immutable, `copy()` does not create a new object in memory. It simply returns a reference to the existing object (incrementing the reference count), making it extremely fast.

-----

### 3\. Under the Hood: Internal Implementation

Python's `frozenset` is implemented in C as part of the CPython interpreter.

#### The C Structure (`PySetObject`)

Surprisingly, `frozenset` and `set` share the exact same C struct: `PySetObject`.

```c
typedef struct {
    PyObject_HEAD
    Py_ssize_t fill;      // Number of active + dummy entries
    Py_ssize_t used;      // Number of active entries (len(s))
    Py_ssize_t mask;      // Table size mask (size - 1)
    setentry *table;      // Pointer to the hash table
    Py_hash_t hash;       // Holds the hash value (unique to frozenset)
    setentry smalltable[PySet_MINSIZE]; // Small optimization array
} PySetObject;
```

**Key Differences in the Struct:**

1.  **`hash` field:**
      * In a **`set`**, this field is generally unused or set to -1 because sets are unhashable.
      * In a **`frozenset`**, this field caches the hash value. The first time you call `hash(my_frozen_set)`, Python computes the hash by XORing the hashes of all elements (making it order-independent) and stores it here. Future calls simply return this stored value, making dictionary lookups very fast.
2.  **`table` pointer:** Points to an array of `setentry` structs, which hold the stored items and their cached hashes.

#### Hash Collision Resolution

Like `set` and `dict`, `frozenset` uses **open addressing** with **linear probing** (modified) to handle collisions. If two elements hash to the same slot, Python checks the next slot according to a perturbation algorithm until an empty spot is found.

-----

### 4\. Memory Management

Memory handling is where `frozenset` shines compared to `set`.

#### 1\. No Over-Allocation for Growth

A standard mutable `set` must allocate extra memory (growth factor) to accommodate future insertions without needing a costly resize operation immediately.

  * **`set`**: Allocates a table roughly 2x to 4x larger than the data to keep the "load factor" low.
  * **`frozenset`**: Since the size is fixed at creation, Python calculates the exact table size needed to hold the elements with a reasonable load factor (usually 2/3 full). It **never** needs to resize.

#### 2\. Singleton Optimization

Python optimizes memory for the empty `frozenset`.

```python
f1 = frozenset()
f2 = frozenset([])
print(f1 is f2)  # True
```

There is only one empty `frozenset` object in memory, shared across the entire interpreter session.

#### 3\. Compactness

Because it doesn't need to support resize operations or "dummy" entries (placeholders for deleted items), `frozenset` often occupies fewer bytes than a `set` with the same elements.

**Memory comparison example:**

```python
import sys
s = {1, 2, 3}
f = frozenset({1, 2, 3})

print(sys.getsizeof(s))  # Often ~216 bytes
print(sys.getsizeof(f))  # Often ~216 bytes (initially similar)
```

*Wait, why are they similar?*
If you create a set and *then* convert it to a frozenset, Python often reuses the underlying memory buffer or allocates a similar size. The savings appear when you have a large `set` that has undergone many add/delete cycles (which fragments the internal table) versus a `frozenset` which is packed tightly from the start.

### Summary: Why use `frozenset`?

1.  **Functional correctness:** You need a set as a dictionary key (e.g., storing edge weights in a graph where nodes are sets).
2.  **Performance:** You want to signal to the reader (and the interpreter) that this data **will not change**.
3.  **Safety:** It prevents accidental modification of critical reference data.

### Next Step

Would you like to see a practical code example of using `frozenset` as a dictionary key for a memoization (caching) algorithm?
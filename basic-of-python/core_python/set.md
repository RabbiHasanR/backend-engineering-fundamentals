To answer your specific question first: **No, Python Sets do NOT use the "Two-Array" (Indices + Entries) layout that modern Python Dictionaries use.**

While modern Dictionaries (Python 3.6+) split data into a sparse *Indices Array* and a dense *Entries Array* to preserve insertion order and save memory, **Sets** use a simpler **Single Sparse Array** architecture. Because sets do not need to preserve insertion order, they stick to a traditional, highly optimized open-addressing hash table structure.

Below is the fully updated article reflecting this internal architecture.

-----

# The Definitive Guide to Python Sets: Internals, Complexity, and Methods

In Python, a **Set** is a mutable collection of unique, immutable elements. It is engineered for one specific goal: $O(1)$ membership testing. Unlike modern Dictionaries, which are ordered, Sets remain **unordered**.

## 1\. Internal Architecture: The Single Sparse Array

Unlike the modern Python `dict` (which uses two arrays: one for indices, one for entries), the Python `set` uses a **Single Contiguous Array** of `setentry` structs.

### The `setentry` Structure

Every slot in this array (called a "bucket") contains exactly two things:

1.  **The Hash:** The cached hash value of the element (to avoid re-calculating it).
2.  **The Key Pointer:** A reference (memory address) to the actual object stored.

### The Layout

The set allocates a block of memory (the array). To maintain speed, this array must remain **sparse** (mostly empty).

  * **Empty Slot:** `Hash = 0`, `Key = NULL`
  * **Active Slot:** `Hash = 123...`, `Key = <Address of Object>`
  * **Dummy Slot:** Used for items that were deleted (to keep the probing chain intact).

### Why not use the "Two-Array" Dict approach?

  * **Dictionaries** use the two-array approach specifically to decouple the "hashing" from the "storage" to guarantee **Insertion Order**.
  * **Sets** do not promise order. Therefore, they skip the overhead of the secondary index array and store data directly in the hash table slots. This makes the implementation simpler but results in the "random" order you see when printing a set.

-----

## 2\. How Insertion and Probing Work

When you execute `my_set.add(item)`, Python performs **Open Addressing** with **Linear Probing**.

### Step 1: Hashing

Python calculates `hash(item)`. Let's say the result is `987654321`.

### Step 2: Masking (Finding the Index)

Python maps this huge hash to an index that fits inside the current array size using a bitwise mask:
$$Index = Hash \ \& \ (ArraySize - 1)$$

### Step 3: Probing (The Look-Up)

Python inspects the slot at that `Index`:

  * **Case A: The Slot is Empty (NULL)**

      * Python inserts the `Hash` and the `Key Pointer` into this slot.
      * **Cost:** $O(1)$.

  * **Case B: The Slot is Occupied (Collision)**

      * This is a **Hash Collision**. The slot is taken by a different object (or the same one).
      * Python calculates a new index using a probing algorithm (pseudo-random steps based on the hash).
      * It checks the *next* calculated slot. It repeats this until it finds an empty slot or finds the existing item.

-----

## 3\. The Duplicate Detection Protocol

How does a set know if an item is a duplicate? It uses a strict 3-step verification process to avoid slow comparisons.

When adding `new_item`, if Python lands on a slot already occupied by `old_item`:

1.  **Hash Check (Fastest):**
      * It compares the stored hash of `old_item` vs the hash of `new_item`.
      * If hashes differ $\to$ Not a duplicate. Probe next slot.
      * If hashes match $\to$ Proceed to Step 2.
2.  **Identity Check (Fast):**
      * It checks memory addresses: `new_item is old_item`.
      * If **True** $\to$ Duplicate. Stop.
      * If **False** $\to$ Proceed to Step 3.
3.  **Equality Check (Slowest):**
      * It runs `new_item == old_item`.
      * If **True** $\to$ Duplicate. Discard `new_item`.
      * If **False** $\to$ Collision. Probe next slot.

-----

## 4\. Memory Management

  * **Sparsity Rule:** To guarantee $O(1)$ performance, the array cannot get too full. If the "Load Factor" (filled slots / total slots) exceeds **2/3 (66%)**, Python triggers a resize.
  * **Resizing:**
    1.  A new, larger array is allocated (usually 2x or 4x size).
    2.  **Every single element** in the old array is re-inserted into the new array.
    3.  This is why `.add()` generally takes $O(1)$, but occasionally takes $O(n)$ during a resize.

-----

## 5\. Methods and Complexity Reference

$n$ = size of current set, $m$ = size of other set.

### A. Basic Modification (In-Place)

| Method | Description | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- |
| `add(x)` | Adds element `x`. | $O(1)$ | $O(1)$ |
| `remove(x)` | Removes `x` or raises KeyError. | $O(1)$ | $O(1)$ |
| `discard(x)` | Removes `x` if present. | $O(1)$ | $O(1)$ |
| `pop()` | Removes arbitrary element. | $O(1)$ | $O(1)$ |
| `clear()` | Resets pointers (retains memory capacity usually). | $O(1)$ | $O(1)$ |

### B. Mathematical Operations (Returns NEW Set)

These create a **new** array in memory.

| Method | Operator | Logic | Time | Space |
| :--- | :--- | :--- | :--- | :--- |
| `union` | `\|` | Elements in A **OR** B. | $O(n + m)$ | $O(n + m)$ |
| `intersection` | `&` | Elements in A **AND** B. | $O(min(n, m))$ | $O(min(n, m))$ |
| `difference` | `-` | Elements in A **NOT** in B. | $O(n)$ | $O(n)$ |
| `symmetric_difference` | `^` | Elements in A **OR** B, not both. | $O(n + m)$ | $O(n + m)$ |

### C. Mathematical Updates (Modifies ORIGINAL Set)

These modify the existing array structure in-place.

| Method | Operator | Logic | Time | Space |
| :--- | :--- | :--- | :--- | :--- |
| `update` | `\|=` | Add elements from B to A. | $O(m)$ | $O(1)$ |
| `intersection_update` | `&=` | Keep only elements in both. | $O(n)$ | $O(1)$ |
| `difference_update` | `-=` | Remove elements found in B. | $O(m)$ | $O(1)$ |
| `symmetric_difference_update` | `^=` | Keep unique elements from both. | $O(n + m)$ | $O(1)$ |

-----

## 6\. Code Examples

### Example 1: Proving Internal Checks (Hash vs Equality)

```python
class DebugItem:
    def __init__(self, val):
        self.val = val
    
    def __hash__(self):
        print(f"Hashing {self.val}")
        return hash(self.val)
    
    def __eq__(self, other):
        print(f"Comparing {self.val} == {other.val}")
        return self.val == other.val

s = set()
item1 = DebugItem(10)
item2 = DebugItem(10) # Different object, same data

s.add(item1) 
# Output: "Hashing 10"

s.add(item2) 
# Output: 
# "Hashing 10" (Hash match detected)
# "Comparing 10 == 10" (Identity check failed, forced to Equality check)
```

### Example 2: Update vs Union

```python
s1 = {1, 2}
s2 = {3, 4}

# Uses EXTRA memory (New Array)
res = s1.union(s2) 

# Uses NO extra memory (Same Array)
s1.update(s2)
```

### Example 3: List De-duplication

```python
raw_data = [1, 2, 2, 3, 4, 4, 5]

# The set constructor iterates the list and hashes every item
unique_data = set(raw_data) 
# {1, 2, 3, 4, 5} -> Note: Order is not guaranteed to be preserved!
```
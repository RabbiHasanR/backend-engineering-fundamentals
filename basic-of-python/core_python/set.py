# 1.Adding and Removing Elements

# Initialize a set
fruits = {"apple", "banana", "cherry"}

# --- 1. add(element) ---
# Adds an element to the set.
fruits.add("orange")
print(f"After add:    {fruits}")

# --- 2. remove(element) ---
# Removes an element. Raises KeyError if the element is not found.
fruits.remove("banana")
print(f"After remove: {fruits}")
# fruits.remove("mango")  # This would crash your program with a KeyError!

# --- 3. discard(element) ---
# Removes an element. Does NOT raise an error if missing. Safer than remove().
fruits.discard("mango")   # Nothing happens, no error
fruits.discard("cherry")  # Actually removes cherry
print(f"After discard:{fruits}")

# --- 4. pop() ---
# Removes and returns an arbitrary (random) element.
# Since sets are unordered, you don't know which one will be popped.
item = fruits.pop()
print(f"Popped item:  {item}")
print(f"Remaining:    {fruits}")

# --- 5. clear() ---
# Removes all elements, leaving an empty set.
fruits.clear()
print(f"After clear:  {fruits}")

# 2. Mathematical Operations (Returns New Set)

set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}

# --- 6. union(other) | Operator: | ---
# Combines elements from both sets.
# result = set_a.union(set_b)
result = set_a | set_b
print(f"Union: {result}")
# Output: {1, 2, 3, 4, 5, 6}

# --- 7. intersection(other) | Operator: & ---
# Returns only elements found in BOTH sets.
# result = set_a.intersection(set_b)
result = set_a & set_b
print(f"Intersection: {result}")
# Output: {3, 4}

# --- 8. difference(other) | Operator: - ---
# Returns elements in A that are NOT in B.
# result = set_a.difference(set_b)  # Output: {1, 2}
# result = set_a - set_b   # Output: {1, 2}
# result = set_b - set_a   # Output: {5, 6}
print(f"Difference: {result}")

# --- 9. symmetric_difference(other) | Operator: ^ ---
# Returns elements in A OR B, but NOT both. (The opposite of intersection)
# result = set_a.symmetric_difference(set_b)
result = set_b ^ set_a
print(f"Symetric Difference: {result}")
# Output: {1, 2, 5, 6}

# 3. Update Operations (Modifies In-Place)
# Setup
set_x = {1, 2, 3}
set_y = {3, 4, 5}

# --- 10. update(other) | Operator: |= ---
# Adds all elements from Y into X.
set_x.update(set_y)
print(f"After update:                {set_x}")
# Output: {1, 2, 3, 4, 5}

# Reset for next example
set_x = {1, 2, 3}

# --- 11. intersection_update(other) | Operator: &= ---
# Removes elements from X that are not in Y.
set_x.intersection_update(set_y)
print(f"After intersection_update:   {set_x}")
# Output: {3}

# Reset
set_x = {1, 2, 3}

# --- 12. difference_update(other) | Operator: -= ---
# Removes elements from X that are present in Y.
set_x.difference_update(set_y)
print(f"After difference_update:     {set_x}")
# Output: {1, 2}

# Reset
set_x = {1, 2, 3}

# --- 13. symmetric_difference_update(other) | Operator: ^= ---
# Keeps only elements found in either X or Y, but not both.
set_x.symmetric_difference_update(set_y)
print(f"After sym_difference_update: {set_x}")
# Output: {1, 2, 4, 5}

# 4. Boolean Checks (Returns True/False)
s1 = {1, 2}
s2 = {1, 2, 3, 4}
s3 = {5, 6}

# --- 14. issubset(other) | Operator: <= ---
# True if all elements of s1 are inside s2
print(f"Is s1 subset of s2?   {s1.issubset(s2)}")   # True
print(f"Is s2 subset of s1?   {s2.issubset(s1)}")   # False

# --- 15. issuperset(other) | Operator: >= ---
# True if s2 contains all elements of s1
print(f"Is s2 superset of s1? {s2.issuperset(s1)}") # True

# --- 16. isdisjoint(other) ---
# True if the sets have NO common elements (intersection is empty)
print(f"Is s1 disjoint s3?    {s1.isdisjoint(s3)}") # True (No common numbers)
print(f"Is s1 disjoint s2?    {s1.isdisjoint(s2)}") # False (They share 1, 2)


# 5. Copying

# --- 17. copy() ---
# Creates a shallow copy. Modifying the copy does not affect the original.
original = {1, 2, 3}
duplicate = original.copy()

duplicate.add(4)

print(f"Original:  {original}")  # {1, 2, 3}
print(f"Duplicate: {duplicate}") # {1, 2, 3, 4}















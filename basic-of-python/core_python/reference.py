import ctypes

# 1. Create the Object
# We explicitly create the int '10' and assign it.
value = 10

# 2. Simulate C-Level Variables
# In C, 'a' and 'b' would be pointers. We simulate this using ctypes.
# ctypes.py_object is effectively a "variable" that holds a Python object.
variable_a = ctypes.py_object(value)
variable_b = ctypes.py_object(value)

# 3. Get the Memory Addresses
# id() gets the address of the VALUE (The Integer 10)
object_address = id(value)

# ctypes.addressof() gets the address of the VARIABLE (The 8-byte pointer itself)
var_a_address = ctypes.addressof(variable_a)
var_b_address = ctypes.addressof(variable_b)

# --- PRINTING THE PROOF ---

print(f"1. THE OBJECT (Integer 10)")
print(f"   Memory Address:  {object_address} (Where data 10 lives)")
print("-" * 50)

print(f"2. VARIABLE 'A' (The Pointer)")
print(f"   Memory Address:  {var_a_address}  (Where 'a' lives)")
print(f"   Value inside 'a':{id(variable_a.value)} (Points to Object)")
print("-" * 50)

print(f"3. VARIABLE 'B' (The Pointer)")
print(f"   Memory Address:  {var_b_address}  (Where 'b' lives)")
print(f"   Value inside 'b':{id(variable_b.value)} (Points to Object)")

# Final Boolean Check
print("-" * 50)
print(f"Do 'a' and 'b' point to the same object?   {id(variable_a.value) == id(variable_b.value)}")
print(f"Are 'a' and 'b' the same physical memory?  {var_a_address == var_b_address}")








a = 5       # Python creates integer object 5 at address X. 'a' points to X.
b = a       # Python sees 'a' points to X. It makes 'b' point to X too.

print(a is b)      # True
print(id(a))       # Example: 140703604471720
print(id(b))       # Example: 140703604471720 (EXACTLY THE SAME)







a = 5
b = a

del a        # We rip the "a" sticky note off the box.
print(b)     # Output: 5. 
             # 'b' still points to the box. It didn't care that 'a' is gone.
             



a = 5
b = a      # Both point to Address X (Value 5)

a = 6      # New box created for 6 (Address Y). 
           # Label 'a' is moved to Address Y.
           # Label 'b' STAYS at Address X.

print(a)   # 6
print(b)   # 5 (Still points to the old address)




a = 10
b = a
del a
print(b)

# What is the output?
# A. 10     B. NameError
# C. None   D. 0



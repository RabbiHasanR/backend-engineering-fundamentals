# 🧠 The Ultimate Beginner's Guide to Bit Manipulation

> 💡 **Welcome!** This guide is written for *everyone* — whether you just started coding or have been at it for a while. We'll go from "what even is a bit?" to confidently reading and writing bitwise operations. Take it one section at a time. You've got this! 🚀

---

## 📚 Table of Contents

1. [Introduction — Why Should I Care?](#introduction)
2. [Part 1 — The 32-Bit Integer Container](#part-1-the-32-bit-integer-container)
3. [Part 2 — Binary Conversions](#part-2-binary-conversions)
4. [Part 3 — Negative Numbers & 2's Complement](#part-3-negative-numbers--2s-complement)
5. [Part 4 — Bitwise Operators](#part-4-bitwise-operators)
   - [AND (`&`)](#1-and-)
   - [OR (`|`)](#2-or-)
   - [XOR (`^`)](#3-xor-)
   - [NOT (`~`)](#4-not-)
6. [Part 5 — Shift Operators](#part-5-shift-operators)
   - [Left Shift (`<<`)](#1-left-shift-)
   - [Right Shift (`>>`)](#2-right-shift-)
7. [⚡ Quick Reference Cheat Sheet](#-quick-reference-cheat-sheet)

---

## Introduction

### 🤔 What is Bit Manipulation — and Why Should I Care?

Imagine you're a computer. You don't understand the word "hello" or the number "42" directly. All you understand is electricity: **on** or **off**, **1** or **0**. These tiny on/off signals are called **bits** (short for **Binary Digits**).

Everything on your computer — text, images, videos, code — is ultimately just a huge river of 1s and 0s.

**Bit manipulation** means working directly with those 1s and 0s to do things like:

- 🔒 Check if a number is odd or even instantly
- ⚡ Multiply or divide by powers of 2 faster than regular arithmetic
- 🗜️ Compress and encrypt data
- 🎮 Store multiple settings in a single number (used heavily in games!)
- 🧩 Solve tricky coding interview problems elegantly

> 💡 **Real-world analogy:** Think of a light switch panel in a big house. Each switch is either ON (1) or OFF (0). Bit manipulation is like knowing the exact trick to flip the right switches super efficiently, without turning them all on and off one by one.

---

## Part 1: The 32-Bit Integer Container

### 📖 What is it?

When your computer stores a whole number (an integer), it puts it in a fixed-size box. The most common box size is **32 bits** — imagine a row of exactly 32 light bulbs, each one either **on (1)** or **off (0)**.

```
Index:  31  30  29  28  ...  3   2   1   0
        ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
Bits:   │ 0 │ 0 │ 0 │ 0 │...│ 0 │ 0 │ 0 │ 1 │
        └───┴───┴───┴───┴───┴───┴───┴───┴───┘
         ▲                               ▲
    Sign Bit                       Rightmost Bit
    (Index 31)                     (Index 0)
```

### 🔍 The Layout

| Part | Bits | Purpose |
|---|---|---|
| **Index 0 to 30** | 31 bits | Store the **magnitude** (actual value) |
| **Index 31** | 1 bit | Store the **sign** (+ or −) |

The leftmost bit (index 31) is called the **Most Significant Bit (MSB)** or the **Sign Bit**.

### 📏 The Sign Bit Rule

```
MSB = 0  →  Positive number  ✅
MSB = 1  →  Negative number  ❌
```

### 📊 Storage Limits

Since 1 bit is "spent" on the sign, we have 31 bits left for the actual number:

- **Maximum value:** 2³¹ − 1 = **2,147,483,647** (about 2.1 billion)
- **Minimum value:** −2³¹ = **−2,147,483,648**

> ⚠️ **Common Mistake:** Beginners often think 32 bits can store up to 2³² values on *each* side of zero. Remember — one whole bit is dedicated to the sign, so positive and negative share the remaining 31 bits.

---

## Part 2: Binary Conversions

### 1. Decimal → Binary

#### 📖 What is it?

Converting a normal number (like 7, 42, or 255) into its binary representation — a sequence of 1s and 0s.

#### 🤔 Why is it useful?

You need to know this to understand how any bitwise operation actually works under the hood.

#### 🔍 How it works — The Division Method

> 💡 **Analogy:** Think of it like peeling an onion. Each time you divide by 2, you peel off one layer (the remainder) until nothing is left.

**Steps:**
1. Divide the number by 2
2. Record the **remainder** (0 or 1)
3. Use the **quotient** as your next number
4. Repeat until the quotient is 0
5. Read remainders from **bottom to top**

**Example: Convert 7 to binary**

```
7 ÷ 2 = 3  remainder  1  ← Read LAST
3 ÷ 2 = 1  remainder  1
1 ÷ 2 = 0  remainder  1  ← Read FIRST

Result (bottom to top): 1 1 1  →  Binary: 111
```

In full 32-bit memory (padded with leading zeros):
```
00000000 00000000 00000000 00000111
```

**Example: Convert 13 to binary**

```
13 ÷ 2 = 6  remainder  1  ← Read LAST
 6 ÷ 2 = 3  remainder  0
 3 ÷ 2 = 1  remainder  1
 1 ÷ 2 = 0  remainder  1  ← Read FIRST

Result (bottom to top): 1 1 0 1  →  Binary: 1101
```

#### 💻 Code Example

```python
# Method 1: Using Python's built-in bin() function
number = 7
print(bin(number))        # Output: 0b111  (0b prefix means binary)
print(bin(number)[2:])    # Output: 111    (strip the 0b prefix)

# Method 2: Manual conversion using division
def decimal_to_binary(n):
    if n == 0:
        return "0"
    
    remainders = []
    while n > 0:
        remainders.append(n % 2)   # Record remainder (0 or 1)
        n = n // 2                  # Integer division
    
    # Remainders were collected in reverse, so flip them
    remainders.reverse()
    return ''.join(map(str, remainders))

print(decimal_to_binary(7))   # Output: 111
print(decimal_to_binary(13))  # Output: 1101

# Method 3: See 32-bit representation
def to_32bit(n):
    # & with a 32-bit mask to handle Python's arbitrary precision
    return format(n & 0xFFFFFFFF, '032b')

print(to_32bit(7))   # Output: 00000000000000000000000000000111
```

#### ✅ Practice Problem

Convert the following decimal numbers to binary (try without looking!):

1. `5` → ?
2. `10` → ?
3. `25` → ?

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. 5  → 101
   5 ÷ 2 = 2 r 1
   2 ÷ 2 = 1 r 0
   1 ÷ 2 = 0 r 1  →  Read bottom-up: 101 ✅

2. 10 → 1010
   10 ÷ 2 = 5 r 0
    5 ÷ 2 = 2 r 1
    2 ÷ 2 = 1 r 0
    1 ÷ 2 = 0 r 1  →  Read bottom-up: 1010 ✅

3. 25 → 11001
   25 ÷ 2 = 12 r 1
   12 ÷ 2 =  6 r 0
    6 ÷ 2 =  3 r 0
    3 ÷ 2 =  1 r 1
    1 ÷ 2 =  0 r 1  →  Read bottom-up: 11001 ✅
```
</details>

---

### 2. Binary → Decimal

#### 📖 What is it?

Reading a binary number and converting it back into a normal decimal number.

#### 🔍 How it works — The Position Formula

Each bit position has a **power of 2** value. The rightmost bit is 2⁰, the next is 2¹, then 2², and so on.

```
Binary:   1    1    0    1
Power:    2³   2²   2¹   2⁰
Value:    8    4    2    1
```

**Multiply each bit by its power value, then add them all up.**

**Example: Convert `1101` to decimal**

```
Position:  3   2   1   0
Bit:       1   1   0   1
Value:     8 + 4 + 0 + 1  =  13
```

**Example: Convert `10110` to decimal**

```
Position:  4   3   2   1   0
Bit:       1   0   1   1   0
Value:    16 + 0 + 4 + 2 + 0  =  22
```

#### 💻 Code Example

```python
# Method 1: Python's built-in int() with base 2
binary_string = "1101"
decimal = int(binary_string, 2)
print(decimal)   # Output: 13

# Method 2: Manual conversion using position values
def binary_to_decimal(binary_str):
    result = 0
    power = 0
    
    # Read from RIGHT to LEFT
    for bit in reversed(binary_str):
        result += int(bit) * (2 ** power)
        power += 1
    
    return result

print(binary_to_decimal("1101"))   # Output: 13
print(binary_to_decimal("10110"))  # Output: 22
```

#### ✅ Practice Problem

Convert these binary numbers to decimal:

1. `1010` → ?
2. `11111` → ?
3. `100000` → ?

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. 1010:   8 + 0 + 2 + 0 = 10 ✅
2. 11111:  16 + 8 + 4 + 2 + 1 = 31 ✅
3. 100000: 32 + 0 + 0 + 0 + 0 + 0 = 32 ✅
```
</details>

---

## Part 3: Negative Numbers & 2's Complement

### 📖 What is it?

Computers can't store a "minus sign" in memory — everything is 1s and 0s. So instead, they use a clever trick called **2's Complement** to represent negative numbers.

### 🤔 Why is it useful?

It lets the computer use the *same* addition circuit for both adding and subtracting. One circuit, two operations — efficient!

> 💡 **Analogy:** Imagine a car odometer that only goes 0–999. If you're at 000 and go "backward" by 1, it wraps to 999. Computers do something similar — they wrap negative numbers around into the high end of the bit space.

---

### Step 1: 1's Complement (The Warm-Up)

#### 🔍 How it works

Simply **flip every single bit**: all `1`s become `0`s, and all `0`s become `1`s.

```
Number 7  →  Binary:  0000 0111
Flip bits →  1's Comp: 1111 1000
```

```python
# 1's complement in Python (8-bit example)
n = 7
ones_complement = ~n & 0xFF   # Mask to 8 bits
print(format(ones_complement, '08b'))  # Output: 11111000
```

---

### Step 2: 2's Complement (The Real Standard)

#### 🔍 How it works

Take the 1's Complement and **add 1** to it.

**Full Example: Represent −7 in binary**

```
Step 1 — Start with 7:
         0000 0111

Step 2 — Flip all bits (1's complement):
         1111 1000

Step 3 — Add 1:
         1111 1000
       +         1
       ───────────
         1111 1001   ← This is how −7 is stored!
```

```
Verify: MSB is 1  →  Confirms it's negative ✅
```

#### 💻 Code Example

```python
# Python handles negative numbers natively using 2's complement
# Let's visualize it manually

def twos_complement(n, bits=8):
    """Convert a negative number to its 2's complement binary representation."""
    if n >= 0:
        return format(n, f'0{bits}b')
    else:
        # Python trick: mask to desired bit width
        return format(n & (2**bits - 1), f'0{bits}b')

print(twos_complement(7))    # Output: 00000111
print(twos_complement(-7))   # Output: 11111001

# Verify: convert back
def from_twos_complement(binary_str):
    """Read a 2's complement binary string back to decimal."""
    if binary_str[0] == '0':   # Positive number
        return int(binary_str, 2)
    else:                        # Negative number
        # Flip bits, add 1, negate
        flipped = ''.join('1' if b == '0' else '0' for b in binary_str)
        magnitude = int(flipped, 2) + 1
        return -magnitude

print(from_twos_complement("11111001"))  # Output: -7  ✅
```

#### ✅ Practice Problem

Represent these numbers in 8-bit 2's complement binary:

1. `−1` → ?
2. `−5` → ?
3. `−128` → ?

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. −1:
   +1  = 0000 0001
   Flip = 1111 1110
   +1   = 1111 1111  ✅

2. −5:
   +5  = 0000 0101
   Flip = 1111 1010
   +1   = 1111 1011  ✅

3. −128:
   +128 = 1000 0000
   Flip  = 0111 1111
   +1    = 1000 0000  ✅
   (Note: −128 is its own 2's complement — a fun edge case!)
```
</details>

> ⚠️ **Common Mistake:** Beginners sometimes try to just put a 1 in front of the binary number to make it negative. That's **wrong**! `10000111` is NOT −7. You must use the full 2's complement process.

---

## Part 4: Bitwise Operators

Bitwise operators work on **individual bits** of two numbers, comparing them side by side — like two parallel rows of switches.

> 💡 **Setup analogy:** Imagine two rows of light switches, one labeled A and one labeled B. Each bitwise operator has a unique rule for looking at one pair of switches (one from A, one from B) and deciding what the output switch should be.

---

### 1. AND (`&`)

#### 📖 What is it?

The AND operator compares two bits and outputs `1` **only if BOTH bits are 1**. Otherwise, output is `0`.

> 💡 **Real-world analogy:** A door that unlocks only if *both* keys are inserted at the same time.

#### 🤔 Why is it useful?

- **Check if a specific bit is ON** (masking)
- **Check if a number is odd or even** (fastest method)
- **Clear (turn off) specific bits**

#### 🔍 How it works

**Truth Table:**
```
A   B   A & B
─────────────
1   1     1    ← Both 1? Output 1
1   0     0
0   1     0
0   0     0
```

**Visual Example: `5 & 3`**
```
  5  →  0000 0101
  3  →  0000 0011
         ─────────
  &  →  0000 0001   (= 1)

Compare column by column:
  1&0=0,  1&1=1,  0&0=0  →  001 = 1 ✅
```

#### 💻 Code Example

```python
# Basic AND operation
print(5 & 3)   # Output: 1

# ─────────────────────────────
# TRICK 1: Check if number is ODD or EVEN
# ─────────────────────────────
# Even numbers always end in 0 in binary (last bit = 0)
# Odd numbers always end in 1 in binary (last bit = 1)
# So: n & 1 tells us the last bit!

def is_odd(n):
    return (n & 1) == 1   # True if last bit is 1

print(is_odd(7))    # Output: True   (7 = 0111, last bit = 1)
print(is_odd(8))    # Output: False  (8 = 1000, last bit = 0)

# ─────────────────────────────
# TRICK 2: Check if a specific bit is ON (bit masking)
# ─────────────────────────────
# To check bit at position i: use (n & (1 << i))

def is_bit_set(n, position):
    mask = 1 << position   # Create a number with only bit 'position' ON
    return (n & mask) != 0

n = 13  # Binary: 1101
print(is_bit_set(n, 0))  # Output: True  (bit 0 = 1)
print(is_bit_set(n, 1))  # Output: False (bit 1 = 0)
print(is_bit_set(n, 2))  # Output: True  (bit 2 = 1)
print(is_bit_set(n, 3))  # Output: True  (bit 3 = 1)
```

#### ✅ Practice Problem

1. What is `12 & 10`? Work it out bit by bit.
2. Is 256 odd or even? How can you tell with AND?
3. In the number `42` (binary: `101010`), is bit 3 set?

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. 12 & 10:
   12 = 0000 1100
   10 = 0000 1010
    &   0000 1000  = 8 ✅

2. 256 & 1:
   256 = ...0000 0000 (last bit is 0)
     1 = ...0000 0001
     &   ...0000 0000 = 0 → EVEN ✅

3. 42 = 101010
   Bit 3 is the 4th from right (0-indexed):  1 0 1 0 1 0
                                              5 4 3 2 1 0
   Bit 3 = 0  →  NOT set ✅
```
</details>

> ⚠️ **Common Mistake:** Confusing `&` (bitwise AND) with `&&` (logical AND). `5 & 3` operates on bits and gives `1`. `5 and 3` in Python is a logical operation and gives `3` (the last truthy value). They're very different!

---

### 2. OR (`|`)

#### 📖 What is it?

OR outputs `1` if **at least one** of the two bits is `1`.

> 💡 **Real-world analogy:** A room light that turns on if *either* person (or both) flips the switch.

#### 🤔 Why is it useful?

- **Turn ON a specific bit**
- **Combine flags/settings** (e.g., game permissions: CAN_RUN | CAN_JUMP)
- **Set a bit without touching others**

#### 🔍 How it works

**Truth Table:**
```
A   B   A | B
─────────────
1   1     1
1   0     1    ← At least one 1? Output 1
0   1     1
0   0     0    ← Only 0 when BOTH are 0
```

**Visual Example: `5 | 3`**
```
  5  →  0000 0101
  3  →  0000 0011
         ─────────
  |  →  0000 0111   (= 7)
```

#### 💻 Code Example

```python
# Basic OR
print(5 | 3)   # Output: 7

# ─────────────────────────────
# TRICK: Turn ON (set) a specific bit
# ─────────────────────────────
def set_bit(n, position):
    mask = 1 << position   # Only bit 'position' is 1
    return n | mask        # Turn on that bit in n

n = 5   # Binary: 0101
print(bin(set_bit(n, 1)))  # Turn on bit 1: 0111 = 7
print(bin(set_bit(n, 3)))  # Turn on bit 3: 1101 = 13

# ─────────────────────────────
# Real-world: Permission flags
# ─────────────────────────────
CAN_READ    = 0b001   # 1
CAN_WRITE   = 0b010   # 2
CAN_EXECUTE = 0b100   # 4

# Grant read and write permissions:
permissions = CAN_READ | CAN_WRITE
print(bin(permissions))     # Output: 0b11 (both bits set)
print(permissions & CAN_READ)    # Output: 1 (has read? Yes!)
print(permissions & CAN_EXECUTE) # Output: 0 (has execute? No!)
```

#### ✅ Practice Problem

1. What is `9 | 6`? Solve bit by bit.
2. You have `n = 8` (binary: `1000`). Turn on bit 1 and bit 2 using OR. What's the result?

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. 9 | 6:
   9 = 0000 1001
   6 = 0000 0110
   |   0000 1111  = 15 ✅

2. Turn on bit 1: 8 | (1 << 1) = 8 | 2 = 1000 | 0010 = 1010 = 10
   Turn on bit 2: 10 | (1 << 2) = 10 | 4 = 1010 | 0100 = 1110 = 14 ✅
```
</details>

> ⚠️ **Common Mistake:** Using OR to "clear" a bit. OR can only turn bits ON, never OFF. To turn a bit OFF, use AND with a mask (covered in NOT section).

---

### 3. XOR (`^`)

#### 📖 What is it?

XOR (Exclusive OR) outputs `1` if the bits are **different**. If they're the same, output is `0`.

> 💡 **Real-world analogy:** A two-person toggle switch. If both people are in the same state (both pressing or both not pressing), the result is OFF. If one is different from the other, the result is ON.

#### 🤔 Why is it useful?

XOR is the secret weapon of bit manipulation! It's used to:
- **Find the unique number** in an array (interview favourite!)
- **Swap two numbers without a temp variable**
- **Toggle** a specific bit on and off
- **Simple encryption**

#### 🔍 How it works

**Truth Table:**
```
A   B   A ^ B
─────────────
1   1     0    ← Same → 0
1   0     1    ← Different → 1
0   1     1    ← Different → 1
0   0     0    ← Same → 0
```

**Key properties of XOR:**
```
n ^ n = 0      (anything XOR itself = 0)
n ^ 0 = n      (anything XOR zero = itself)
XOR is commutative: a ^ b = b ^ a
XOR is associative: (a ^ b) ^ c = a ^ (b ^ c)
```

**Visual Example: `5 ^ 3`**
```
  5  →  0000 0101
  3  →  0000 0011
         ─────────
  ^  →  0000 0110   (= 6)
```

#### 💻 Code Example

```python
# Basic XOR
print(5 ^ 3)   # Output: 6

# ─────────────────────────────
# TRICK 1: Swap two numbers without a temp variable!
# ─────────────────────────────
a, b = 10, 20
print(f"Before: a={a}, b={b}")

a = a ^ b
b = a ^ b   # (a^b)^b = a
a = a ^ b   # (a^b)^a = b

print(f"After:  a={a}, b={b}")  # Output: a=20, b=10

# ─────────────────────────────
# TRICK 2: Find the ONE unique number in an array
# ─────────────────────────────
# If all numbers appear twice EXCEPT one, XOR finds it!
# Because: duplicate ^ duplicate = 0, and 0 ^ unique = unique

def find_unique(nums):
    result = 0
    for n in nums:
        result ^= n   # XOR each number
    return result

nums = [4, 1, 2, 1, 2]   # 1 and 2 appear twice, 4 appears once
print(find_unique(nums))  # Output: 4  ✅

# ─────────────────────────────
# TRICK 3: Toggle (flip) a specific bit
# ─────────────────────────────
def toggle_bit(n, position):
    mask = 1 << position
    return n ^ mask

n = 5   # Binary: 0101
print(bin(toggle_bit(n, 0)))  # Flip bit 0: 0100 = 4
print(bin(toggle_bit(n, 1)))  # Flip bit 1: 0111 = 7
```

#### ✅ Practice Problem

1. What is `7 ^ 7`? And `7 ^ 0`? What do these results tell you?
2. In the list `[3, 5, 3, 7, 5, 2, 2]`, find the unique number using XOR.
3. Toggle bit 2 of the number `12` (binary: `1100`).

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. 7 ^ 7 = 0  (same bits cancel out)
   7 ^ 0 = 7  (XOR with 0 changes nothing)
   This tells us: identical numbers always XOR to 0,
   and 0 is a "neutral" element for XOR! ✅

2. 3 ^ 5 ^ 3 ^ 7 ^ 5 ^ 2 ^ 2
   = (3^3) ^ (5^5) ^ (2^2) ^ 7
   = 0 ^ 0 ^ 0 ^ 7
   = 7  ← The unique number! ✅

3. 12 = 1100
   mask = 1 << 2 = 0100
   12 ^ mask = 1100 ^ 0100 = 1000 = 8 ✅
```
</details>

> ⚠️ **Common Mistake:** Confusing XOR (`^`) with exponentiation. In Python, `2^3` is NOT 2³ = 8. It's `2 XOR 3 = 1`. To raise 2 to the power of 3 in Python, use `2**3`.

---

### 4. NOT (`~`)

#### 📖 What is it?

NOT flips every single bit in a number. `0`s become `1`s, and `1`s become `0`s.

> 💡 **Analogy:** Imagine a light panel where NOT flips every single switch at once — all the ON lights go OFF and all the OFF lights go ON.

#### 🤔 Why is it useful?

- Create **masks** to clear specific bits
- Understand how **negative numbers** are stored
- The key formula: `~n = -(n + 1)` always

#### 🔍 How it works — Step by Step

**The Golden Formula:** `~n = -(n + 1)`

This is because NOT is the same as 1's complement, and the 2's complement representation makes it come out exactly one less than the negative.

**Example 1: `~5`**
```
Step 1 — Write 5 in binary (8-bit):
         0000 0101

Step 2 — Flip every bit:
         1111 1010

Step 3 — MSB is 1, so this is NEGATIVE
         Take 2's complement to find the magnitude:
         Flip: 0000 0101
         +1:   0000 0110  (= 6)

Step 4 — Result: −6

         Check: ~5 = -(5+1) = -6  ✅
```

**Example 2: `~(−6)`**
```
Step 1 — Write −6 in binary (2's complement): 1111 1010
Step 2 — Flip every bit: 0000 0101
Step 3 — MSB is 0, so this is POSITIVE
Step 4 — 0000 0101 = 5

         Check: ~(−6) = −(−6+1) = −(−5) = 5  ✅
```

#### 💻 Code Example

```python
# Basic NOT
print(~5)    # Output: -6
print(~-6)   # Output: 5
print(~0)    # Output: -1
print(~-1)   # Output: 0

# The golden formula: ~n = -(n+1)
n = 42
print(~n == -(n + 1))   # Output: True  — always!

# ─────────────────────────────
# TRICK: Clear (turn OFF) a specific bit using NOT + AND
# ─────────────────────────────
def clear_bit(n, position):
    mask = ~(1 << position)   # All bits ON except position
    return n & mask           # AND clears the target bit

n = 13   # Binary: 1101
print(bin(clear_bit(n, 0)))  # Clear bit 0: 1100 = 12
print(bin(clear_bit(n, 2)))  # Clear bit 2: 1001 = 9

# Manual step-by-step trace for clear_bit(13, 0):
# 1 << 0 = 0000 0001
# ~(1<<0) = 1111 1110  (mask: all ON except bit 0)
# 13      = 0000 1101
# 13&mask = 0000 1100  = 12 ✅
```

#### ✅ Practice Problem

1. What is `~100`? Verify using the formula `~n = -(n+1)`.
2. What is `~(~7)`? Can you predict without calculating?
3. Use NOT and AND to clear bit 3 from the number `15` (binary: `1111`).

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. ~100 = -(100+1) = -101 ✅

2. ~(~7) = ~(-8) = -(-8+1) = -(-7) = 7
   Any double NOT returns the original number! ✅

3. Clear bit 3 from 15:
   1 << 3      = 0000 1000
   ~(1 << 3)   = 1111 0111  (mask)
   15 & mask   = 0000 1111 & 1111 0111
               = 0000 0111 = 7  ✅
```
</details>

> ⚠️ **Common Mistake:** In Python, `~n` on a positive number always gives a negative result, which surprises beginners. This is correct and expected — Python uses arbitrary-precision integers with sign, so `~5` will always be `-6`, never just flipping 8 bits to get `250`.

---

## Part 5: Shift Operators

Shift operators literally **slide** all the bits left or right by a given number of positions. Think of it like nudging a train of 1s and 0s along a track.

> 💡 We'll use 8-bit examples here for clarity (easier to visualize). The exact same rules apply to 32-bit integers.

---

### 1. Left Shift (`<<`)

#### 📖 What is it?

Push all the bits to the **left** by a given number of positions. Bits that fall off the left edge are **lost**, and empty spaces on the right are filled with `0`s.

```
Before:  [ 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 ]   ← 3
Shift left by 2:
After:   [ 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 ]   ← 12
                               ↑ moved       ↑ filled with 0s
```

#### 🤔 Why is it useful?

Left shifting by `k` is exactly the same as **multiplying by 2ᵏ** — and it's *much faster* for the CPU.

```
n << 1  =  n × 2
n << 2  =  n × 4
n << 3  =  n × 8
n << k  =  n × 2ᵏ
```

#### 🔍 How it works — Step by Step

**Example: `3 << 2` (shift 3 left by 2)**

```
Step 1 — Write 3 in binary (8-bit):
         0000 0011

Step 2 — Shift everything LEFT by 2:
         The two leftmost bits (0,0) fall off forever
         Everything else moves 2 spots left
         0000 11__ (empty slots on right)

Step 3 — Fill empty slots with 0s:
         0000 1100

Step 4 — Convert to decimal:
         8 + 4 = 12

Math check: 3 × 2² = 3 × 4 = 12  ✅
```

```
Visual animation:
         ┌──────────────────────┐
Before:  │ 0  0  0  0  0  0  1  1 │
         └──────────────────────┘
               ← ← ← ← ← ← ← ← (shift left by 2)
         ┌──────────────────────┐
After:   │ 0  0  0  0  1  1  0  0 │
         └──────────────────────┘
                            ↑  ↑
                         filled with 0s
```

#### 💻 Code Example

```python
# Basic left shift
print(3 << 2)   # Output: 12   (3 × 4)
print(1 << 4)   # Output: 16   (1 × 16)
print(5 << 1)   # Output: 10   (5 × 2)

# ─────────────────────────────
# TRICK: Fast multiplication by power of 2
# ─────────────────────────────
n = 6
print(n << 1)   # 6  × 2  = 12
print(n << 2)   # 6  × 4  = 24
print(n << 3)   # 6  × 8  = 48

# ─────────────────────────────
# TRICK: Create a bitmask for position i
# ─────────────────────────────
# 1 << i creates a number with ONLY bit i turned on
for i in range(5):
    mask = 1 << i
    print(f"1 << {i} = {mask:>3}  →  {format(mask, '08b')}")

# Output:
# 1 << 0 =   1  →  00000001
# 1 << 1 =   2  →  00000010
# 1 << 2 =   4  →  00000100
# 1 << 3 =   8  →  00001000
# 1 << 4 =  16  →  00010000
```

#### ✅ Practice Problem

1. What is `7 << 3`? Verify with the formula.
2. What single left-shift gives you the number 64?
3. What happens to `100 << 1`? Is it always safe to left shift?

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. 7 << 3 = 7 × 2³ = 7 × 8 = 56
   Binary: 00000111 → 00111000 = 56 ✅

2. 1 << 6 = 64
   00000001 → 01000000 = 64 ✅

3. 100 << 1 = 200 (fine for 32-bit)
   But be careful! Left shifting large numbers can cause OVERFLOW
   if the bits you shift out were significant.
   In Python (unlimited integer size), this is safe.
   In C/Java with 32-bit ints, you can lose data! ⚠️
```
</details>

> ⚠️ **Common Mistake:** Assuming left shift is always safe. In languages like C and Java with fixed-width integers, shifting bits off the left edge causes **overflow** and unpredictable results. In Python (which has arbitrary-size integers), it's always safe — but be aware of this in other languages!

---

### 2. Right Shift (`>>`)

#### 📖 What is it?

Push all the bits to the **right** by a given number of positions. Bits that fall off the right edge are **lost**. Empty spaces on the left are filled with... it depends!

```
Positive number (MSB=0)  →  Fill left with 0s
Negative number (MSB=1)  →  Fill left with 1s  (Sign Extension)
```

This rule is called **Sign Extension** — it makes sure negative numbers stay negative after shifting.

#### 🤔 Why is it useful?

Right shifting by `k` is the same as **integer division by 2ᵏ** (rounded down).

```
n >> 1  =  n ÷ 2
n >> 2  =  n ÷ 4
n >> k  =  n ÷ 2ᵏ  (integer division, rounds toward −∞)
```

#### 🔍 How it works

---

**Example A: Positive number — `20 >> 2`**

```
Step 1 — Write 20 in binary (8-bit):
         0001 0100   (MSB = 0, positive)

Step 2 — Shift RIGHT by 2:
         The rightmost 00 falls off
         __00 0101   (empty slots on left)

Step 3 — Fill with 0s (because MSB was 0):
         0000 0101

Step 4 — Convert: 4 + 1 = 5

Math check: 20 ÷ 2² = 20 ÷ 4 = 5  ✅
```

---

**Example B: Negative number — `(−20) >> 2`**

```
Step 1 — Write −20 in 8-bit 2's complement:
         +20 = 0001 0100
         Flip = 1110 1011
          +1  = 1110 1100   (MSB = 1, negative)

Step 2 — Shift RIGHT by 2:
         The rightmost 00 falls off
         __11 1011   (empty slots on left)

Step 3 — Fill with 1s (because MSB was 1 — Sign Extension!):
         1111 1011

Step 4 — Verify (it's negative, take 2's complement):
         Flip: 0000 0100
          +1:  0000 0101  (= 5)
         Result: −5

Math check: −20 ÷ 4 = −5  ✅
```

> ⚠️ **Why Sign Extension matters:** Without filling 1s for negative numbers, the result would become a large positive number — completely wrong! Sign extension is what keeps arithmetic correct.

```
If we incorrectly filled with 0s:
__11 1011  →  0011 1011  = 59  ← WRONG!
Correct fill with 1s:
__11 1011  →  1111 1011  = −5  ← CORRECT ✅
```

#### 💻 Code Example

```python
# Basic right shift
print(20 >> 2)    # Output: 5     (20 ÷ 4)
print(100 >> 3)   # Output: 12    (100 ÷ 8, rounded down)
print(-20 >> 2)   # Output: -5    (sign preserved!)
print(-1 >> 1)    # Output: -1    (all 1s shifted right, fills with 1s)

# ─────────────────────────────
# TRICK: Fast division by power of 2
# ─────────────────────────────
n = 64
print(n >> 1)   # 32   (÷2)
print(n >> 2)   # 16   (÷4)
print(n >> 6)   # 1    (÷64)

# ─────────────────────────────
# TRICK: Extract individual bits
# ─────────────────────────────
# Shift right then AND with 1 to get the bit at position i
def get_bit(n, position):
    return (n >> position) & 1

n = 13   # Binary: 1101
for i in range(4):
    print(f"Bit {i} of 13: {get_bit(n, i)}")

# Output:
# Bit 0 of 13: 1
# Bit 1 of 13: 0
# Bit 2 of 13: 1
# Bit 3 of 13: 1

# ─────────────────────────────
# USEFUL: Count number of bits needed to represent n
# ─────────────────────────────
def bit_length(n):
    count = 0
    while n > 0:
        n >>= 1   # Same as: n = n >> 1
        count += 1
    return count

print(bit_length(7))    # Output: 3  (111 needs 3 bits)
print(bit_length(255))  # Output: 8  (11111111 needs 8 bits)
```

#### ✅ Practice Problem

1. What is `48 >> 4`? Verify with the formula.
2. What is `−8 >> 1`? Show the bit-level steps.
3. Using right shift and AND, extract all 4 bits of `n = 9` (binary: `1001`) one at a time.

<details>
<summary>💡 Click to reveal solutions</summary>

```
1. 48 >> 4 = 48 ÷ 16 = 3
   48 = 0011 0000 → shift right 4 → 0000 0011 = 3 ✅

2. −8 >> 1:
   +8  = 0000 1000
   Flip = 1111 0111
    +1  = 1111 1000  (−8 in 2's complement, MSB=1)
   Shift right by 1 (fill with 1):
   1111 1100
   Verify: flip→0000 0011=3, +1→0000 0100=4, negative → −4
   Check: −8 ÷ 2 = −4 ✅

3. n = 9 = 1001
   Bit 0: (9 >> 0) & 1 = 9 & 1 = 1
   Bit 1: (9 >> 1) & 1 = 4 & 1 = 0
   Bit 2: (9 >> 2) & 1 = 2 & 1 = 0
   Bit 3: (9 >> 3) & 1 = 1 & 1 = 1  ✅
```
</details>

> ⚠️ **Common Mistake:** Assuming right shift always rounds toward zero. It actually rounds toward negative infinity (floors). So `−7 >> 1` gives `−4`, not `−3`. This matches true floor division: `math.floor(−7 / 2) = −4`.

---

## ⚡ Quick Reference Cheat Sheet

### Operators at a Glance

| Operator | Symbol | Rule | Example | Result |
|---|---|---|---|---|
| **AND** | `&` | 1 only if both are 1 | `5 & 3` | `1` |
| **OR** | `\|` | 1 if at least one is 1 | `5 \| 3` | `7` |
| **XOR** | `^` | 1 if bits are different | `5 ^ 3` | `6` |
| **NOT** | `~` | Flip all bits | `~5` | `-6` |
| **Left Shift** | `<<` | Move bits left, fill 0s | `3 << 2` | `12` |
| **Right Shift** | `>>` | Move bits right, sign-extend | `20 >> 2` | `5` |

---

### Useful Formulas

| Goal | Formula | Example |
|---|---|---|
| Check if odd | `n & 1 == 1` | `7 & 1 → 1 (odd)` |
| Check if even | `n & 1 == 0` | `8 & 1 → 0 (even)` |
| Get bit at pos i | `(n >> i) & 1` | `(13>>2)&1 → 1` |
| Set bit at pos i | `n \| (1 << i)` | `5 \| (1<<3) → 13` |
| Clear bit at pos i | `n & ~(1 << i)` | `13 & ~(1<<2) → 9` |
| Toggle bit at pos i | `n ^ (1 << i)` | `5 ^ (1<<0) → 4` |
| Multiply by 2ᵏ | `n << k` | `3 << 2 → 12` |
| Divide by 2ᵏ | `n >> k` | `20 >> 2 → 5` |
| NOT formula | `~n = -(n+1)` | `~5 → -6` |
| Zero a number | `n ^ n = 0` | `7 ^ 7 → 0` |
| Find unique in array | XOR all elements | `[1,2,1] → 2` |
| Swap without temp | `a^=b; b^=a; a^=b` | `(10,20)→(20,10)` |

---

### Common Mistakes — Master Checklist

| ❌ Mistake | ✅ Correct Approach |
|---|---|
| Using `^` for power (`2^3`) | Use `2**3` for powers in Python |
| Using `&` instead of `and` for logic | `&` is bitwise; `and` is logical |
| Thinking `~n` gives unsigned flip | `~n = -(n+1)`, always negative in Python |
| Filling negative right-shifts with 0s | Fill with **1s** (sign extension!) |
| Making negative numbers by prepending 1 | Use full **2's complement** process |
| Assuming left shift is always safe | Can **overflow** in C/Java (safe in Python) |
| Forgetting `~` precedence | `~1 << 2` is `(~1) << 2` — use parentheses! |

---

> 🎉 **Congratulations!** You've reached the end of the guide. Bit manipulation is one of those topics that feels confusing at first but *clicks* once you see the patterns. Keep practicing with the problems above, and soon you'll be reaching for bitwise operators instinctively. Happy coding! 💻
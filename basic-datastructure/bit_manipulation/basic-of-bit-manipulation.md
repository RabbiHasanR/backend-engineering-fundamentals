# **The Ultimate Guide to Binary Numbers and Bitwise Operators**

Computers do not speak decimal (); they speak binary (). Every piece of data—text, images, code—is ultimately stored as a sequence of bits (Binary Digits).

This guide explains how numbers are stored in a computer's memory, how to convert them, and how to manipulate them using bitwise operators.

---

## **Part 1: The 32-Bit Integer Container**

In modern computing, integers are commonly stored in a **32-bit** format. Think of this as a fixed box with exactly 32 slots (indices 0 to 31) that must always be filled with either a `0` or a `1`.

### **1. The Layout**

* **Total Bits:** 32
* **Indices:**  (Rightmost) to  (Leftmost).
* **Index 0-30:** Store the **magnitude** (value) of the number.
* **Index 31 (MSB):** The **Sign Bit**.

### **2. The Sign Bit Rule**

The Most Significant Bit (the one at index 31) acts as a flag for the number's sign:

* **`0`** = Positive Number ()
* **`1`** = Negative Number ()

### **3. Storage Limits**

Since 1 bit is reserved for the sign, we have 31 bits left for the value.

* **Formula:** Range is  to .
* **Max Value:** 
* **Min Value:** 

---

## **Part 2: Binary Conversions**

### **1. Decimal to Binary**

To convert a decimal number (base-10) to binary (base-2), we use the **Division Method**.

**Steps:**

1. Divide the number by 2.
2. Record the quotient and the remainder ( or ).
3. Repeat until the quotient is .
4. Write remainders from **bottom to top**.

**Example: **
| Division | Quotient | Remainder |
| :--- | :--- | :--- |
|  | 3 | **1** |
|  | 1 | **1** |
|  | 0 | **1** |

* **Result:** `111`
* **In 32-bit Memory:** The computer pads the left with zeros:
`00000000 00000000 00000000 00000111`

### **2. Binary to Decimal**

To convert binary back to decimal, use the **Position Formula**.


**Example: **

* 
* 
* 
* 
* **Total:** 

---

## **Part 3: Negative Numbers (Complements)**

Computers do not store a "minus sign." Instead, they use **2's Complement** to represent negative values.

### **1. 1's Complement**

**Definition:** Simply flip every bit in the number.

* 
* 

> *Example (7 to -7 step 1):*
> Binary 7: `000...0111`
> Flip it: `111...1000`

### **2. 2's Complement (The Standard)**

**Definition:** Take the 1's Complement and **add 1**.

> *Example (Completing the -7):*
> 1. Start with flipped bits: `111...1000`
> 2. Add 1: `111...1000 + 1`
> 3. Result: `111...1001`
> 
> 

---

## **Part 4: Bitwise Operators**

These operators work on the individual bits of the numbers.

### **1. AND (`&`)**

**Logic:** True (1) only if **both** bits are True.

| A | B | Result |
| --- | --- | --- |
| 1 | 1 | **1** |
| 1 | 0 | **0** |
| 0 | 1 | **0** |
| 0 | 0 | **0** |

### **2. OR (`|`)**

**Logic:** True (1) if **at least one** bit is True.

| A | B | Result |
| --- | --- | --- |
| 1 | 1 | **1** |
| 1 | 0 | **1** |
| 0 | 1 | **1** |
| 0 | 0 | **0** |

### **3. XOR (`^`)**

**Logic:** True (1) if bits are **different** (Odd number of 1s).

| A | B | Result |
| --- | --- | --- |
| 1 | 0 | **1** |
| 0 | 1 | **1** |
| 1 | 1 | **0** |
| 0 | 0 | **0** |

### **4. NOT (`~`)**

**What is it?**
The NOT operator inverts all bits (). This is technically just the **1's Complement**.

**How to calculate the Decimal Value (Signed Integers):**
Because computers store numbers in **2's Complement**, the result of a NOT operation on a number  is mathematically:


**Manual Calculation Steps (Your Logic):**
If you want to find the decimal value manually without a calculator:

1. **Flip** all the bits of the number.
2. **Check the MSB (Most Significant Bit / Leftmost bit):**
* **If MSB is 0 (Positive):** Convert directly to decimal.
* **If MSB is 1 (Negative):** The computer is storing a negative number. To find out *which* negative number:
* Take the **2's Complement** of this result (Flip again and add 1).
* Convert that to decimal.
* Add a negative sign to the final answer.





**Example 1: NOT 5 (`~5`)**

* **Step 1 (Binary):** 5 is `0000 0101`
* **Step 2 (Flip):** `1111 1010`
* **Step 3 (Check):** The first bit is **1**, so it is negative.
* **Step 4 (Find Magnitude):**
* Flip `1111 1010`  `0000 0101`
* Add 1  `0000 0110` (Decimal 6)


* **Step 5 (Result):** Since it was negative, the answer is **-6**.

**Example 2: NOT -6 (`~-6`)**

* **Step 1 (Binary):** -6 is stored as `1111 1010` (from previous example).
* **Step 2 (Flip):** `0000 0101`
* **Step 3 (Check):** The first bit is **0**, so it is positive.
* **Step 4 (Convert):** `0000 0101` is **5**.
* **Result:** **5**.

---

## **Part 5: Shift Operators**

Here is a detailed, step-by-step breakdown of the **Left Shift** and **Right Shift** operators. I will use 8-bit visual examples (instead of 32-bit) to make it easier to see, but the logic is exactly the same for 32-bit integers.

### **1. LEFT SHIFT (`<<`)**

**The Concept:**
Imagine pushing the entire train of bits to the **left**.

1. **Left Side:** The bits on the far left fall off the edge and are lost forever.
2. **Right Side:** Empty spaces open up on the right. We always fill these spaces with **`0`s**.

**Mathematical Meaning:**
Shifting left by **1** is equivalent to **multiplying by 2**.
Shifting left by **k** is equivalent to **multiplying by **.

#### **Example: **

We want to shift the number 3 to the left by 2 positions.

* **Step 1: Write 3 in Binary**
`0000 0011`
* **Step 2: Shift everything Left by 2**
The two `0`s on the far left fall off.
The `11` moves two spots to the left.
Two empty spots appear on the right.
`0000 0011`  `0000 11__` (Empty slots)
* **Step 3: Fill with Zeros**
`0000 1100`
* **Step 4: Calculate Decimal**


> **Math Check:** . (Matches!)

---

### **2. RIGHT SHIFT (`>>`)**

**The Concept:**
Imagine pushing the entire train of bits to the **right**.

1. **Right Side:** The bits on the far right fall off the edge and are lost.
2. **Left Side:** Empty spaces open up on the left. What do we fill them with?
* **If the number is Positive (starts with 0):** Fill with **`0`**.
* **If the number is Negative (starts with 1):** Fill with **`1`**.
* *Note: This rule is called "Sign Extension." It ensures negative numbers stay negative.*



**Mathematical Meaning:**
Shifting right by **k** is equivalent to **dividing by ** (Integer division, rounding down).

#### **Example A: Positive Number ()**

We want to shift 20 right by 2 positions.

* **Step 1: Write 20 in Binary**
`0001 0100` (Sign bit is **0**, so it's positive)
* **Step 2: Shift Right by 2**
The `00` on the far right falls off.
`__00 0101` (Empty slots on left)
* **Step 3: Fill with Sign Bit (0)**
`0000 0101`
* **Step 4: Calculate Decimal**


> **Math Check:** . (Matches!)

---

#### **Example B: Negative Number ()**

This is where it gets tricky. We want to shift -20 right by 2 positions.

* **Step 1: Write -20 in Binary (2's Complement)**
 is `0001 0100`.
Flip bits: `1110 1011`.
Add 1: `1110 1100`.
**Binary for -20:** `1110 1100` (Sign bit is **1**, so it's negative)
* **Step 2: Shift Right by 2**
The `00` on the far right falls off.
`__11 1011` (Empty slots on left)
* **Step 3: Fill with Sign Bit (1)**
Because the original number was negative, we fill the empty spots with **1s**.
`1111 1011`
* **Step 4: Verify Result**
This is a negative number (starts with 1). Let's convert it back to decimal to check:
1. Binary: `1111 1011`
2. Flip: `0000 0100`
3. Add 1: `0000 0101` (Decimal 5)
4. Result: **-5**



> **Math Check:** . (Matches!)
> *If we had filled with 0s, the binary would have become positive (`0011 1011` = 59), which would be the wrong answer for division.*

---

## **Quick Reference Cheat Sheet**

| Operator | Symbol | Action | Formula | 32-bit Note |
| --- | --- | --- | --- | --- |
| **AND** | `&` | Both 1  1 | - | - |
| **OR** | `|` | Any 1  1 | - | - |
| **XOR** | `^` | Different  1 | - | - |
| **NOT** | `~` | Flip all bits |  | Flips sign bit too. |
| **Left Shift** | `<<` | Move Left |  | Can cause overflow. |
| **Right Shift** | `>>` | Move Right |  | Preserves sign (Sign Extension). |
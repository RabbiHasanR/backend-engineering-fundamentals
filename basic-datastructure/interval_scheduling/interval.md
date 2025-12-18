To master Interval Scheduling problems (common in coding interviews and algorithm design), you need to understand specific **Greedy algorithms**, **Sorting techniques**, and the **Sweep Line** concept.

Here is a breakdown of what you need to learn and the specific patterns to master.

### 1. The Core Prerequisites

Before tackling the patterns, ensure you understand these fundamentals:

* **Interval Representation:** Understanding an interval as a pair `[start, end]`.
* **Sorting is Key:** 90% of interval problems start by **sorting** the intervals. You must understand *how* to sort them (usually by Start Time, sometimes by End Time) to reveal the solution.
* **Overlap Logic:** Be comfortable checking if two intervals `A` and `B` overlap.
* *Condition:* `A.start < B.end` AND `A.end > B.start`.



---

### 2. The 4 Essential Patterns

#### Pattern A: Merge Intervals (The "Coalescing" Pattern)

This is used when you need to combine overlapping time slots into a single continuous block.

* **The Goal:** Simplify a list of intervals by merging any that touch or overlap.
* **The Technique:**
1. **Sort** by Start Time.
2. Iterate through the sorted list.
3. If `current_interval.start <= previous_interval.end`, they overlap. **Merge them** by updating the previous end time to `max(prev.end, curr.end)`.


* **Classic Problem:** *Merge Intervals*.

#### Pattern B: Max Non-Overlapping Intervals (The "Greedy" Pattern)

This is the classic "Interval Scheduling" problem. You want to attend as many meetings as possible, but you cannot attend two at once.

* **The Goal:** Find the maximum number of intervals that can be selected without any overlaps.
* **The Technique:**
1. **Sort** by **End Time** (ascending).
2. Pick the first interval.
3. Iterate through the rest; if an interval starts *after* the previous one ends, pick it and update your "end time" reference.
4. Discard any that start before the current one ends.


* **Classic Problem:** *Non-overlapping Intervals* or *Activity Selection Problem*.

#### Pattern C: Meeting Rooms II (The "Heap" or "Chronological" Pattern)

This pattern is used to find the *minimum resources* required (e.g., "How many conference rooms do we need?" or "What is the max CPU load?").

* **The Goal:** Find the maximum number of overlapping intervals at any single point in time.
* **The Technique (Min-Heap approach):**
1. **Sort** intervals by Start Time.
2. Use a **Min-Heap** to store the *End Times* of ongoing meetings.
3. For every new meeting, check the top of the heap (the meeting ending soonest).
4. If the new meeting starts *after* the top of the heap ends, pop the heap (reuse that room).
5. Push the new meeting's end time onto the heap.
6. The size of the heap tells you the rooms needed.


* **Classic Problem:** *Meeting Rooms II* or *Minimum Platforms required for a Railway Station*.

#### Pattern D: The Sweep Line (Point-Based Processing)

This is a powerful variation for complex overlap counting.

* **The Goal:** Visualize time as a line and "sweep" across it to count events.
* **The Technique:**
1. Deconstruct each interval `[start, end]` into two separate events: `(start, +1)` and `(end, -1)`.
2. **Sort** all events by time.
3. Iterate through the sorted events, adding the `+1` or `-1` to a running counter.
4. The maximum value of the counter represents the maximum overlap.



---

### 3. Cheat Sheet: Which Sort to Use?

| Problem Type | Sorting Strategy | Why? |
| --- | --- | --- |
| **Merge Overlaps** | Sort by **Start Time** | You need to know when the next block begins to extend the current one. |
| **Max # of Items** | Sort by **End Time** | Finishing a task early leaves more room for future tasks (Greedy). |
| **Min Resources** | Sort by **Start Time** | You need to process meetings in the order they arrive to assign rooms. |

### 4. Advanced Concept: Weighted Interval Scheduling

Sometimes intervals have a "weight" or "profit" (e.g., one long job pays more than two short jobs).

* **The Twist:** The "Greedy" approach (Pattern B) fails here.
* **The Solution:** You must use **Dynamic Programming (DP)** combined with Binary Search to find the optimal set.

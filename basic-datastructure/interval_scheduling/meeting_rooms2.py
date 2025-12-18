# Problem Statement: Meeting Rooms II
# You are given an array of meeting time intervals consisting of start and end times [[s1,e1],[s2,e2],...].
# Find the minimum number of conference rooms required to hold all meetings without overlap.

# 🔹 Example Input and Output
# Example 1
# intervals = [[0,30],[5,10],[15,20]]
# Meeting A: [0,30]

# Meeting B: [5,10]

# Meeting C: [15,20]

# Timeline:

# Meeting A overlaps with both B and C.

# B and C don’t overlap with each other, but both overlap with A.

# So we need 2 rooms.

# ✅ Output:
# 2


# Example 2
# intervals = [[7,10],[2,4]]

# Meeting A: [7,10]

# Meeting B: [2,4]

# Timeline:

# No overlap.

# Only 1 room needed.

# ✅ Output:
# 1


# 1. Brute Force Approach
# Idea
# For each meeting, try to place it in an existing room.

# If it overlaps with all current rooms, allocate a new room.

# Keep track of room schedules explicitly.

# Steps
# Sort meetings by start time.

# Maintain a list of rooms, each storing the end time of the last meeting scheduled there.

# For each meeting:

# Check if it can fit into any existing room (meeting start ≥ room’s last end).

# If yes → update that room’s end time.

# If no → add a new room.

# Answer = number of rooms.

# time O(n^2) and space o(n)

def minMeetingRoomsBruteForce(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0
    
    intervals.sort(key=lambda x: x[0])  # sort by start time
    rooms = []
    for start, end in intervals:
        placed = False
        for i in range(len(rooms)):
            if rooms[i] <= start:
                rooms[i] = end
                placed = True
                break
        if not placed:
            rooms.append(end)
    return len(rooms)

print(minMeetingRoomsBruteForce([[0,30],[5,10],[15,20]]))
print(minMeetingRoomsBruteForce([[7,10],[2,4]]))


# 2. Optimized Min-Heap Approach
# Idea
# Use a min-heap to track the earliest ending meeting:

# Sort meetings by start time.

# Push end times into heap.

# If the current meeting starts after the earliest ending meeting, pop from heap (reuse room).

# Always push current meeting’s end time.

# Heap size = number of rooms needed.

# time O(nlogn) and space O(n)

import heapq

def minMeetingRoomHeap(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0
    heap = []
    intervals.sort(key=lambda x: x[0])
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heappop(heap)
        heapq.heappush(heap, end)
    return len(heap)

print(minMeetingRoomHeap([[0,30],[5,10],[15,20]]))
print(minMeetingRoomHeap([[7,10],[2,4]]))

# 3. optimal two-pointer sweep line solution
# time O(nlogn) and space o(n)
# Core Idea
# Separate all start times and end times into two sorted lists.

# Use two pointers (i for starts, j for ends) to simulate the timeline:

# If a meeting starts before the earliest meeting ends → need a new room (count += 1).

# If a meeting starts after or exactly when another ends → free a room (count -= 1).

# Track the maximum number of rooms in use (res = max(res, count)).

# This is essentially a sweep line algorithm: walk through time, tracking how many meetings are active.


def minMeetingRooms(intervals: list[list[int]]) -> int:
    start = sorted([item[0] for item in intervals])
    end = sorted([item[1] for item in intervals])
    
    res, count = 0, 0
    i, j = 0, 0
    
    while i < len(start):
        if start[i] < end[j]:
            i += 1
            count += 1
        else:
            j += 1
            count -= 1
        
        res = max(res, count)
    return res


print(minMeetingRooms([[0,30],[5,10],[15,20]]))
print(minMeetingRooms([[7,10],[2,4]]))
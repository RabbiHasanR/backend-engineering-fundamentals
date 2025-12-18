# Problem Statement:  
# You are given an array of meeting time intervals consisting of start and end times [[s1,e1],[s2,e2],...].
# Determine if a person could attend all meetings (i.e., no overlaps).

# 🔹 Example Input & Output
# Example 1

# intervals = [[0,30],[5,10],[15,20]]

# Meeting A: [0,30]

# Meeting B: [5,10]

# Meeting C: [15,20]

# Here, Meeting A overlaps with both B and C.
# ✅ Output: False (cannot attend all meetings)


# Example 2

# intervals = [[7,10],[2,4]]

# Meeting A: [7,10]

# Meeting B: [2,4]

# No overlap.
# ✅ Output: True (can attend all meetings)


# brute force

def canAttendMeetingsBruteForce(intervals: list[list[int]]) -> bool :
    for i in range(len(intervals)):
        for j in range(i+1, len(intervals)):
            if not (intervals[i][1] <= intervals[j][0] or intervals[j][1] <= intervals[i][0]): return False
    return True

# optimal solution. first sort based on start time and then check current start time is smaller then previous end time then overlap
# time O(nlogn) and space  O(1) (ignoring input sort, which might require O(n) extra space depending on language).

def canAttendMeetings(intervals: list[list[int]]):
    intervals.sort(key=lambda x: x[0])
    
    for i in range(1, len(intervals)):
        prev_meetings = intervals[i-1]
        curr_meetings = intervals[i]
        
        if curr_meetings[0] < prev_meetings[1]:
            return False
    return True


print(canAttendMeetings([[0,30],[5,10],[15,20]]))

print(canAttendMeetings([[7,10],[2,4]]))

print(canAttendMeetingsBruteForce([[0,30],[5,10],[15,20]]))

print(canAttendMeetingsBruteForce([[7,10],[2,4]]))
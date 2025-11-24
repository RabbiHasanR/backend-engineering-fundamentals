def maximum_subarray(nums, k):
    prefix_nums = {0:-1}
    curr_sum = 0
    max_len = 0
    
    for i in range(len(nums)):
        curr_sum += nums[i]
        if curr_sum - k in prefix_nums:
            max_len = max(max_len, i - prefix_nums[curr_sum - k])
        if curr_sum not in prefix_nums:
            prefix_nums[curr_sum] = i
    return max_len


nums = [1,-1,5,-2,3]
k = 3

print(maximum_subarray(nums, k))
def convertToBinary(n: int) -> str:
    res = []
    
    while n > 0:
        if n % 2 == 0: res.append("0")
        else: res.append("1")
        
        n = n // 2
    return "".join(res[::-1])

print(convertToBinary(7))


def convertToDecimal(n: str) -> int:
    
    res = 0
    p = 1
    for i in range(len(n)-1, -1, -1):
        if n[i] == "1":
            res += p
        p *= 2
    return res

print(convertToDecimal("1101"))


# swap two numbers




a = 5
b = 6

# output
# a = 6
# b = 5

#a,b=b,a  # this is swaping 

# solve using bit manipulation

a = a ^ b  
b = a ^ b  # which is a ^ b ^ b . so b ^ b is 0 so here b = a
a = a ^ b  # which is a ^ b ^ a. because now b = a..so a ^ a is 0 and here a = b

print(a,b)

# check is the ith bit is set or not

n = 13
i = 1

# brute force approch ..convert 13 to binary (1101). so from right if index start 0 then 2 bit is 1. so it is set. if i = 1 then 1 bit is 0 which is not set

# solve using bit manipulation
# using left shift operator
res = (n&(1<<i)) !=0
print(res)

# using right shift operator

res = ((n >> i) & 1) != 0
print(res)


# set the ith bit
n = 4
i = 1

# brute force approch. convert 4 to binary 1001. and now from right index 0 to index 2.change this bit to 1 from any bit 0 or 1. now answer is 1101.

# solve using bit manipulation
# using left shift operator
res = n | (1 << i)
print(res)


# clear the ith bit
n = 13
i = 2

# brute force approch. convert 13 to binary and now from right index 0 to index i and change this bit to 0

## solve using bit manipulation

res = n & (~(1<<i))
print(res)

# toggole the ith bit

n = 13
i = 2

# brute force approch. convert 13 to binary and now from right index 0 to index i and change this bit if 1 then 0 if 0 then 1

# using bit manipulation
res = n ^ (1<<i)
print(res)


# remove the last set bit(rightmost)
n = 12

# brute force approch. convert n to binary and find first 1 bit from right and make it 0. 

# using bit manipulation

res = n & n - 1
print(res)


# check is the number is a power of 2 or not
n = 32

# brute force approch. convert n to binary and count 1 bit if 1 bit count is 1 then this is power of 2 else not

# using bit manipulation

res = (n & n -1) == 0
print(res)

# count the number of set bits

n = 13

# brute force time O(logn)

def countSetBit(n):
    count = 0
    
    while n > 0:
        if n % 2 == 0:
            n = n // 2
        else:
            count += 1
            n = n // 2
    return count
print(countSetBit(n))


# bit manipulation

def countSetBitOptimize(n):
    count = 0
    
    while n > 0:
        count += n & 1
        n = n >> 1
    return count
print(countSetBitOptimize(n))
# another approch

def countSetBitAnother(n):
    count = 0
    while n != 0:
        n = n & n - 1
        count += 1
    return count

print(countSetBitAnother(n))
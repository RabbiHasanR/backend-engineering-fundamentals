import sys
from collections import abc

# without generator

def square_numbers(nums):
    result = []
    for i in nums:
        result.append(i*i)
    return result

print(sys.getsizeof(square_numbers))
my_nums = square_numbers([1,2,3,4,5])
print(sys.getsizeof(my_nums))
print(my_nums)
        
        
        
# with generator

def square(nums):
    for i in nums:
        yield (i * i)

print(sys.getsizeof(square))
my_nums = square([1,2,3,4,5])
print(sys.getsizeof(my_nums))
print(my_nums)
for num in my_nums:
    print(num)

# print(next(my_nums))
# print(next(my_nums))
# print(next(my_nums))
# print(next(my_nums))
# print(next(my_nums))
my_nums = [x*x for x in [1,2,3,4,5]]
print(sys.getsizeof(my_nums))
print(my_nums)
my_nums = (x*x for x in [1,2,3,4,5])
print(sys.getsizeof(my_nums))
print(my_nums)


my_nums = [x*x for x in range(10000000)]
print(sys.getsizeof(my_nums))
# print(my_nums)
my_nums = (x*x for x in range(10000000))
print(sys.getsizeof(my_nums))
print(my_nums)

print(isinstance(my_nums, abc.Iterable))


def topten():
    yield 1
    yield 2
    yield 3
    yield 4


values = topten()
print(values.__next__())


def topten_square():
    n = 1
    while n <= 10:
        sq = n * n
        yield sq
        n += 1
        
squares = topten_square()
# for i in squares:
#     print(i)
    

while True:
    try:
        value = next(squares)
        print(value)
    except StopIteration:
        print('Done')
        break    
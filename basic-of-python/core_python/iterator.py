nums = [7,8,9,5]
it = iter(nums)

# print(it.__next__())
# print(it.__next__())
# print(it.__next__())
# print(it.__next__())
# print(it.__next__())  # get error

# print(next(it))
# print(next(it))
# print(next(it))
# print(next(it))


# custom iterator

class TopTen:
    def __init__(self):
        self.num = 1
    
    def __iter__(self):
        return self
    def __next__(self):
        if self.num <= 10:
            val = self.num
            self.num += 1
            return val
        raise StopIteration
    
values = TopTen()

print(next(values))

for i in values:
    print(i)

# print(values.__next__())


class MyRange:
    def __init__(self, start, end):
        self.value = start
        self.end = end
        
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.value >= self.end:
            raise StopIteration
        current = self.value
        self.value += 1
        return current
    
nums = MyRange(1,10)
# for num in nums:
#     print(num)
print(next(nums))
print(next(nums))
print(next(nums))
print(next(nums))



class Sentence:
    def __init__(self, sentence: str):
        self.sentence = sentence
        self.index = 0
        self.words = self.sentence.split()
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.words):
            raise StopIteration
        current = self.words[self.index]
        self.index += 1
        return current
    
sentence = Sentence("This is a test")

for word in sentence:
    print(word)
    
    
    
nums = [1,2,3]

print(dir(nums))

print(dir(iter(nums)))


# class Words:
#     def __init__(self):
#         self.values = ['a', 'b', 'c']
    
#     # def __iter__(self):
#     #     return self
    
#     def __getitem__(self, index):
#         return self.values[index]
    
# from collections import abc
# w = Words()
# print(isinstance(w, abc.Iterable))
# for i in w:
#     print(i)
    
    

class MyRange:
    def __init__(self, limit):
        self.limit = limit  # Stored data configuration

    def __iter__(self):
        # The Iterable returns an Iterator
        return MyRangeIterator(self.limit)

class MyRangeIterator:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0  # <--- INTERNAL STATE (Memory of where we are)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < self.limit:
            num = self.current
            self.current += 1  # Update state
            return num
        else:
            raise StopIteration  # Signal to stop
    
    

# my_range = MyRange(10)

# for num in my_range:
#     print(num)


r = range(10)

for i in r:
    print(i)
    
for i in r:
    print(i)
    
    


import sys

# 1. List Comprehension
my_list = [x for x in range(10**7)]
print(f"List Memory: {sys.getsizeof(my_list) // 1024 // 1024} MB")  
# Output: List Memory: 84 MB

# 2. Generator Expression
my_gen = (x for x in range(10**7))
print(f"Gen Memory:  {sys.getsizeof(my_gen)} Bytes")
# Output: Gen Memory:  200 Bytes










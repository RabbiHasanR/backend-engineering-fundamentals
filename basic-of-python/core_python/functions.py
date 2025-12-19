# # closures
# a = 10
# x = 5
# l = [1,2,3,4]
# def outer_func(message):
#     a = "fuck"
#     x = 10
#     def inner_func():
#         print(f"Message: {message} {a}")
#     return inner_func


# my_clousers = outer_func("Hello World")

# print(dir(my_clousers))
# print(my_clousers.__closure__)
# my_clousers()


# print(globals())



def outer():
    x = 10
    
    def inner():
        return x

# Accessing the "Blueprint" (Code Object)
code_obj = outer.__code__

print("--- 1. Variable Names (co_varnames) ---")
print(code_obj.co_varnames)
# Output: ('x', 'inner') 
# Explanation: It knows these names will exist.

print("\n--- 2. Constants (co_consts) ---")
print(code_obj.co_consts)
# Output: (None, 10, <code object inner at 0x...>)
# Explanation: 
# - '10' is waiting here. 
# - The 'inner' function is just a dead Code Object waiting here.

print("\n--- 3. Cell Variables (co_cellvars) ---")
print(code_obj.co_cellvars)
# Output: ('x',)
# Explanation: This marks 'x' as special because 'inner' needs it (Closure).



# lambda

double = lambda x: x * 2

print(double(2))

f = lambda x: x + 1
print(f)
print(dir(f))
print(f(2))

students = [("Alice", 25), ("Bob", 20), ("Charlie", 30)]
students.sort(key=lambda x: x[1])
print(students)


print((lambda x, y: x + y)(5,4))


# higher order funciton

def add(a,b): return a + b
def multiply(a,b): return a * b


def compute(action: function, x: int, y: int) -> int:
    print(f"I am about to run the function: {action.__name__}")
    return action(x, y)

result = compute(add, 5,3)
print(result)


def get_greeter(tone: str) -> function:
    def shout(name: str) -> str:
        return f"{name.upper()}"
    
    def whisper(name: str) -> str:
        return f"{name.lower()}"
    
    if tone == "loud":
        return shout
    return whisper


my_func = get_greeter("loud")
print(my_func("Alice"))


nums = [1,2,3]
squared = list(map(lambda x: x**2, nums))
print(squared)

nums  = [1,2,3,4]
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)

words = ["apple", "bat", "cat", "zebra"]
print(sorted(words, key=len))


def wrapper(original_func: function) -> function:
    def inner():
        print("Before call")
        original_func()
        print("After call")
    return inner

@wrapper
def say_hello():
    print("Hello!")
    
say_hello()
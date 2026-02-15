# Simple Decorators

# decorator without parameters
def decorator(func):
    def wrapper():
        print("Before calling the function.")
        func()
        print("After calling the function.")
    return wrapper

@decorator
def greet():
    print("Hello world")
    
greet()


# decorator with parameters

def decorator_name(func):
    def wrapper(*args, **kwargs):
        print("Before execution")
        result = func(*args, **kwargs)
        print("After execution")
        return result
    return wrapper

@decorator_name
def add(a, b):
    return a + b
print(add(5,3))


# functions as first-class objects
# Assigning a function to a variable
def greet_two(n):
    return f"Hello, {n}!"
say_hi = greet_two  # Assign the greet function to say_hi
print(say_hi("Alice")) 

# passing a function as an argument
def apply(f, v):
    return f(v)
res = apply(say_hi, "Bob")
print(res)


# Returning a function from another function
def make_mult(f):
    def mul(x):
        return x * f
    return mul

dbl = make_mult(2)
print(dbl(5))

# higher order function
# A higher-order function that takes another function as an argument
def fun(f: function, x: int) -> function:
    return f(x)
# A simple function to pass
def square(x: int) -> int:
    return x * x
res = fun(square, 5)  # Using apply_function to apply the square function
print(res)

# function decorators

def simple_decorator(func):
    def wrapper():
        print(">>> Starting function")
        func()
        print(">>> Function finished")
    return wrapper

@simple_decorator
def greet_three():
    print("Hello, World!")
greet_three()
# Method Decorators

def method_decorator(func):
    def wrapper(self, *args, **kwargs):
        print("Before method execution")
        res=func(self, *args, **kwargs)
        print("After method execution")
        return res
    return wrapper

class MyClass:
    @method_decorator
    def say_hello(self):
        print("Hello!")
obj = MyClass()
obj.say_hello()

# Class Decorators
from typing import TypeVar

T = TypeVar("T", bound=type)

def fun(cls: T) -> T:
    cls.class_name = cls.__name__
    return cls

@fun
class Person:
    pass

print(Person.class_name)


# Built in decorators

class MathOperations:
    @staticmethod
    def add(x, y):
        return x + y
    
res = MathOperations.add(5, 3)
print(res)


class Employee:
    raise_amount = 1.05
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    
    @classmethod
    def set_raise_amount(cls, amount):
        cls.raise_amount = amount
Employee.set_raise_amount(1.10)
print(Employee.raise_amount)



class Circle:
    def __init__(self, radius):
        self._radius = radius
        
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value >= 0:
            self._radius = value
        else:
            raise ValueError("Radius cannot be negative")
    @property
    def area(self):
        return 3.14159 * (self._radius ** 2)
    
c = Circle(5)

print(c.radius)
print(c.area)
c.radius = 10
print(c.area)

# chaining decorators

def decor1(func): 
    def inner(): 
        x = func() 
        return x * x 
    return inner 

def decor(func): 
    def inner(): 
        x = func() 
        return 2 * x 
    return inner 

@decor1
@decor
def num(): 
    return 10

@decor
@decor1
def num2():
    return 10
  
print(num()) 
print(num2())


# class based decorators

class UppercaseDecorator:
    def __init__(self, function: callable[..., str]) -> None:
        self.function: callable[..., str] = function
    def __call__(self, *args: any, **kwds: any) -> str:
        result = self.function(*args, **kwds)
        return result.upper()

@UppercaseDecorator    
def greet() -> str:
    return "hello there"

print(greet())


class CallCounter:
    def __init__(self, function):
        self.function = function
        self.count = 0
        
    def __call__(self, *args, **kwds):
        self.count += 1
        print(f"Function {self.function.__name__} has been called {self.count} times.")
        return self.function(*args, **kwds)

@CallCounter
def say_hello():
    print("Hello!")
    
say_hello()
say_hello()
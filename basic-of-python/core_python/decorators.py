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
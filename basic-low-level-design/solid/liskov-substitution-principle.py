# Exercise 1: The Rectangle/Square Problem
# Refactor Rectangle/Square Class
# Solved
# Problem: This is the classic LSP example. A Square class extends Rectangle but overrides setWidth and setHeight to maintain equal sides. This breaks client code that expects width and height to be independent.

# Refactor the design using a Shape interface with a getArea() method, so that Rectangle and Square are both valid shapes without one inheriting from the other.

# Requirements:

# Create a Shape interface with a getArea() method
# Implement Rectangle with independent width and height, set via constructor
# Implement Square with a single side length, set via constructor
# Neither class should extend the other
# Client code should work with any Shape without assumptions about mutability

# before lsp
# Before: Square extends Rectangle but breaks its contract
class Rectangle:
    def __init__(self):
        self.width = 0
        self.height = 0

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def get_area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # Forces equal sides

    def set_height(self, height):
        self.width = height  # Forces equal sides
        self.height = height

# Client code that breaks with Square
def resize(rect):
    rect.set_width(5)
    rect.set_height(10)
    print("Area:", rect.get_area())

resize(Rectangle())  # Area: 50
resize(Square())     # Area: 100 -- LSP violation!

# TODO: Refactor using a Shape interface (ABC) with get_area().
# TODO: Rectangle and Square should be independent implementations of Shape.


# after lsp



from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def get_area(self) -> float:
        pass


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def get_area(self) -> float:
        return self._width * self._height


class Square(Shape):
    def __init__(self, side: float):
        self._side = side

    def get_area(self) -> float:
        return self._side * self._side

if __name__ == "__main__":
    rectangle: Shape = Rectangle(5, 10)
    square: Shape = Square(5)

    print(f"Rectangle area: {int(rectangle.get_area())}")
    print(f"Square area: {int(square.get_area())}")





# Exercise 2: The Bird/Penguin Problem
# Refactor Bird/Penguin Class
# Problem:  A Bird class has both eat() and fly() methods. A Penguin subclass extends Bird but overrides fly() to throw an exception, since penguins cannot fly. Any client code that calls fly() on a Bird reference will crash at runtime when it gets a Penguin.

# Requirements:

# Create a Bird interface with only an eat() method
# Create a FlyingBird interface that extends Bird and adds a fly() method
# Sparrow implements FlyingBird (it can eat and fly)
# Penguin implements Bird (it can eat, but not fly)
# Client code that works with Bird should never call fly(), and code that needs flight should accept FlyingBird


# before lsp

# Before: Penguin extends Bird but can't fly
class Bird:
    def eat(self):
        print(f"{self.__class__.__name__} is eating")

    def fly(self):
        print(f"{self.__class__.__name__} is flying")

class Sparrow(Bird):
    pass

class Penguin(Bird):
    def fly(self):
        raise NotImplementedError("Penguins can't fly!")

def make_bird_fly(bird):
    bird.fly()  # Crashes for Penguin!

make_bird_fly(Sparrow())  # Works fine
make_bird_fly(Penguin())  # NotImplementedError!

# TODO: Split Bird into a Bird ABC (eat) and a FlyingBird ABC (fly).
# TODO: Sparrow implements FlyingBird, Penguin implements only Bird.


# after lsp

from abc import ABC, abstractmethod


class Bird(ABC):
    @abstractmethod
    def eat(self) -> None:
        pass


class FlyingBird(Bird):
    @abstractmethod
    def fly(self) -> None:
        pass


class Sparrow(FlyingBird):
    def eat(self) -> None:
        print("Sparrow is eating")

    def fly(self) -> None:
        print("Sparrow is flying")


class Penguin(Bird):
    def eat(self) -> None:
        print("Penguin is eating")


if __name__ == "__main__":
    sparrow = Sparrow()
    sparrow.eat()
    sparrow.fly()

    penguin = Penguin()
    penguin.eat()
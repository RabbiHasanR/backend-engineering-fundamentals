Class and Object: A class is the blueprint. An object is the thing you build from it.

A class is a bluprint; an object is an instance of it.

Fields hold state, methods define behavior

Each object owns its own independent copy of the data

Private fields plus methods let a class guard its own rules

This keeps state together, valid, and easy to extend.




1. What is a Class?
A class is a blueprint, template, or recipe for creating objects. It defines what an object will contain (its data) and what it will be able to do (its behavior).

A class is not an object itself, it’s a template used to create many objects with similar structure but independent state.

Key Characteristics of a Class:
It groups related data (attributes) and actions (methods) together.
Defines attributes to represent the state or data of an object.
Defines methods (functions inside a class) to represent the behavior or actions the object can perform.


2. What is an Object?
An object is an instance of a class.  It's the actual thing you can interact with, store data in, and invoke methods on.

When you create an object, you’re essentially saying:

“Take this blueprint (class) and build one actual thing (object) out of it.”

Each object gets its own copy of the data defined in the class, shares the same structure and behavior, and operates independently of every other object created from that same class.


Example:

```python
class Car:
    def __init__(self, brand, model):
        self._brand = brand
        self._model = model
        self._speed = 0

    
    def accelerate(self, increment):
        self._speed += increment
    
    def display_status(self):
        print(f"{self._brand} is running at {self._speed}")


if __name__ == "__main__":
    corolla = Car("Toyota", "Corolla")
    mustang = Car("Ford", "Mustang")

    corolla.accelerate(20)
    mustang.accelerate(40)

    corolla.display_status()
    print("---------------")
    mustang.display_status()

# Output
# Toyota Corolla is running at 20 km/h.
# -----------------
# Ford Mustang is running at 40 km/h.
```




3. Practical Example: Online Food Order
Let's apply classes and objects to a real-world problem: building an order management system for a food delivery platform.


```python
class FoodOrder:
    def __init__(self, order_id: str, customer_name: str):
        self._order_id = order_id
        self._customer_name = customer_name
        self._items: list[str] = []
        self._total_amount = 0.0
        self._is_placed = False
    
    def add_item(self, name: str, price: float) -> None:
        if self._is_placed:
            print("Cannot modify a placed order")
            return
        self._items.append(item)
        self._total_amount += price
    
    def place_order(self) -> bool:
        if self._is_placed or not self._items:
            return False
        self._is_placed = True
        return True
    
    def get_item_count(self) -> int:
        return len(self._items)

    def display_order(self) -> None:
        status = "PLACED" if self._is_placed else "PENDING"
        print(f"Order {self._order_id} ({self._customer_name}) - {status}")
        for item in self._items:
            print(f"  - {item}")
        print(f"  Total: ${self._total_amount:.2f}")

if __name__ == "__main__":
    order1 = FoodOrder("ORD-101", "Alice")
    order1.add_item("Pizza", 12.99)
    order1.add_item("Garlic Bread", 4.99)
    order1.add_item("Coke", 2.49)
    order1.place_order()

    order2 = FoodOrder("ORD-102", "Bob")
    order2.add_item("Burger", 9.99)
    order2.add_item("Fries", 3.99)

    order1.display_order()
    print()
    order2.display_order()



# output

# Order ORD-101 (Alice) - PLACED
#   - Pizza
#   - Garlic Bread
#   - Coke
#   Total: $20.47

# Order ORD-102 (Bob) - PENDING
#   - Burger
#   - Fries
#   Total: $13.98
```
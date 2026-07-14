1. What is an Enum?
An enum (short for enumeration) is a special data type that defines a fixed set of named constants. Unlike strings or integers, enums are type-safe, meaning the compiler ensures you can only use values that actually exist in your defined set.

They ensure that a variable can only take one out of a predefined set of valid options.

Why Use Enums?
To appreciate what enums give you, consider the alternative. Without enums, you'd represent order statuses as strings scattered throughout your codebase:

```python
String status = "PENDING";

// Somewhere else in the codebase...
if (status.equals("PNDING")) {  // Typo! This condition is never true
    processOrder();
}
```

This code compiles without any warnings. The typo "PNDING" is a perfectly valid string as far as the compiler is concerned. The bug only surfaces when a customer complains that their order never gets processed.

Enums eliminate this entire category of bugs. When you define OrderStatus as an enum with values like PENDING, CONFIRMED, SHIPPED, and DELIVERED, the compiler knows exactly which values are valid.

Here are several key advantages Enums provide over plain constants or strings:

Avoid “magic values”: No more scattered strings or integers like "PENDING" or 3 in your code.
Improve readability: Enums make your intent clear — OrderStatus.SHIPPED is far more descriptive than 3.
Enable compiler checks: The compiler validates enum usage, catching typos and invalid assignments early.
Support IDE features: Most IDEs provide auto-completion and refactoring tools for enum values.
Reduce bugs: You can’t accidentally assign a random string or number that doesn’t belong to enum.
Example Enums
Enums are perfect for defining categories or states that rarely change.

Order States (e.g., PENDING, IN_PROGRESS, COMPLETED)
User Roles (e.g., ADMIN, CUSTOMER, DRIVER)
Vehicle Types (e.g., CAR, BIKE, TRUCK)
Directions (e.g., NORTH, SOUTH, EAST, WEST)
By using enums instead of raw strings, you make your system easier to understand and harder to misuse.


```python
from enum import Enum

class OrderStatus(Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# using in code
status = OrderStatus.SHIPPED
if status == OrderStatus.SHIPPED:
    print("Your package is on the way!")
```


Enums with Properties and Methods
Enums can do more than just name constants. In many languages, each enum value can hold additional data and even define behavior. This makes them surprisingly powerful for modeling domain concepts.

Let’s consider a Coin enum that represents U.S. coins and their denominations. Each coin has a name (PENNY, NICKEL, DIME, QUARTER) and a value in cents (1, 5, 10, 25). Instead of maintaining a separate lookup table for coin values, you can embed the value directly in the enum.

```python
from enum import Enum

class Coin(Enum):
    PENNY = 1
    NICKEL = 5
    DIME = 10
    QUARTER = 25
    
    def __init__(self, value):
        self.coin_value = value
    
    def get_value(self):
        return self.coin_value


# using it in code:
total = Coin.DIME.get_value() + Coin.QUARTER.get_value()  # 35
```



3. Practical Example: Order Processing System


```python
from enum import Enum

class OrderStatus(Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class PaymentMethod(Enum):
    CREDIT_CARD = ("Credit Card", 2.5)
    DEBIT_CARD = ("Debit Card", 1.0)
    UPI = ("UPI", 0.0)
    NET_BANKING = ("Net Banking", 1.5)

    def __init__(self, display_name: str, fee_parcent: float):
        self.display_name = display_name
        self.fee_percent = fee_percent


class Order:
    _status_transitions = {
        OrderStatus.PLACED: OrderStatus.CONFIRMED,
        OrderStatus.CONFIRMED: OrderStatus.SHIPPED,
        OrderStatus.SHIPPED: OrderStatus.DELIVERED,
    }

    def __init__(self, order_id: str, payment_method: PaymentMethod, amount: float):
        self._order_id = order_id
        self._status = OrderStatus.PLACED
        self._payment_method = payment_method
        self._amount = amount
    
    def advance_status(self) -> bool:
        next_status = self._status_transitions.get(self._status)
        if next_status:
            self._status = next_status
            return True
        return False

    def cancel(self) -> bool:
        if self._status in (OrderStatus.PLACED, OrderStatus.CONFIRMED):
            self._status = OrderStatus.CANCELLED
            return True
        return False
    
    def get_total_with_fees(self) -> float:
        return self._amount + (self._amount * self._payment_method.fee_percent / 100)

    def display_info(self) -> None:
        print(f"Order {self._order_id} | Status: {self._status.value} | "
              f"Payment: {self._payment_method.display_name} | "
              f"Amount: ${self._amount:.2f} (with fees: ${self.get_total_with_fees():.2f})")
    
if __name__ == "__main__":
    order = Order("ORD-001", PaymentMethod.CREDIT_CARD, 99.99)
    order.display_info()

    order.advance_status()  # PLACED -> CONFIRMED
    order.advance_status()  # CONFIRMED -> SHIPPED
    order.display_info()

    print(f"Cancel after shipping: {order.cancel()}")  # False
```
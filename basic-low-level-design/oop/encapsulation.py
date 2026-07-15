# Encapsulation in Practice: BankAccount

# Now let's see a complete encapsulated class with proper validation, controlled access, and business rules. 
# The BankAccount class keeps balance private and only allows modifications through deposit() and withdraw(), each of which enforces its own rules.

class BankAccount:
    def __init__(self, account_holder: str):
        self.__account_holder = account_holder
        self.__balance = 0.0
    
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.__balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.__balance:
            raise ValueError("Insufficient funds")
        self.__balance -= amount

    @property
    def balance(self) -> float:
        return self.__balance

    @property
    def account_holder(self) -> str:
        return self.__account_holder
    
    
if __name__ == "__main__":
    account = BankAccount("Rabbi Hasan")
    print(account.account_holder, account.balance)
    account.deposit(500)
    print(account.balance)
    account.withdraw(300)
    print(account.balance)
    
    
    
# Practical Example: PaymentProcessor
# Let’s take a more realistic example. You're building a PaymentProcessor class that handles credit card transactions. 
# The raw card number must never be stored or visible anywhere in the system. If a developer accidentally logs the payment object or inspects it in a debugger, they should only see a masked version.
# The masking logic, the amount, and the processing flow are all internal details that the caller doesn't need to worry about.


class PaymentProcessor:
    def __init__(self, card_number: str, amount: float):
        self.__card_number = self.__mask_card_number(card_number)
        self.__amount = amount

    def __mask_card_number(self, card_number: str) -> str:
        return "****-****-****-" + card_number[-4:]

    def process_payment(self) -> None:
        print(f"Processing payment of ${self.__amount} for card {self.__card_number}")


if __name__ == "__main__":
    payment = PaymentProcessor("1234567812345678", 250.00)
    payment.process_payment()
    
    
    
# Exercise 1: TemperatureSensor
# Design Temperature Sensor Class
# Solved
# Problem: Build a TemperatureSensor class that collects temperature readings and provides statistical access. The sensor should validate that readings fall within a reasonable range and never expose its internal list of readings directly.

# Requirements:

# Private list of readings
# addReading(value): adds a temperature reading, but only if it's between -50 and 150 degrees (inclusive). Reject out-of-range values.
# getAverage(): returns the average of all readings, or 0 if no readings exist
# getReadingCount(): returns how many readings have been recorded
# getReadings(): returns a copy of the readings list (not the original)




class TemperatureSensor:
    def __init__(self):
        self._readings: list[float] = []

    def add_reading(self, value: float) -> None:
        # Only add if value is between -50 and 150 (inclusive)
        if -50 <= value <= 150:
            self._readings.append(value)

    def get_average(self) -> float:
        # Return the average of all readings, or 0.0 if no readings exist
        if not self._readings:
            return 0.0
        return round(sum(self._readings) / len(self._readings), 2)

    def get_reading_count(self) -> int:
        # Return how many readings have been recorded
        return len(self._readings)

    def get_readings(self) -> list[float]:
        # Return a copy of the readings list (not the original)
        return list(self._readings)


if __name__ == "__main__":
    sensor = TemperatureSensor()
    sensor.add_reading(22.5)
    sensor.add_reading(23.1)
    sensor.add_reading(200.0)  # Should be rejected
    sensor.add_reading(-10.0)

    print(f"Count: {sensor.get_reading_count()}")  # 3
    print(f"Average: {sensor.get_average()}")       # 11.87
    


# Exercise 2: ShoppingCart
# Design ShoppingCart Class
# Problem: Build a ShoppingCart class that manages items, supports a one-time discount code, and prevents modifications after checkout.

# Requirements:

# Private map/dictionary of items (item name to price)
# Private discount code (can only be applied once)
# Private isCheckedOut flag
# addItem(name, price): adds an item, but only if the cart hasn't been checked out
# applyDiscount(code): if the code is "SAVE10" and no discount has been applied yet, marks the discount as applied and stores it. Returns success/failure.
# getTotal(): returns the sum of all prices, minus 10% if a discount was applied
# checkout(): marks the cart as checked out if it has at least one item. After checkout, no items can be added and no discounts can be applied.


class ShoppingCart:
    def __init__(self):
        self._items: dict[str, float] = {}
        self._discount_applied = False
        self._is_checked_out = False

    def add_item(self, name: str, price: float) -> None:
        # Add item to cart, but reject if already checked out
        if self._is_checked_out:
            print("Cannot modify a checked-out cart")
            return
        self._items[name] = price

    def apply_discount(self, code: str) -> bool:
        if code == "SAVE10" and not self._discount_applied and not self._is_checked_out:
            self._discount_applied = True
            return True
        return False

    def get_total(self) -> float:
        total = sum(self._items.values())
        if self._discount_applied:
            total *= 0.9
        return round(total, 2)

    def checkout(self) -> None:
        # Mark cart as checked out (only if it has items and isn't already checked out)
        if self._items and not self._is_checked_out:
            self._is_checked_out = True


if __name__ == "__main__":
    cart = ShoppingCart()
    cart.add_item("Laptop", 999.99)
    cart.add_item("Mouse", 29.99)

    print(f"Total: ${cart.get_total():.2f}")                     # 1029.98

    print(f"Discount: {str(cart.apply_discount('SAVE10')).lower()}")          # true
    print(f"Total: ${cart.get_total():.2f}")                     # 926.98

    print(f"Discount: {str(cart.apply_discount('SAVE10')).lower()}")          # false

    cart.checkout()
    cart.add_item("Keyboard", 79.99)  # Should be rejected
    print(f"Total: ${cart.get_total():.2f}")                     # 926.98
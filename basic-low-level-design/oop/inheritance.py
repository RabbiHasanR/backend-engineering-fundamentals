# The most basic form of inheritance is a child class that extends a parent class and 
# adds new behavior on top of the inherited fields and methods. Here's the vehicle hierarchy built with inheritance.




class Vehicle:
    def __init__(self, make: str, model: str, year: str):
        self._make = make
        self._model = model
        self._year = year
    
    def start_engine(self):
        print("Engine started")
    
    def stop_engine(self):
        print("Engine stopped")
    
    def display_info(self):
        print(f"{self._year} {self._make} {self._model}")


class ElectricCar(Vehicle):
    def __init__(self, make: str, model: str, year: int, battery_capacity: int):
        super().__init__(make, model, year)
        self._battery_capacity = battery_capacity
        
    def charge_battery(self):
        print(f"Charging {self._battery_capacity}kWh battery")
        

class GasCar(Vehicle):
    def __init__(self, make: str, model: str, year: int, fuel_tank_size: float):
        super().__init__(make, model, year)
        self._fuel_tank_size = fuel_tank_size

    def fill_tank(self):
        print(f"Filling {self._fuel_tank_size}L fuel tank")
        
if __name__ == "__main__":
    tesla = ElectricCar(make="Tesla", model="Model 3", year=2026, battery_capacity=75)
    toyota = GasCar(make="Toyota", model="Camry", year=2025, fuel_tank_size=60.0)

    print("--- Standard Vehicle Actions ---")
    tesla.display_info()
    toyota.display_info()

    tesla.start_engine()
    toyota.start_engine()

    print("\n--- Specific Actions ---")
    tesla.charge_battery()
    toyota.fill_tank()
    
    


# Practical Example: Notification System
# Let's apply inheritance to a completely different domain to show that these patterns aren't limited to vehicles. 
# Imagine you're building a notification system that can send messages through different channels: email, SMS, and push notifications.

# All notification types share common properties: a recipient, a message, and a timestamp. 
# They all need a formatHeader() method that produces a consistent header format. 
# But the send() method works differently for each channel, email needs a subject line, SMS has a character limit, 
# and push notifications have a device token and priority level.



from datetime import datetime


class Notification:
    def __init__(self, recipient: str, message: str):
        self._recipient = recipient
        self._message = message
        self._timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def format_header(self) -> str:
        return f"[{self._timestamp}] To: {self._recipient}"

    def send(self):
        print(self.format_header())
        print(f"Message: {self._message}")


class EmailNotification(Notification):
    def __init__(self, recipient: str, message: str, subject: str):
        super().__init__(recipient, message)
        self._subject = subject

    def send(self):
        print(self.format_header())
        print(f"Subject: {self._subject}")
        print(f"Body: {self._message}")
        print("Status: Email delivered")


class SMSNotification(Notification):
    MAX_LENGTH = 160

    def __init__(self, recipient: str, message: str, phone_number: str):
        super().__init__(recipient, message)
        self._phone_number = phone_number

    def send(self):
        print(self.format_header())
        print(f"Phone: {self._phone_number}")
        sms_body = (self._message[:self.MAX_LENGTH - 3] + "..."
                    if len(self._message) > self.MAX_LENGTH
                    else self._message)
        print(f"SMS: {sms_body}")
        print(f"Status: SMS sent ({len(sms_body)}/{self.MAX_LENGTH} chars)")


class PushNotification(Notification):
    def __init__(self, recipient: str, message: str,
                 device_token: str, priority: str):
        super().__init__(recipient, message)
        self._device_token = device_token
        self._priority = priority

    def send(self):
        print(self.format_header())
        print(f"Device: {self._device_token[:8]}...")
        print(f"Priority: {self._priority}")
        print(f"Alert: {self._message}")
        print("Status: Push notification delivered")


if __name__ == "__main__":
    email = EmailNotification(
        "alice@example.com", "Your order has been shipped!", "Order Update")
    email.send()

    print()

    sms = SMSNotification(
        "Bob", "Your verification code is 482910.", "+1-555-0123")
    sms.send()

    print()

    push = PushNotification(
        "Charlie", "New message from Alice", "d8a3f4b2c1e5a9b7", "high")
    push.send()
    
    
    
    
    
    
    
# Exercise 1: Bank Account Hierarchy
# Design Bank Account Hierarchy Class
# Solved
# Problem: Build a bank account system using inheritance. The base BankAccount class has common fields and methods for deposits and withdrawals. Specialized account types have different withdrawal rules.

# Requirements:

# Base BankAccount class with ownerName, accountNumber, and balance (protected). A deposit(amount) method that adds to the balance if the amount is positive. A withdraw(amount) method that subtracts from the balance if funds are sufficient and returns true/false. A displayAccount() method that prints the owner's name, account number, and formatted balance.
# SavingsAccount: adds an interestRate field. Overrides withdraw() to enforce a minimum balance of $100 (the withdrawal fails if it would drop the balance below $100). Adds an applyInterest() method that increases the balance by balance * interestRate / 100.
# CheckingAccount: adds an overdraftLimit field. Overrides withdraw() to allow withdrawals up to balance + overdraftLimit.
# displayAccount() should work correctly for all account types without any changes to the base class.  
    
    
    
    

class BankAccount:
    def __init__(self, owner_name: str, account_number: str, balance: float):
        # TODO: initialize self._owner_name, self._account_number, and self._balance
        self._owner_name = owner_name
        self._account_number = account_number
        self._balance = balance

    def deposit(self, amount: float) -> bool:
        # TODO: add amount to balance if amount > 0, return True if successful
        if amount > 0:
            self._balance += amount
            return True
        return False

    def withdraw(self, amount: float) -> bool:
        # TODO: subtract amount from balance if balance >= amount, return True
        if amount > 0 and self._balance >= amount:
            self._balance -= amount
            return True
        return False

    def display_account(self):
        # TODO: print "owner_name (account_number) | Balance: $balance"
        # Hint: use f"${self._balance:.2f}" for formatting
        print(f"{self._owner_name} ({self._account_number}) | Balance: ${self._balance:.2f}")


class SavingsAccount(BankAccount):
    def __init__(self, owner_name: str, account_number: str,
                 balance: float, interest_rate: float):
        super().__init__(owner_name, account_number, balance)
        # TODO: initialize self._interest_rate
        self._interest_rate = interest_rate

    def withdraw(self, amount: float) -> bool:
        # TODO: only allow if (balance - amount) >= 100
        if amount > 0 and (self._balance - amount) >= 100:
            self._balance -= amount
            return True
        return False

    def apply_interest(self):
        # TODO: add (balance * interest_rate / 100) to balance
        self._balance += (self._balance * self._interest_rate / 100)


class CheckingAccount(BankAccount):
    def __init__(self, owner_name: str, account_number: str,
                 balance: float, overdraft_limit: float):
        super().__init__(owner_name, account_number, balance)
        # TODO: initialize self._overdraft_limit
        self._overdraft_limit = overdraft_limit

    def withdraw(self, amount: float) -> bool:
        # TODO: allow if (balance + overdraft_limit) >= amount
        if amount > 0 and (self._balance + self._overdraft_limit) >= amount:
            self._balance -= amount
            return True
        return False


if __name__ == "__main__":
    savings = SavingsAccount("Alice", "SAV-001", 1000, 2.0)
    savings.display_account()
    print(f"Withdraw $950: {str(savings.withdraw(950)).lower()}")
    savings.apply_interest()
    savings.display_account()

    print()

    checking = CheckingAccount("Bob", "CHK-002", 500, 300)
    checking.display_account()
    print(f"Withdraw $700: {str(checking.withdraw(700)).lower()}")
    checking.display_account()
    
    



# Exercise 2: Shape Hierarchy
# Design Shape Hierarchy Class
# Problem: Build a shape hierarchy where the base class provides a shared describe() method, and each child class implements its own area() and perimeter() methods.

# Requirements:

# Base Shape class with a name field (protected). A describe() method that prints "Shape: [name], Area: [area], Perimeter: [perimeter]". Abstract-like area() and perimeter() methods that return 0 by default.
# Circle: takes a radius. Area = pi r^2, Perimeter = 2 pi * r.
# Rectangle: takes width and height. Area = w h, Perimeter = 2 (w + h).
# describe() should work for any shape without modification because it calls area() and perimeter() internally.



import math


class Shape:
    def __init__(self, name: str):
        self._name = name

    def area(self) -> float:
        # TODO: return 0 by default
        return 0

    def perimeter(self) -> float:
        # TODO: return 0 by default
        return 0

    def describe(self):
        # TODO: print "Shape: name, Area: area, Perimeter: perimeter"
        # Hint: use f"{value:.2f}" for formatting
        print(f"Shape: {self._name}, Area: {self.area():.2f}, Perimeter: {self.perimeter():.2f}")


class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("Circle")
        # TODO: initialize self._radius
        self._radius = radius

    def area(self) -> float:
        # TODO: return math.pi * radius * radius
        return math.pi * self._radius * self._radius

    def perimeter(self) -> float:
        # TODO: return 2 * math.pi * radius
        return 2 * math.pi * self._radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        super().__init__("Rectangle")
        # TODO: initialize self._width and self._height
        self._width = width
        self._height = height

    def area(self) -> float:
        # TODO: return width * height
        return self._width * self._height

    def perimeter(self) -> float:
        # TODO: return 2 * (width + height)
        return 2 * (self._width + self._height)


if __name__ == "__main__":
    circle = Circle(5.0)
    circle.describe()

    rect = Rectangle(4.0, 6.0)
    rect.describe()
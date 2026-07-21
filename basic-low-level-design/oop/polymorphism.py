# Suppose you’re designing a system that sends notifications. You want to support email, SMS, push notifications, etc.

class Notification:
    def __init__(self, recipient: str, message: str):
        self._recipient = recipient
        self._message = message

    def send(self):
        print(f"Sending generic notification to {self._recipient}")


class EmailNotification(Notification):
    def __init__(self, recipient: str, message: str, subject: str):
        super().__init__(recipient, message)
        self._subject = subject

    def send(self):
        print(f"Sending EMAIL to {self._recipient} | Subject: {self._subject}")


class SMSNotification(Notification):
    def __init__(self, recipient: str, message: str, phone_number: str):
        super().__init__(recipient, message)
        self._phone_number = phone_number

    def send(self):
        print(f"Sending SMS to {self._phone_number} | Message: {self._message}")


class PushNotification(Notification):
    def __init__(self, recipient: str, message: str, device_token: str):
        super().__init__(recipient, message)
        self._device_token = device_token

    def send(self):
        print(f"Sending PUSH to device {self._device_token[:8]}"
              f"... | Alert: {self._message}")


if __name__ == "__main__":
    notifications = [
        EmailNotification("alice@example.com", "Your order shipped!", "Order Update"),
        SMSNotification("Bob", "Code: 482910", "+1-555-0123"),
        PushNotification("Charlie", "New message", "d8a3f4b2c1e5a9b7"),
    ]

    for n in notifications:
        n.send()
        
        






# Exercise 1: Discount Calculator
# Design Discount Calculator Class
# Solved
# Problem: Build a pricing system where an OrderProcessor applies discounts polymorphically. Different discount types share a common base class with shared formatting logic, but each one calculates the discounted price differently. The processor works with any discount through the abstract Discount type.

# Requirements:

# Abstract Discount class with a label field (protected), an abstract apply(price) method that returns the discounted price, and a concrete describe(originalPrice) method that prints "label: $originalPrice -> $discountedPrice".
# PercentageDiscount: takes a percentage (e.g., 20 means 20% off). Label is "20.0% off". Returns price * (1 - percentage/100).
# FlatDiscount: takes a fixed amount off. Label is "$15.0 off". Returns price - amount (minimum 0).
# BuyOneGetOneFree: halves the price. Label is "Buy 1 Get 1 Free". Returns price / 2.
# OrderProcessor class with a processOrder(itemName, price, discount) method that prints the item name and calls describe() on the discount.









from abc import ABC, abstractmethod


class Discount(ABC):
    def __init__(self, label: str):
        self._label = label

    @abstractmethod
    def apply(self, price: float) -> float:
        pass

    def describe(self, original_price: float):
        discounted_price = self.apply(original_price)
        print(f"{self._label}: ${original_price:.2f} -> ${discounted_price:.2f}")


class PercentageDiscount(Discount):
    def __init__(self, percentage: float):
        super().__init__(f"{percentage:.1f}% off")
        self._percentage = percentage

    def apply(self, price: float) -> float:
        return price * (1 - self._percentage / 100)


class FlatDiscount(Discount):
    def __init__(self, amount: float):
        super().__init__(f"${amount:.1f} off")
        self._amount = amount

    def apply(self, price: float) -> float:
        return max(price - self._amount, 0)


class BuyOneGetOneFree(Discount):
    def __init__(self):
        super().__init__("Buy 1 Get 1 Free")

    def apply(self, price: float) -> float:
        return price / 2


class OrderProcessor:
    def process_order(self, item_name: str, price: float, discount: Discount):
        print(f"Item: {item_name}")
        discount.describe(price)


if __name__ == "__main__":
    processor = OrderProcessor()

    processor.process_order("Laptop", 999.99, PercentageDiscount(20))
    processor.process_order("Headphones", 49.99, FlatDiscount(15))
    processor.process_order("Keyboard", 79.98, BuyOneGetOneFree())
    
    
    
    
    
    
    
    

# Exercise 2: Logging System
# Design Logging System Class
# Problem: Build a logging system where the application uses a Logger interface polymorphically. Different logger implementations send messages to different destinations, and the application doesn't know or care which one it's using.

# Requirements:

# Logger interface with log(level, message) and getDestination() methods.
# ConsoleLogger: prints formatted log messages to the console.
# FileLogger: simulates writing to a file (print with file path prefix).
# DatabaseLogger: simulates inserting into a database (print with table name prefix).
# Application class that takes a Logger in its constructor and uses it throughout.



from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def log(self, level: str, message: str) -> None:
        pass

    @abstractmethod
    def get_destination(self) -> str:
        pass


class ConsoleLogger(Logger):
    def log(self, level: str, message: str) -> None:
        print(f"[{level}] {message}")

    def get_destination(self) -> str:
        return "Console"


class FileLogger(Logger):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def log(self, level: str, message: str) -> None:
        print(f"Writing to {self._file_path}: [{level}] {message}")

    def get_destination(self) -> str:
        return f"File: {self._file_path}"


class DatabaseLogger(Logger):
    def __init__(self, table_name: str):
        self._table_name = table_name

    def log(self, level: str, message: str) -> None:
        print(f"INSERT INTO {self._table_name}: [{level}] {message}")

    def get_destination(self) -> str:
        return f"Database: {self._table_name}"


class Application:
    def __init__(self, logger: Logger):
        self._logger = logger

    def run(self):
        self._logger.log("INFO", "Application starting...")
        self._logger.log("INFO", "Processing data...")
        self._logger.log("INFO", "Application shutting down.")


if __name__ == "__main__":
    loggers = [
        ConsoleLogger(),
        FileLogger("/var/log/app.log"),
        DatabaseLogger("app_logs"),
    ]

    for logger in loggers:
        print(f"--- Using {logger.get_destination()} ---")
        app = Application(logger)
        app.run()
        print()
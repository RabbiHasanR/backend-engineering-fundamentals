# without dry principle



# In auth_service.py
def is_valid_email(email: str) -> bool:
    return email is not None and "@" in email and "." in email

# In payment_service.py
def is_valid_email(email: str) -> bool:
    return email is not None and "@" in email and "." in email

# In messaging_service.py
def is_valid_email(email: str) -> bool:
    return email is not None and "@" in email and "." in email



# Applying DRY

class EmailValidator:
    @staticmethod
    def is_valid(email: str) -> bool:
        return (
            email is not None
            and "@" in email
            and "." in email
            and (email.endswith(".com") or email.endswith(".org"))
        )
        
# use

# # In auth_service.py
# if EmailValidator.is_valid(user.email):
#     pass
#     # Proceed with authentication

# # In payment_service.py
# if EmailValidator.is_valid(customer.email):
#     pass
#     # Proceed with payment processing

# # In messaging_service.py
# if EmailValidator.is_valid(recipient.email):
#     pass
#     # Proceed with sending message



# The Problem
# You have three services, OrderService, ShippingService, and SupportService, that all need to send notifications to users. Each service currently duplicates two pieces of logic: formatting a message and sending it via an external notification API.

# Before: Violating DRY
# Each service contains its own copy of the message formatting and sending logic.

class OrderService:
    def notify_order_confirmation(self, user_id: str, order_id: str) -> None:
        # Duplicated: message formatting
        message = f"[Order] Hi {user_id}, your order {order_id} has been confirmed."
        formatted = message[0].upper() + message[1:]

        # Duplicated: sending logic
        print("Connecting to notification API...")
        print(f"Sending to {user_id}: {formatted}")
        print("Notification sent successfully.")

class ShippingService:
    def notify_shipment_update(self, user_id: str, tracking_id: str) -> None:
        # Duplicated: message formatting
        message = f"[Shipping] Hi {user_id}, your shipment {tracking_id} is on its way."
        formatted = message[0].upper() + message[1:]

        # Duplicated: sending logic
        print("Connecting to notification API...")
        print(f"Sending to {user_id}: {formatted}")
        print("Notification sent successfully.")

class SupportService:
    def notify_ticket_resolution(self, user_id: str, ticket_id: str) -> None:
        # Duplicated: message formatting
        message = f"[Support] Hi {user_id}, your ticket {ticket_id} has been resolved."
        formatted = message[0].upper() + message[1:]

        # Duplicated: sending logic
        print("Connecting to notification API...")
        print(f"Sending to {user_id}: {formatted}")
        print("Notification sent successfully.")
        

# After: DRY Applied
# We extract the duplicated behavior into two focused classes: MessageFormatter handles message formatting, and NotificationSender handles the sending logic.

class MessageFormatter:
    @staticmethod
    def format(category: str, user_id: str, detail: str) -> str:
        message = f"[{category}] Hi {user_id}, {detail}"
        return message[0].upper() + message[1:]

class NotificationSender:
    @staticmethod
    def send(user_id: str, message: str) -> None:
        print("Connecting to notification API...")
        print(f"Sending to {user_id}: {message}")
        print("Notification sent successfully.")

class OrderService:
    def notify_order_confirmation(self, user_id: str, order_id: str) -> None:
        message = MessageFormatter.format(
            "Order", user_id, f"your order {order_id} has been confirmed.")
        NotificationSender.send(user_id, message)

class ShippingService:
    def notify_shipment_update(self, user_id: str, tracking_id: str) -> None:
        message = MessageFormatter.format(
            "Shipping", user_id, f"your shipment {tracking_id} is on its way.")
        NotificationSender.send(user_id, message)

class SupportService:
    def notify_ticket_resolution(self, user_id: str, ticket_id: str) -> None:
        message = MessageFormatter.format(
            "Support", user_id, f"your ticket {ticket_id} has been resolved.")
        NotificationSender.send(user_id, message)
        
        

# Exercise 1: TaxCalculator
# Refactor TaxCalculator
# Solved
# Problem: You have three region-specific order processors (USOrderProcessor, EUOrderProcessor, UKOrderProcessor) that each duplicate the same tax calculation logic. Your task is to extract a TaxCalculator interface with region-specific implementations, then refactor the order processors to use it.

# Requirements:

# Create a TaxCalculator interface with a calculateTax(amount) method
# Implement USTaxCalculator (10% tax), EUTaxCalculator (20% tax), and UKTaxCalculator (15% tax)
# Refactor the order processors to accept a TaxCalculator instead of duplicating tax logic
# Each order processor should print the subtotal, tax amount, and total



from abc import ABC, abstractmethod

class TaxCalculator(ABC):

    @abstractmethod
    def calculate_tax(self, amount: float) -> float:
        pass
    
    @abstractmethod
    def get_region(self) -> str:
        pass

# Before: Each processor duplicates tax calculation
class USTaxCalculator(TaxCalculator):
    def calculate_tax(self, amount: float) -> float:
        return amount * 0.10

    def get_region(self) -> str:
        return "US"
    

class EUTaxCalculator(TaxCalculator):
    def calculate_tax(self, amount: float) -> float:
        return amount * 0.20

    def get_region(self) -> str:
        return "EU"

class UKTaxCalculator(TaxCalculator):
    def calculate_tax(self, amount: float) -> float:
        return amount * 0.15

    def get_region(self) -> str:
        return "UK"

class OrderProcessor:
    def __init__(self, tax_calculator: TaxCalculator):
        self.tax_calculator = tax_calculator

    def process_order(self, amount: float) -> None:
        tax = self.tax_calculator.calculate_tax(amount)
        total = amount + tax
        print(f"{self.tax_calculator.get_region()} Order - "
              f"Subtotal: ${amount:.2f}, Tax: ${tax:.2f}, Total: ${total:.2f}")

if __name__ == "__main__":
    # After refactoring, usage should look like:
    us_processor = OrderProcessor(USTaxCalculator())
    us_processor.process_order(100.0)
    

    eu_processor = OrderProcessor(EUTaxCalculator())
    eu_processor.process_order(100.0)

    uk_processor = OrderProcessor(UKTaxCalculator())
    uk_processor.process_order(100.0)
    
    

# Exercise 2: ConfigLoader
# Refactor ConfigLoader
# Problem: Your application loads configuration from three sources: a config file, environment variables, and default values. Each source currently has its own parsing and validation pipeline, but the pipeline logic (read, parse, validate, return) is identical. Your task is to eliminate this duplication.

# Requirements:

# Create a ConfigSource interface with a loadValue(key) method
# Implement FileConfigSource, EnvConfigSource, and DefaultConfigSource
# Create a ConfigLoader that tries each source in priority order (file first, then env, then defaults) and returns the first non-null value
# Add validation: config values must be non-empty strings


import os
from abc import ABC, abstractmethod

class ConfigSource(ABC):

    @abstractmethod
    def load_value(self, key: str) -> str:
        pass

class FileConfigSource(ConfigSource):
    def __init__(self, config: dict):
        self.config = config

    def load_value(self, key: str):
        return self.config.get(key)

class EnvConfigSource(ConfigSource):

    def load_value(self, key: str):
        return os.environ.get(key.replace(".", "_").upper())

class DefaultConfigSource(ConfigSource):
    def __init__(self, config: dict):
        self.config = config

    def load_value(self, key: str):
        return self.config.get(key)


class ConfigLoader:
    def __init__(self, sources: list):
        self.sources = sources

    def get(self, key: str):
        for source in self.sources:
            value = source.load_value(key)
            if value is not None and value != "":
                return value
        return None
    


if __name__ == "__main__":
    file_config = {"db.host": "localhost", "db.port": "5432"}
    defaults = {"db.host": "127.0.0.1", "db.port": "3306", "db.timeout": "30"}

    loader = ConfigLoader([
        FileConfigSource(file_config),
        EnvConfigSource(),
        DefaultConfigSource(defaults),
    ])

    print(f"db.host = {loader.get('db.host')}")
    print(f"db.port = {loader.get('db.port')}")
    print(f"db.timeout = {loader.get('db.timeout')}")
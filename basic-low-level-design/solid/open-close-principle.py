# Exercise 1: ShippingCostCalculator
# Refactor ShippingCostCalculator Class
# Solved
# Problem: A ShippingCostCalculator uses if-else to determine the shipping cost based on the shipping type (Standard, Express, Overnight, International). Every time a new shipping type is added, someone has to modify the calculator. Refactor this so that new shipping types can be added without modifying the calculator.

# Requirements:

# Define a ShippingStrategy interface with a calculateCost(weight) method
# Create concrete implementations: StandardShipping, ExpressShipping, OvernightShipping, InternationalShipping
# Refactor ShippingCostCalculator to accept a ShippingStrategy instead of a string
# The calculator should delegate cost computation to the strategy


from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def calculate_cost(self, weight: float) -> float:
        pass

class StandardShipping(ShippingStrategy):

    def calculate_cost(self, weight: float) -> float:
        return weight * 1.5

class ExpressShipping(ShippingStrategy):

    def calculate_cost(self, weight: float) -> float:
        return weight * 3.0

class OvernightShipping(ShippingStrategy):

    def calculate_cost(self, weight: float) -> float:
        return weight * 5.0

class InternationalShipping(ShippingStrategy):

    def calculate_cost(self, weight: float) -> float:
        return weight * 10.0

class ShippingCostCalculator:
    def __init__(self, strategy: ShippingStrategy):
        self.strategy = strategy

    def calculate(self, weight: float) -> float:
        return self.strategy.calculate_cost(weight)

if __name__ == "__main__":
    weight = 2.0

    standard = ShippingCostCalculator(StandardShipping())
    express = ShippingCostCalculator(ExpressShipping())
    overnight = ShippingCostCalculator(OvernightShipping())
    international = ShippingCostCalculator(InternationalShipping())

    print(f"Standard: ${standard.calculate(weight)}")
    print(f"Express: ${express.calculate(weight)}")
    print(f"Overnight: ${overnight.calculate(weight)}")
    print(f"International: ${international.calculate(weight)}")
    
    
    
    

# Exercise 2: NotificationService
# Refactor NotificationService Class
# Solved
# Problem: A NotificationService has hardcoded notification channels (Email and SMS). Every time the business wants to add a new channel (Push, Slack, WhatsApp), the service must be modified. Refactor it to make it extensible so that new channels can be added without modifying existing code.

# Requirements:

# Define a NotificationChannel interface with a send(message) method
# Create concrete implementations: EmailChannel, SMSChannel, PushChannel, SlackChannel
# Refactor NotificationService to accept one or more NotificationChannel instances
# The service should delegate sending to the channel without knowing its type


from abc import ABC, abstractmethod

# NotificationChannel interface
class NotificationChannel(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

# Concrete channels
class EmailChannel(NotificationChannel):
    def send(self, message: str) -> None:
        print(f"Sending EMAIL: {message}")

class SMSChannel(NotificationChannel):
    def send(self, message: str) -> None:
        print(f"Sending SMS: {message}")

class PushChannel(NotificationChannel):
    def send(self, message: str) -> None:
        print(f"Sending PUSH: {message}")

class SlackChannel(NotificationChannel):
    def send(self, message: str) -> None:
        print(f"Sending SLACK: {message}")

# Refactored service - no if-else
class NotificationService:
    def __init__(self, channels: list[NotificationChannel]):
        self.channels = channels

    def send_notification(self, message: str) -> None:
        for channel in self.channels:
            channel.send(message)

# Main
if __name__ == "__main__":
    channels = [
        EmailChannel(),
        SMSChannel(),
        PushChannel(),
        SlackChannel(),
    ]

    service = NotificationService(channels)
    service.send_notification("Your order has shipped!")

# Let’s say you’re designing a payment processing module that supports multiple providers like Stripe, Razorpay, and PayPal.

# You don’t want your business logic to depend on a specific provider. You just want a common way to initiate a payment.


from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def initiate_payment(self, amount):
        pass
    


class StripePayment(PaymentGateway):
    def initiate_payment(self, amount):
        print(f"Processing payment via Stripe: ${amount}")
        
class RazorpayPayment(PaymentGateway):
    def initiate_payment(self, amount):
        print(f"Processing payment via Razorpay: ₹{amount}")
        
        
class CheckoutService:
    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway
    
    def set_payment_gateway(self, payment_gateway):
        self.payment_gateway = payment_gateway
    
    def checkout(self, amount):
        self.payment_gateway.initiate_payment(amount)
        
        

if __name__ == "__main__":
    stripe_gateway = StripePayment()
    checkout_service = CheckoutService(stripe_gateway)
    checkout_service.checkout(120.50)  # Output: Processing payment via Stripe: $120.5
    
    # Switch to Razorpay
    razorpay_gateway = RazorpayPayment()
    checkout_service.set_payment_gateway(razorpay_gateway)
    checkout_service.checkout(150.50)  # Output: Processing payment via Razorpay: ₹150.5
    
    
    

# 4. Practical Example: Notification Service
# Let's apply interfaces to a different domain. Imagine you're building an alerting system for a DevOps platform. When something goes wrong (server down, high CPU, disk full), the system needs to send notifications. Some teams prefer email, others use Slack, and some have custom webhook integrations.

# The alerting service shouldn't know or care which channel is being used. It just sends the notification through whatever channel was configured.


class NotificationService(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        pass


class EmailNotifier(NotificationService):
    def send(self, recipient: str, message: str) -> None:
        print(f"[Email] To: {recipient} | {message}")

class SlackNotifier(NotificationService):
    def send(self, recipient: str, message: str) -> None:
        print(f"[Slack] Channel: {recipient} | {message}")

class WebhookNotifier(NotificationService):
    def send(self, recipient: str, message: str) -> None:
        print(f"[Webhook] URL: {recipient} | {message}")
        
        

class AlertService:
    def __init__(self, notifier: NotificationService):
        self._notifier = notifier
        
    def trigger_alert(self, recipient: str, issue: str) -> None:
        alert_message = f"ALERT: {issue}"
        self._notifier.send(recipient, alert_message)

if __name__ == "__main__":
    email_alerts = AlertService(EmailNotifier())
    email_alerts.trigger_alert("ops@company.com", "CPU usage at 95%")

    slack_alerts = AlertService(SlackNotifier())
    slack_alerts.trigger_alert("#incidents", "Database connection pool exhausted")

    webhook_alerts = AlertService(WebhookNotifier())
    webhook_alerts.trigger_alert("https://hooks.example.com/alerts", "Disk usage at 90%")
    
    
    


# Exercise 1: Log Formatter
# Design Log Formatter Class
# Problem: Build a logging system where the format of log messages is configurable. A Logger class writes log messages, but the format (plain text vs. JSON) is determined by an injected Formatter interface.

# Requirements:

# Formatter interface with a format(message) method that takes a string and returns a formatted string
# PlainFormatter: returns the message as-is (e.g., "Server started on port 8080")
# JsonFormatter: returns the message wrapped in JSON (e.g., {"log": "Server started on port 8080"})
# Logger class takes a Formatter in its constructor and has a log(message) method that formats the message, then prints it



class Formatter(ABC):
    @abstractmethod
    def format(self, message: str) -> str:
        pass

class PlainFormatter(Formatter):
    def format(self, message: str) -> str:
        # Return the message as-is
        return message

class JsonFormatter(Formatter):
    def format(self, message: str) -> str:
        # Return the message wrapped in JSON: {"log": "message"}
        return '{"log": "' + message + '"}'

class Logger:
    def __init__(self, formatter: Formatter):
        self._formatter = formatter

    def log(self, message: str) -> None:
        print(self._formatter.format(message))


if __name__ == "__main__":
    plain_logger = Logger(PlainFormatter())
    plain_logger.log("Server started on port 8080")

    json_logger = Logger(JsonFormatter())
    json_logger.log("Server started on port 8080")
    
    
    
    
# Exercise 2: Input Validator
# Design Input Validator Class
# Solved
# Problem: Build a registration system where multiple validation rules are applied to user input. Each rule is a separate implementation of a Validator interface, and the RegistrationService runs all validators before accepting the registration.

# Requirements:

# Validator interface with a validate(input) method that returns true if valid, false otherwise
# EmailValidator: returns true if the input contains @
# PasswordValidator: returns true if the input has 8 or more characters
# RegistrationService: takes a list of validators in its constructor. Its register(input) method runs all validators and prints whether the input passed or failed    





class Validator(ABC):
    @abstractmethod
    def validate(self, input: str) -> bool:
        pass

class EmailValidator(Validator):
    def validate(self, input: str) -> bool:
        # Return True if "@" in input
        return "@" in input

class PasswordValidator(Validator):
    def validate(self, input: str) -> bool:
        # Return True if len(input) >= 8
        return len(input) >= 8

class RegistrationService:
    def __init__(self, validators: list[Validator]):
        self._validators = validators

    def register(self, input: str) -> None:
        # Run all validators on input. If all pass, print "input" - PASSED
        # If any fail, print "input" - FAILED
        for validator in self._validators:
            status = "PASSED" if validator.validate(input) else "FAILED"
            print(f'"{input}" - {status}')


if __name__ == "__main__":
    email_reg = RegistrationService([EmailValidator()])
    email_reg.register("user@example.com")  # Should pass
    email_reg.register("invalid-email")      # Should fail

    pass_reg = RegistrationService([PasswordValidator()])
    pass_reg.register("strongpassword")  # Should pass
    pass_reg.register("short")            # Should fail
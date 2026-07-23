# Let's model a simple Printer that depends on a Document to print. 
# The Printer receives the document as a method parameter, uses it, and doesn't store it.


class Document:
    def __init__(self, content):
        self.content = content
        
    def get_content(self):
        return self.content
		
class Printer:
    def print(self, document):
        print("Printing:", document.get_content())
		
if __name__ == "__main__":
    doc = Document("Hello, World!")
    printer = Printer()

    printer.print(doc)

    # After print() returns, the printer has no reference to the document.
    # The document can be garbage collected independently of the printer.		
    
    
    

# Consider a NotificationService that sends email notifications. A straightforward implementation might create its own EmailSender internally:
# without dependency injection

class NotificationService:
    def __init__(self):
        self.sender = EmailSender()  # Creates its own dependency

    def notify_user(self, message):
        self.sender.send(message)
        
# This looks reasonable, but it has several problems:

# Can't switch implementations. Want to send SMS instead of email? You have to modify the NotificationService class itself.
# Can't test in isolation. Unit tests will actually send real emails (or fail trying) because there's no way to substitute a mock.
# Violates the Open/Closed Principle. Adding a new notification channel requires changing existing code rather than extending it.


# The Solution: Inject from Outside
# Instead of letting the class create its own dependencies, you provide them from outside. 
# This is Dependency Injection: a design technique where a class receives the objects it depends on rather than creating them itself.


from abc import ABC, abstractmethod

class Sender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

class EmailSender(Sender):
    def send(self, message: str) -> None:
        print(f"Email: {message}")

class SmsSender(Sender):
    def send(self, message: str) -> None:
        print(f"SMS: {message}")

class NotificationService:
    def __init__(self, sender: Sender):
        self.sender = sender  # Injected from outside

    def notify_user(self, message: str) -> None:
        self.sender.send(message)
        
        

# Practical Example: Event Ticketing System
# Let's put dependency into practice with a realistic scenario. A TicketBookingService handles the complete flow of booking an event ticket. During the bookTicket() method, it needs to validate that seats are available, process a payment, generate a QR code for the ticket, and send a confirmation email. Each of these responsibilities belongs to a separate class, and the booking service depends on all four of them, but only during the booking method.


class SeatValidator:
    def is_available(self, event_id, seat_number):
        print(f"Checking seat {seat_number} for event {event_id}")
        return True  # Simulated: seat is available

class PaymentProcessor:
    def charge(self, email, amount):
        print(f"Charging ${amount} to {email}")
        return True  # Simulated: payment succeeds

class QRCodeGenerator:
    def generate(self, event_id, seat_number):
        qr_code = f"QR-{event_id}-{seat_number}"
        print(f"Generated QR code: {qr_code}")
        return qr_code

class EmailService:
    def send_confirmation(self, email, qr_code):
        print(f"Sending confirmation to {email} with code {qr_code}")

class TicketBookingService:
    def book_ticket(self, event_id, seat_number, email, amount,
                    validator, payment, qr_generator, email_service):
        if not validator.is_available(event_id, seat_number):
            print("Seat not available.")
            return False

        if not payment.charge(email, amount):
            print("Payment failed.")
            return False

        qr_code = qr_generator.generate(event_id, seat_number)
        email_service.send_confirmation(email, qr_code)

        print("Booking confirmed!")
        return True
		
if __name__ == "__main__":
    booking_service = TicketBookingService()

    # All dependencies are created externally and passed in
    validator = SeatValidator()
    payment = PaymentProcessor()
    qr_generator = QRCodeGenerator()
    email_service = EmailService()

    booking_service.book_ticket("CONF-2025", "A12", "alice@example.com",
        99.99, validator, payment, qr_generator, email_service)		



# Exercise 1: File Conversion Service
# Design File Conversion Service
# Solved
# Problem: Build a FileConverter that converts files from one format to another. During the convert() method, it depends on a FileReader to read the source file, a FormatParser to parse the content, and a FileWriter to write the output. None of these are stored as fields.

# Requirements:

# FileReader with a read(filePath) method that returns the file content as a string.
# FormatParser with a parse(content, targetFormat) method that returns the converted content.
# FileWriter with a write(filePath, content) method that writes the content to a file.
# FileConverter with a convert(sourcePath, targetPath, targetFormat, reader, parser, writer) method that coordinates the three dependencies. No fields.


class FileReader:
    def read(self, file_path):
        print(f"Reading file: {file_path}")
        content = "name,age,city"
        print(f"Content: {content}")
        return content

class FormatParser:
    def parse(self, content, target_format):
        print(f"Parsing content to {target_format} format")
        parsed = '[{"name":"Alice","age":30,"city":"NYC"}]'
        print(f"Parsed: {parsed}")
        return parsed

class FileWriter:
    def write(self, file_path, content):
        print(f"Writing to file: {file_path}")

class FileConverter:
    def convert(self, source_path, target_path, target_format,
                reader, parser, writer):
        content = reader.read(source_path)
        parsed = parser.parse(content, target_format)
        writer.write(target_path, parsed)
        print(f"File conversion complete: {source_path} -> {target_path}")

if __name__ == "__main__":
    converter = FileConverter()

    reader = FileReader()
    parser = FormatParser()
    writer = FileWriter()

    converter.convert("data.csv", "output.json", "JSON", reader, parser, writer)
    
    
    
# Exercise 2: Order Processing Pipeline
# Design Order Processing Pipeline
# Solved
# Problem: Build an OrderProcessor that processes customer orders. During processOrder(), it depends on an InventoryChecker to verify stock, a PriceCalculator to compute the total, and an InvoiceGenerator to create the invoice. All dependencies come in as method parameters.

# Requirements:

# InventoryChecker with a checkStock(itemName, quantity) method that returns true if stock is available.
# PriceCalculator with a calculate(itemName, quantity) method that returns the total price.
# InvoiceGenerator with a generate(itemName, quantity, total) method that returns an invoice string.
# OrderProcessor with a processOrder(itemName, quantity, checker, calculator, generator) method that coordinates the pipeline. No fields.




class InventoryChecker:
    def check_stock(self, item_name, quantity):
        print(f"Checking stock for {item_name} (x{quantity})")
        print("Stock available: true")
        return True

class PriceCalculator:
    def calculate(self, item_name, quantity):
        unit_price = 1249.99
        total = unit_price * quantity
        print(f"Calculating price: {item_name} x {quantity} = ${total:.2f}")
        return total

class InvoiceGenerator:
    def generate(self, item_name, quantity, total):
        print("Generating invoice...")
        return f"--- INVOICE ---\nItem: {item_name}\nQuantity: {quantity}\nTotal: ${total:.2f}\n--- END ---"

class OrderProcessor:
    def process_order(self, item_name, quantity, checker, calculator, generator):
        in_stock = checker.check_stock(item_name, quantity)
        if not in_stock:
            return f"Order rejected: {item_name} is out of stock."
        total = calculator.calculate(item_name, quantity)
        return generator.generate(item_name, quantity, total)

if __name__ == "__main__":
    processor = OrderProcessor()

    checker = InventoryChecker()
    calculator = PriceCalculator()
    generator = InvoiceGenerator()

    invoice = processor.process_order("Laptop", 2, checker, calculator, generator)
    print(invoice)
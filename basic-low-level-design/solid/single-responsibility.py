# Exercise 1: OrderService God Class
# Refactor OrderService God Class
# Problem: You have an OrderService class that handles order processing, inventory management, and sending notifications. This class has three distinct responsibilities tangled together. Your task is to refactor it into three focused classes: OrderProcessor, InventoryManager, and NotificationService.

# Requirements:

# OrderProcessor should handle order validation and total calculation
# InventoryManager should handle stock checks and stock updates
# NotificationService should handle sending order confirmation messages
# Each class should accept dependencies through its constructor (or method parameters) rather than doing everything internally



# Before: One class doing three unrelated jobs
class OrderService:
    def __init__(self):
        self.inventory = {"LAPTOP": 10, "PHONE": 25, "TABLET": 15}
        self.orders = []

    def place_order(self, product_id: str, quantity: int, customer_email: str):
        # Responsibility 1: Inventory check
        stock = self.inventory.get(product_id, 0)
        if stock < quantity:
            print(f"Insufficient stock for {product_id}")
            return

        # Responsibility 2: Order processing
        price_per_unit = 100.0
        total = price_per_unit * quantity
        order_id = f"ORD-{len(self.orders) + 1}"
        self.orders.append(order_id)

        # Responsibility 3: Update inventory
        self.inventory[product_id] = stock - quantity

        # Responsibility 4: Send notification
        print(f"Email to {customer_email}: Order {order_id} confirmed. Total: ${total}")

# TODO: Refactor into OrderProcessor, InventoryManager, and NotificationService.

if __name__ == "__main__":
    # After refactoring, usage should look like:
    # inventory = InventoryManager()
    # notifications = NotificationService()
    # processor = OrderProcessor(inventory, notifications)
    # processor.place_order("LAPTOP", 2, "alice@example.com")
    pass



class InventoryManager:
    def __init__(self):
        self.stock = {"LAPTOP": 10, "PHONE": 25, "TABLET": 15}

    def check_stock(self, product_id, quantity):
        return self.stock.get(product_id, 0) >= quantity

    def reduce_stock(self, product_id, quantity):
        self.stock[product_id] -= quantity


class NotificationService:
    def send_order_confirmation(self, customer_email, order_id, total):
        print(f"Email to {customer_email}: Order {order_id} confirmed. Total: ${total}")


class OrderProcessor:
    def __init__(self, inventory_manager, notification_service):
        self.inventory_manager = inventory_manager
        self.notification_service = notification_service
        self.order_counter = 0

    def place_order(self, product_id, quantity, customer_email):
        if not self.inventory_manager.check_stock(product_id, quantity):
            print(f"Insufficient stock for {product_id}")
            return
        self.inventory_manager.reduce_stock(product_id, quantity)
        total = quantity * 100.0
        self.order_counter += 1
        order_id = f"ORD-{self.order_counter}"
        self.notification_service.send_order_confirmation(
            customer_email, order_id, total
        )


if __name__ == "__main__":
    inventory = InventoryManager()
    notifications = NotificationService()
    processor = OrderProcessor(inventory, notifications)
    processor.place_order("LAPTOP", 2, "alice@example.com")
    
    
    
# Exercise 2: ReportManager
# Refactor ReportManager Class
# Problem: You have a ReportManager class that generates report data, formats it into a specific output (CSV, JSON), and distributes it via email. These are three distinct responsibilities bundled into one class. Your task is to refactor it into ReportGenerator, ReportFormatter, and ReportDistributor.

# Requirements:

# ReportGenerator should gather and return raw report data (a list of records)
# ReportFormatter should take raw data and format it as CSV text
# ReportDistributor should take a formatted report and "send" it to a recipient
# The main workflow should compose these three classes together



# Before: One class doing three unrelated jobs
class ReportManager:
    def create_and_send_report(self, recipient: str):
        # Responsibility 1: Generate report data
        data = [
            ["Name", "Sales", "Region"],
            ["Alice", "15000", "North"],
            ["Bob", "22000", "South"],
            ["Charlie", "18000", "East"],
        ]

        # Responsibility 2: Format as CSV
        csv_lines = []
        for row in data:
            csv_lines.append(",".join(row))
        csv_output = "\n".join(csv_lines)

        # Responsibility 3: Distribute via email
        print(f"Sending report to: {recipient}")
        print(csv_output)
        print("Report sent successfully.")

# TODO: Refactor into ReportGenerator, ReportFormatter, and ReportDistributor.

if __name__ == "__main__":
    # After refactoring, usage should look like:
    # generator = ReportGenerator()
    # formatter = ReportFormatter()
    # distributor = ReportDistributor()
    # data = generator.generate()
    # formatted = formatter.format_as_csv(data)
    # distributor.distribute("manager@company.com", formatted)
    pass



class ReportGenerator:
    def generate(self):
        return [
            ["Name", "Sales", "Region"],
            ["Alice", "15000", "North"],
            ["Bob", "22000", "South"],
            ["Charlie", "18000", "East"],
        ]


class ReportFormatter:
    def format_as_csv(self, data):
        return "\n".join(",".join(row) for row in data)


class ReportDistributor:
    def distribute(self, recipient, formatted_report):
        print(f"Sending report to: {recipient}")
        print(formatted_report)
        print("Report sent successfully.")


if __name__ == "__main__":
    generator = ReportGenerator()
    formatter = ReportFormatter()
    distributor = ReportDistributor()

    data = generator.generate()
    csv = formatter.format_as_csv(data)
    
    distributor.distribute("manager@company.com", csv)

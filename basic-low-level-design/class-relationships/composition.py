# Let's model the ordering scenario. An Order composes multiple LineItem objects. 
# The order creates line items internally when items are added, and destroys them when the order is destroyed.


class LineItem:
    def __init__(self, product_name: str, quantity: int, unit_price: float):
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
        
    def get_subtotal(self) -> float:
        return self.quantity * self.unit_price
    
    def describe(self):
        print(f"{self.product_name} x{self.quantity} "
              f"@ ${self.unit_price:.2f} = ${self.get_subtotal():.2f}")
        


class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self.line_items = []
        
    def add_item(self, product, quantity, unit_price):
        self.line_items.append(LineItem(product, quantity, unit_price))

    def remove_item(self, product):
        self.line_items = [
            item for item in self.line_items
            if item.product_name != product
        ]

    def get_total(self):
        return sum(item.get_subtotal() for item in self.line_items)

    def print_receipt(self):
        print(f"Order: {self.order_id}")
        for item in self.line_items:
            item.describe()
        print(f"Total: ${self.get_total():.2f}")

if __name__ == "__main__":
    order = Order("ORD-1001")
    order.add_item("Wireless Mouse", 2, 29.99)
    order.add_item("USB-C Cable", 3, 9.99)
    order.add_item("Laptop Stand", 1, 49.99)

    order.print_receipt()






# Exercise 1: Computer System
# Design Computer System Class
# Solved
# Problem: Build a Computer that composes a CPU, RAM, and HardDrive. The computer creates these parts internally based on specs passed to its constructor. No component exists outside of a computer, and destroying the computer destroys all its components.

# Requirements:

# CPU with a model name and core count. A describe() method that prints the specs.
# RAM with a size in GB. A describe() method that prints the capacity.
# HardDrive with a capacity in GB. A describe() method that prints the capacity.
# Computer that takes spec parameters in its constructor and creates all three components internally. A describeSpecs() method that prints all component details.



class CPU:
    def __init__(self, model, cores):
        self.model = model
        self.cores = cores

    def describe(self):
        # TODO: Print CPU model and core count
        print(f"  CPU: {self.model} ({self.cores} cores)")

class RAM:
    def __init__(self, size_gb):
        self.size_gb = size_gb

    def describe(self):
        # TODO: Print RAM size
        print(f"  RAM: {self.size_gb} GB")

class HardDrive:
    def __init__(self, capacity_gb):
        self.capacity_gb = capacity_gb

    def describe(self):
        # TODO: Print hard drive capacity
        print(f"  Storage: {self.capacity_gb} GB")

class Computer:
    def __init__(self, name, cpu_model, cpu_cores, ram_gb, storage_gb):
        self.name = name
        # TODO: Create CPU, RAM, and HardDrive internally
        self.cpu = CPU(cpu_model, cpu_cores)
        self.ram = RAM(ram_gb)
        self.hard_drive = HardDrive(storage_gb)

    def describe_specs(self):
        # TODO: Print computer name and describe all components
        print(f"Computer: {self.name}")
        self.cpu.describe()
        self.ram.describe()
        self.hard_drive.describe()

    def upgrade_ram(self, new_size_gb):
        # TODO (Challenge): Replace RAM with a higher-capacity one
        self.ram = RAM(new_size_gb)

if __name__ == "__main__":
    pc = Computer("Dev Workstation", "Intel i7-13700K", 16, 32, 1000)

    pc.describe_specs()

    # Challenge: upgrade RAM and verify
    pc.upgrade_ram(64)
    print("\nAfter RAM upgrade:")
    pc.describe_specs()

    # When pc is destroyed, all components are destroyed with it.
    
    

# Exercise 2: Chat Conversation System
# Design Chat Conversation System
# Solved
# Problem: A Conversation composes Message objects. Messages are created when sendMessage(sender, text) is called. Deleting a conversation deletes all its messages. Messages belong to exactly one conversation and have no meaning outside of it.

# Requirements:

# Message with a sender name, text, and a timestamp. A display() method that prints the message.
# Conversation with a title and a list of Message objects. A sendMessage(sender, text) method that creates a Message internally. A printHistory() method that prints all messages. A delete() method that clears all messages.






import time

class Message:
    def __init__(self, sender, text):
        self.sender = sender
        self.text = text
        self.timestamp = time.time()

    def display(self):
        # TODO: Print message in format "[sender]: text"
        print(f"[{self.sender}]: {self.text}")

class Conversation:
    def __init__(self, title):
        self.title = title
        self.messages = []

    def send_message(self, sender, text):
        # TODO: Create a Message internally and add it to the list
        self.messages.append(Message(sender, text))

    def print_history(self):
        # TODO: Print conversation title and all messages
        print(f"--- {self.title} ---")
        for message in self.messages:
            message.display()

    def delete(self):
        # TODO: Clear all messages (they are destroyed with the conversation)
        self.messages.clear()

    def get_message_count(self):
        return len(self.messages)

    def forward_message(self, target, message_index):
        # TODO (Challenge): Copy message content into a NEW Message
        # in the target conversation. Don't move the original.
        if 0 <= message_index < len(self.messages):
            original = self.messages[message_index]
            target.send_message(original.sender, original.text)

if __name__ == "__main__":
    team_chat = Conversation("Team Discussion")
    project_chat = Conversation("Project Alpha")

    team_chat.send_message("Alice", "Hey team, standup in 5 minutes")
    team_chat.send_message("Bob", "Got it, joining now")
    team_chat.send_message("Alice", "Don't forget to update your tasks")

    project_chat.send_message("Charlie", "Deployment is scheduled for Friday")

    print("Before deletion:")
    team_chat.print_history()
    print(f"Project chat has {project_chat.get_message_count()} messages\n")

    # Challenge: forward a message
    team_chat.forward_message(project_chat, 2)
    print("After forwarding:")
    project_chat.print_history()

    # Delete team chat - all its messages are destroyed
    team_chat.delete()
    print("\nAfter deleting team chat:")
    print(f"Team chat has {team_chat.get_message_count()} messages")
    print(f"Project chat still has {project_chat.get_message_count()} messages")
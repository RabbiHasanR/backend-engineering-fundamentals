# Exercise 1: Fat MultiFunctionDevice
# Refactor MultiFunctionDevice
# Problem: You have a MultiFunctionDevice interface with print(), scan(), fax(), and staple() methods. A BasicPrinter only prints. Refactor into separate Printable, Scannable, and Faxable interfaces so that BasicPrinter only implements the capabilities it actually supports.

# Requirements:

# Create four focused interfaces: Printable, Scannable, Faxable, and Stapleable
# BasicPrinter implements only Printable
# OfficePrinter implements Printable, Scannable, and Faxable
# FullDevice implements all four interfaces
# No class should have empty methods or throw UnsupportedOperationException

# before ISP


from abc import ABC, abstractmethod

# Before: Fat interface forces BasicPrinter to implement everything
class MultiFunctionDevice(ABC):
    @abstractmethod
    def print_doc(self, document):
        pass

    @abstractmethod
    def scan(self, document):
        pass

    @abstractmethod
    def fax(self, document, number):
        pass

    @abstractmethod
    def staple(self, document):
        pass

class BasicPrinter(MultiFunctionDevice):
    def print_doc(self, document):
        print(f"Printing: {document}")

    def scan(self, document):
        raise NotImplementedError("BasicPrinter cannot scan.")

    def fax(self, document, number):
        raise NotImplementedError("BasicPrinter cannot fax.")

    def staple(self, document):
        raise NotImplementedError("BasicPrinter cannot staple.")

if __name__ == "__main__":
    printer = BasicPrinter()
    printer.print_doc("report.pdf")

# TODO: Create Printable, Scannable, Faxable, and Stapleable interfaces.
# TODO: Refactor BasicPrinter to implement only Printable.
# TODO: Create an OfficePrinter that implements Printable, Scannable, and Faxable.
# TODO: Create a FullDevice that implements all four interfaces.




# after ISP

from abc import ABC, abstractmethod

# Segregated interfaces - each with a single capability
class Printable(ABC):
    @abstractmethod
    def print_doc(self, document):
        pass

class Scannable(ABC):
    @abstractmethod
    def scan(self, document):
        pass

class Faxable(ABC):
    @abstractmethod
    def fax(self, document, number):
        pass

class Stapleable(ABC):
    @abstractmethod
    def staple(self, document):
        pass

# BasicPrinter only implements Printable
class BasicPrinter(Printable):
    def print_doc(self, document):
        print(f"BasicPrinter -> Printing: {document}")

# OfficePrinter implements three interfaces
class OfficePrinter(Printable, Scannable, Faxable):
    def print_doc(self, document):
        print(f"OfficePrinter -> Printing: {document}")

    def scan(self, document):
        print(f"OfficePrinter -> Scanning: {document}")

    def fax(self, document, number):
        print(f"OfficePrinter -> Faxing: {document} to {number}")

# FullDevice implements all four interfaces
class FullDevice(Printable, Scannable, Faxable, Stapleable):
    def print_doc(self, document):
        print(f"FullDevice -> Printing: {document}")

    def scan(self, document):
        print(f"FullDevice -> Scanning: {document}")

    def fax(self, document, number):
        print(f"FullDevice -> Faxing: {document} to {number}")

    def staple(self, document):
        print(f"FullDevice -> Stapling: {document}")

if __name__ == "__main__":
    basic = BasicPrinter()
    basic.print_doc("report.pdf")

    office = OfficePrinter()
    office.print_doc("memo.pdf")
    office.scan("memo.pdf")
    office.fax("memo.pdf", "555-1234")

    full = FullDevice()
    full.print_doc("contract.pdf")
    full.scan("contract.pdf")
    full.fax("contract.pdf", "555-5678")
    full.staple("contract.pdf")
    
    
    

# Exercise 2: Fat UserService
# Refactor UserService
# Problem: A UserService interface bundles CRUD operations, admin operations (ban, promote), and audit operations (getLoginHistory, getActivityLog). Most implementations only need CRUD. Refactor into UserCrud, AdminControls, and AuditLog interfaces.

# Requirements:

# Create three focused interfaces: UserCrud (create, get, update, delete), AdminControls (ban, promote), and AuditLog (getLoginHistory, getActivityLog)
# BasicUserService implements only UserCrud
# AdminUserService implements UserCrud and AdminControls
# FullUserService implements all three interfaces
# No class should have empty methods or throw UnsupportedOperationException

# before ISP

from abc import ABC, abstractmethod
from typing import List

# Before: Fat interface bundles three unrelated sets of operations
class UserService(ABC):
    @abstractmethod
    def create_user(self, name: str, email: str):
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> str:
        pass

    @abstractmethod
    def update_user(self, user_id: str, new_email: str):
        pass

    @abstractmethod
    def delete_user(self, user_id: str):
        pass

    @abstractmethod
    def ban_user(self, user_id: str, reason: str):
        pass

    @abstractmethod
    def promote_user(self, user_id: str, role: str):
        pass

    @abstractmethod
    def get_login_history(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    def get_activity_log(self, user_id: str) -> List[str]:
        pass

class BasicUserService(UserService):
    def create_user(self, name, email):
        print(f"Creating user: {name} ({email})")

    def get_user(self, user_id):
        print(f"Fetching user: {user_id}")
        return f"User-{user_id}"

    def update_user(self, user_id, new_email):
        print(f"Updating user {user_id} email to {new_email}")

    def delete_user(self, user_id):
        print(f"Deleting user: {user_id}")

    def ban_user(self, user_id, reason):
        raise NotImplementedError("Not an admin service.")

    def promote_user(self, user_id, role):
        raise NotImplementedError("Not an admin service.")

    def get_login_history(self, user_id):
        raise NotImplementedError("No audit capability.")

    def get_activity_log(self, user_id):
        raise NotImplementedError("No audit capability.")

if __name__ == "__main__":
    svc = BasicUserService()
    svc.create_user("Alice", "alice@example.com")
    svc.get_user("u123")

# TODO: Create UserCrud, AdminControls, and AuditLog interfaces.
# TODO: Refactor BasicUserService to implement only UserCrud.
# TODO: Create an AdminUserService that implements UserCrud and AdminControls.
# TODO: Create a FullUserService that implements all three interfaces.



# after ISP


from abc import ABC, abstractmethod
from typing import List

# Segregated interfaces
class UserCrud(ABC):
    @abstractmethod
    def create_user(self, name: str, email: str):
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> str:
        pass

    @abstractmethod
    def update_user(self, user_id: str, new_email: str):
        pass

    @abstractmethod
    def delete_user(self, user_id: str):
        pass

class AdminControls(ABC):
    @abstractmethod
    def ban_user(self, user_id: str, reason: str):
        pass

    @abstractmethod
    def promote_user(self, user_id: str, role: str):
        pass

class AuditLog(ABC):
    @abstractmethod
    def get_login_history(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    def get_activity_log(self, user_id: str) -> List[str]:
        pass

# BasicUserService implements only UserCrud
class BasicUserService(UserCrud):
    def create_user(self, name, email):
        print(f"BasicUserService -> Creating user: {name} ({email})")

    def get_user(self, user_id):
        print(f"BasicUserService -> Fetching user: {user_id}")
        return f"User-{user_id}"

    def update_user(self, user_id, new_email):
        print(f"BasicUserService -> Updating user {user_id} email to {new_email}")

    def delete_user(self, user_id):
        print(f"BasicUserService -> Deleting user: {user_id}")

# AdminUserService implements UserCrud and AdminControls
class AdminUserService(UserCrud, AdminControls):
    def create_user(self, name, email):
        print(f"AdminUserService -> Creating user: {name} ({email})")

    def get_user(self, user_id):
        print(f"AdminUserService -> Fetching user: {user_id}")
        return f"User-{user_id}"

    def update_user(self, user_id, new_email):
        print(f"AdminUserService -> Updating user {user_id} email to {new_email}")

    def delete_user(self, user_id):
        print(f"AdminUserService -> Deleting user: {user_id}")

    def ban_user(self, user_id, reason):
        print(f"AdminUserService -> Banning user {user_id}: {reason}")

    def promote_user(self, user_id, role):
        print(f"AdminUserService -> Promoting user {user_id} to {role}")

# FullUserService implements all three interfaces
class FullUserService(UserCrud, AdminControls, AuditLog):
    def create_user(self, name, email):
        print(f"FullUserService -> Creating user: {name} ({email})")

    def get_user(self, user_id):
        print(f"FullUserService -> Fetching user: {user_id}")
        return f"User-{user_id}"

    def update_user(self, user_id, new_email):
        print(f"FullUserService -> Updating user {user_id} email to {new_email}")

    def delete_user(self, user_id):
        print(f"FullUserService -> Deleting user: {user_id}")

    def ban_user(self, user_id, reason):
        print(f"FullUserService -> Banning user {user_id}: {reason}")

    def promote_user(self, user_id, role):
        print(f"FullUserService -> Promoting user {user_id} to {role}")

    def get_login_history(self, user_id):
        history = ["2024-01-01", "2024-01-05"]
        print(f"FullUserService -> Login history for {user_id}: [{', '.join(history)}]")
        return history

    def get_activity_log(self, user_id):
        log = ["created_post", "updated_profile"]
        print(f"FullUserService -> Activity log for {user_id}: [{', '.join(log)}]")
        return log

if __name__ == "__main__":
    basic = BasicUserService()
    basic.create_user("Alice", "alice@example.com")
    basic.get_user("u123")

    admin = AdminUserService()
    admin.create_user("Bob", "bob@example.com")
    admin.ban_user("u456", "spam")
    admin.promote_user("u456", "admin")

    full = FullUserService()
    full.create_user("Carol", "carol@example.com")
    full.ban_user("u789", "abuse")
    full.get_login_history("u789")
# Exercise 1: Bank Account
# Design Bank Account Class
# Problem: Create a BankAccount class that manages a simple bank account with deposit, withdrawal, and balance checking functionality.

# Requirements:

# Fields: accountNumber, ownerName, balance
# Constructor that initializes the account with owner name and account number (balance starts at 0)
# deposit(amount): adds money to balance (only positive amounts)
# withdraw(amount): removes money if sufficient balance exists, returns success/failure
# getBalance(): returns current balance



class BankAccount:
    def __init__(self, account_number: str, owner_name: str):
        self._account_number = account_number
        self._owner_name = owner_name
        self._balance = 0
        
    
    def deposit(self, amount: float) -> None:
        if amount < 0:
            print("Can not deposite negetive amount")
            return
        self._balance += amount
    
    def withdraw(self, amount: float) -> bool:
        if amount > self._balance:
            print("Insufficient balance")
            return False
        self._balance -= amount
        return True
    
    def get_balance(self) -> float:
        return self._balance
    
    
    
if __name__ == "__main__":
    account = BankAccount("123456", "John Doe")
    account.deposit(1000)
    print(account.get_balance())  # Should print 1000.0

    success = account.withdraw(500)
    print(str(success).lower())   # Should print true
    print(account.get_balance())  # Should print 500.0
    
    
    

# Exercise 2: Library Book

# Design Library Book Class
# Problem: Create a Book class for a library management system.

# Requirements:

# Fields: title, author, isbn, isAvailable
# Constructor that initializes all fields (book starts as available)
# borrowBook(): marks book as unavailable if currently available, returns success/failure
# returnBook(): marks book as available
# displayInfo(): prints book details including availability status


class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self._title = title
        self._author = author
        self._isbn = isbn
        self._isAvailable = True


    def borrow_book(self) -> bool:
        if self._isAvailable:
            self._isAvailable = False
            return True
        return False
    
    def return_book(self) -> None:
        self._isAvailable = True
    
    def display_info(self) -> None:
        status = "Available" if self._isAvailable else "Borrowed"
        print(f"{self._title} by {self._author} (ISBN: {self._isbn}) - {status}")
        
        


if __name__ == "__main__":
    book = Book("The Pragmatic Programmer", "David Thomas", "978-0135957059")
    book.display_info()

    success = book.borrow_book()
    print(f"Borrow successful: {str(success).lower()}")
    book.display_info()

    success = book.borrow_book()
    print(f"Borrow successful: {str(success).lower()}")

    book.return_book()
    book.display_info()
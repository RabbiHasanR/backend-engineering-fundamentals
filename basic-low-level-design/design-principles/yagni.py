# Simplify an Overengineered PasswordValidator
# Solved
# Problem: A developer built a full validation rules engine with an interface, three rule classes, 
# and a validation engine. But the actual requirement is simple: check if a password is at least 8 characters long.
# Here is the overengineered code:

from abc import ABC, abstractmethod

class ValidationRule(ABC):
    @abstractmethod
    def check(self, input_str: str) -> bool:
        pass

class MinLengthRule(ValidationRule):
    def __init__(self, min_length: int):
        self.min_length = min_length

    def check(self, input_str: str) -> bool:
        return len(input_str) >= self.min_length

class HasUpperCaseRule(ValidationRule):
    def check(self, input_str: str) -> bool:
        for c in input_str:
            if c.isupper():
                return True
        return False

class HasDigitRule(ValidationRule):
    def check(self, input_str: str) -> bool:
        for c in input_str:
            if c.isdigit():
                return True
        return False

class PasswordValidator:
    def __init__(self, rules: list):
        self.rules = rules

    def is_valid(self, password: str) -> bool:
        for rule in self.rules:
            if not rule.check(password):
                return False
        return True
    
    
# That is 1 interface, 3 rule classes, and a validation engine for a single length check. Way too much.

# Your task: Strip the code down to a single class with a single isValid method. Fill in the method body in the starter code below.

# Requirements:

# Accept a password string
# Return true if the password is at least 8 characters, false otherwise
# Handle null/empty passwords (return false)




class PasswordValidator:
    def is_valid(self, password: str) -> bool:
        # Your implementation here
        return len(password) >= 8

validator = PasswordValidator()
print(str(validator.is_valid("short")).lower())
print(str(validator.is_valid("longenough")).lower())
print(str(validator.is_valid("12345678")).lower())
print(str(validator.is_valid("")).lower())
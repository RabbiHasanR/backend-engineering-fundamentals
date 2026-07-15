Encapsulation:

keep data private; epxose controlled methods
validate input so state stays valid
getters and setters guard access
hide sensitive data inside the class
internals can change without breaking callers


Encapsulation



Encapsulation is one of the four foundational principles of object-oriented design. It is the practice of grouping data (variables) and behavior (methods) that operate on that data into a single unit (typically a class) and restricting direct access to the internal details of that class.

In simple terms:

Encapsulation = Data hiding + Controlled access


1. Why Encapsulation Matters
Encapsulation isn’t just about data protection, it’s about designing systems that are robust, secure, and easy to maintain.

Here's why that matters in practice:

1. Data Hiding
Sensitive data (like a bank balance or password) should not be exposed directly. Encapsulation keeps this data private and accessible only through controlled methods.

2. Controlled Access and Validation
It ensures that data can only be modified in controlled, predictable ways.

For example, you can prevent invalid deposits or withdrawals by validating input inside methods.

3. Improved Maintainability
Because internal details are hidden, you can change the implementation (e.g., how data is stored or validated) without affecting the code that depends on it.

4. Security and Stability
By preventing external tampering, encapsulation reduces the risk of inconsistent or invalid system states.



2. How Encapsulation is Achieved
Encapsulation is primarily implemented using two language features: access modifiers that control visibility, and getters/setters that provide controlled access to private data.

1. Access Modifiers
Access modifiers are keywords that control which parts of your code can see and interact with a class's fields and methods. The three most common are:

private: Accessible only within the same class. This is the primary tool for hiding data.
protected: Accessible within the same class and its subclasses. Useful when child classes need access to parent data.
public: Accessible from anywhere. This is what you use for the controlled interface.
The general rule is simple: make everything private by default, then selectively expose what needs to be public.


```python
class Product:
    def __init__(self, name: str, price: float):
        self.__name = name
        self.__price = price

    @property
    def name(self) -> str:
        return self.__name

    @property
    def price(self) -> float:
        return self.__price
    
    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Price cannot be negative")
        self.__price = value

if __name__ == "__main__":
    product = Product("A", 100)
    print(product.name, product.price)
    product.price = 200
    print(product.price)


```
1. What is Association?
Association represents a relationship between two classes where one object uses, communicates with, or references another.

This relationship models the idea:

“One object need to know about the existence of another object to perform its responsibilities”

If Class A must interact with Class B to fulfill its purpose, then Class A is associated with Class B.


Real-World Analogy

Think of a Student and a Teacher.

A student has-a teacher who teaches them.
A teacher teaches multiple students.



However:

A student can still exist without a teacher.
A teacher can still exist without any specific student.
This is a real-world association:

The relationship exists.
But neither party owns the other.
Their lifecycles are independent.



Key Characteristics of Association:
Association reflects a "has-a" or "uses-a" relationship.
Associated objects are loosely coupled and can exist independently of one another.
The association can be unidirectional or bidirectional, and can follow different multiplicity patterns (1-to-1, 1-to-many, etc.).



Types of Association:

In Object-Oriented Design, associations are primarily defined by two key properties:

Directionality — Who knows about whom?
Multiplicity — How many objects are connected?

Based on Direction (Directionality):

a. Unidirectional Association
In a unidirectional association, only one class is aware of or holds a reference to the other class. The referenced class has no knowledge of who is referencing it.


b. Bidirectional Association
In a bidirectional association, both classes are aware of each other. Each class holds a reference to the other, enabling two-way communication.




3.2 Based on Multiplicity
a. One-to-One Association
Each object of one class is linked to exactly one object of the other class.


b. One-to-Many Association
One object of a class is linked to multiple objects of another class. This is one of the most common patterns in software design.


c. Many-to-Many Association
Multiple objects from one class are associated with multiple objects from another class. This is common in scenarios involving memberships, enrollments, or tagging systems.
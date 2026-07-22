# Example: An Order object uses a PaymentGateway to process transactions, 
# but the PaymentGateway doesn't keep track of any orders. 
# The order knows about the gateway. The gateway doesn't know about the order.
# Undirectional Association


class PaymentGateway:
    def process_payment(self, amount: float):
        print(f"Processing payment of ${amount}")


class Order:
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
    
    def checkout(self):
        self.gateway.process_payment(100.0)
        
        


# Example: A Team has a list of Developers, and each Developer knows which Team they belong to. Either side can navigate to the other.
# Bidirectional Association

class Developer:
    def __init__(self):
        self.team = None
    
    def set_team(self, team):
        self.team = team


class Team:
    def __init__(self):
        self.developers = []
        
    def add_developer(self, dev: Developer):
        self.developers.append(dev)
        dev.set_team(self)
        
        

# Example: Each User has exactly one Profile, and each Profile belongs to one User. This is a bidirectional one-to-one relationship.
# One-to-One Association

class Profile:
    def __init__(self):
        self.user = None
    
    def set_user(self, user):
        self.user = user
        
class User:
    def __init__(self):
        self.profile = None
    
    def set_profile(self, profile: Profile):
        self.profile = profile
        profile.set_user(self)
        


# Example: Each Project can have many Issues (bug reports, feature requests), 
# but each Issue belongs to one Project. The project holds a list of issues, 
# and each issue holds a back-reference to its project.
# One-to-Many Association

class Issue:
    def __init__(self):
        self.project = None

    def set_project(self, project):
        self.project = project


class Project:
    def __init__(self):
        self.issues = []

    def add_issue(self, issue: Issue):
        self.issues.append(issue)
        issue.set_project(self)
        

# Example: A User can be a member of multiple Groups (WhatsApp groups, Slack channels), 
# and a Group can have multiple Users. Both sides hold a list of the other. The joinGroup() and addUser() methods keep both sides in sync.

class User:
    def __init__(self, name: str):
        self.name = name
        self.groups = []

    def join_group(self, group):
        if group not in self.groups:
            self.groups.append(group)
            group.add_user(self)

class Group:
    def __init__(self, name: str):
        self.name = name
        self.users = []

    def add_user(self, user: User):
        if user not in self.users:
            self.users.append(user)
            user.join_group(self)

# Usage
alice = User("Alice")
bob = User("Bob")

backend = Group("Backend")
dev_ops = Group("DevOps")

alice.join_group(backend)
alice.join_group(dev_ops)
bob.join_group(backend)

# Alice is in: Backend, DevOps
# Bob is in: Backend
# Backend has: Alice, Bob
# DevOps has: Alice






# Practical Example: Hospital Appointment System
# Let's build a system that combines multiple association types in a realistic domain. 
# A hospital manages doctors, patients, rooms, and appointments. The relationships between these entities 
# demonstrate unidirectional, bidirectional, one-to-many, and many-to-many associations working together.

# Here's how the classes connect:

# Appointment holds a reference to a Room (unidirectional, the room doesn't know about its appointments).
# Doctor has a list of Appointment objects, and each Appointment points back to its Doctor (bidirectional one-to-many).
# Patient has a list of Appointment objects, and each Appointment points back to its Patient (bidirectional one-to-many).
# Doctor and Patient are connected many-to-many through Appointment as an intermediary. A doctor sees many patients, 
# and a patient can visit many doctors, but they don't reference each other directly.



class Room:
    def __init__(self, number: str, floor: int):
        self.number = number 
        self.floor = floor 
        
        
class Appointment:
    def __init__(self, doctor, patient, room: Room, time: str):
        self.doctor = doctor
        self.patient = patient
        self.room = room
        self.time = time
        doctor.add_appointment(self)
        patient.add_appointment(self)


class Doctor:
    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization
        self.appointments = []

    def add_appointment(self, appt: Appointment):
        self.appointments.append(appt)

    def get_patients(self):
        seen = set()
        result = []
        for appt in self.appointments:
            if id(appt.patient) not in seen:
                seen.add(id(appt.patient))
                result.append(appt.patient)
        return result

class Patient:
    def __init__(self, name: str):
        self.name = name
        self.appointments = []

    def add_appointment(self, appt: Appointment):
        self.appointments.append(appt)

    def get_doctors(self):
        seen = set()
        result = []
        for appt in self.appointments:
            if id(appt.doctor) not in seen:
                seen.add(id(appt.doctor))
                result.append(appt.doctor)
        return result

# Usage
dr_smith = Doctor("Dr. Smith", "Cardiology")
dr_patel = Doctor("Dr. Patel", "Neurology")

alice = Patient("Alice")
bob = Patient("Bob")

room_101 = Room("101", 1)
room_205 = Room("205", 2)

Appointment(dr_smith, alice, room_101, "9:00 AM")
Appointment(dr_smith, bob, room_101, "10:00 AM")
Appointment(dr_patel, alice, room_205, "2:00 PM")

print(f"{dr_smith.name}'s patients:")
for p in dr_smith.get_patients():
    print(f"  - {p.name}")

print(f"{alice.name}'s doctors:")
for d in alice.get_doctors():
    print(f"  - {d.name} ({d.specialization})")

print(f"{dr_smith.name}'s schedule:")
for a in dr_smith.appointments:
    print(f"  - {a.time} with {a.patient.name} in Room {a.room.number}")
    
    
    
# Exercise 1: Online Course Platform
# Design Online Course Platform
# Solved
# Problem: Build a course platform where instructors create courses and students enroll in them. 
# This exercise practices unidirectional and one-to-many associations.

# Requirements:

# Instructor with a name and a list of Course objects they teach. An addCourse(course) method that adds the course and sets the instructor on the course.
# Course with a title, an Instructor reference, and a list of enrolled Student objects. 
# An enrollStudent(student) method that adds the student and sets the enrolled course on the student.
# Student with a name and an enrolledCourse reference (the course they're currently taking).
# A getInstructorName() method that navigates through the course to return the instructor's name.



class Instructor:
    def __init__(self, name: str):
        self.name = name
        self.courses = []

    def add_course(self, course):
        self.courses.append(course)
        course.set_instructor(self)

class Course:
    def __init__(self, title: str):
        self.title = title
        self.instructor = None
        self.students = []

    def set_instructor(self, instructor):
        self.instructor = instructor

    def enroll_student(self, student):
        self.students.append(student)
        student.set_enrolled_course(self)

class Student:
    def __init__(self, name: str):
        self.name = name
        self.enrolled_course = None

    def set_enrolled_course(self, course):
        self.enrolled_course = course

    def get_instructor_name(self) -> str:
        if self.enrolled_course and self.enrolled_course.instructor:
            return self.enrolled_course.instructor.name
        return "No instructor"

if __name__ == "__main__":
    alice = Instructor("Alice")
    dsa = Course("Data Structures")
    sys_design = Course("System Design")

    alice.add_course(dsa)
    alice.add_course(sys_design)

    bob = Student("Bob")
    charlie = Student("Charlie")

    dsa.enroll_student(bob)
    dsa.enroll_student(charlie)
    sys_design.enroll_student(charlie)

    print(f"{alice.name}'s courses:")
    for c in alice.courses:
        print(f"  - {c.title}")

    print(f"Students in {dsa.title}:")
    for s in dsa.students:
        print(f"  - {s.name}")

    print(f"{bob.name}'s instructor: {bob.get_instructor_name()}")
    
    
    
    

# Exercise 2: Social Network
# Design Social Network Classes
# Solved
# Problem: Build a social network where users can follow each other and send messages. 
# This exercise practices bidirectional and many-to-many associations with synchronization guards.

# Requirements:

# User with a name, a followers list, a following list, and a messages list of Message objects.
# follow(user) method that adds the target to following and adds this to the target's followers. 
# Include a duplicate guard to prevent infinite recursion and self-follows.
# Message with an author (User reference), content string, and timestamp string. The author's messages list is updated on creation.
# sendMessage(content, timestamp) that creates a Message and adds it to the user's messages list.



class Message:
    def __init__(self, author, content: str, timestamp: str):
        self.author = author
        self.content = content
        self.timestamp = timestamp

class User:
    def __init__(self, name: str):
        self.name = name
        self.followers = []
        self.following = []
        self.messages = []

    def follow(self, user):
        if user is self:
            return
        if user in self.following:
            return
        self.following.append(user)
        user.followers.append(self)

    def send_message(self, content: str, timestamp: str):
        message = Message(self, content, timestamp)
        self.messages.append(message)

if __name__ == "__main__":
    alice = User("Alice")
    bob = User("Bob")
    charlie = User("Charlie")

    alice.follow(bob)
    alice.follow(charlie)
    bob.follow(alice)

    alice.send_message("Hello world!", "10:00 AM")
    bob.send_message("Learning OOP!", "10:30 AM")

    print(f"{alice.name} is following:")
    for u in alice.following:
        print(f"  - {u.name}")

    print(f"{bob.name}'s followers:")
    for u in bob.followers:
        print(f"  - {u.name}")

    print(f"{alice.name}'s messages:")
    for m in alice.messages:
        print(f"  [{m.timestamp}] {m.content}")
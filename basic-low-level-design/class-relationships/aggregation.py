# Let’s model a real-world aggregation: The relationship between a university Department and its Professors.

# A department "has" professors, but the professors are independent entities. If the department is restructured or closed, 
# the professors (as university employees) still exist and can be assigned to other departments. The department does not own the lifecycle of the professors.


class Professor:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name
		
class Department:
    def __init__(self, name, professors):
        self.name = name
        self.professors = professors

    def print_professors(self):
        print(f"Professors in {self.name} Department:")
        for professor in self.professors:
            print(f"- {professor.get_name()}")
			
if __name__ == "__main__":
    p1 = Professor("Dr. Smith")
    p2 = Professor("Dr. Johnson")

    profs = [p1, p2]

    cs_dept = Department("Computer Science", profs)
    cs_dept.print_professors()

    # cs_dept can go out of scope or be deleted...
    # but p1 and p2 still exist and can be used elsewhere.			
    
    
    
    
    
#  Practical Example: Music Library System
# Let's build a system that demonstrates aggregation across multiple classes. A music library manages artists, songs, playlists, and users. The relationships between these entities show how parts (songs) can be shared across multiple wholes (playlists), and how deleting a whole leaves its parts intact.

# Here's how the classes connect:

# Artist is an independent entity that creates songs.
# Song belongs to an Artist but exists independently of any playlist.
# Playlist aggregates multiple Song objects. The same song can appear in different playlists.
# User aggregates multiple Playlist objects. Deleting a user's playlist doesn't destroy the songs.
# Library holds the master collection of all songs, independent of any playlist or user.





class Artist:
    def __init__(self, name: str):
        self.name = name

class Song:
    def __init__(self, title: str, artist: Artist, duration: int):
        self.title = title
        self.artist = artist
        self.duration = duration

    def __str__(self):
        return f"{self.title} by {self.artist.name} ({self.duration}s)"

class Playlist:
    def __init__(self, name: str):
        self.name = name
        self.songs = []

    def add_song(self, song: Song):
        self.songs.append(song)

    def remove_song(self, song: Song):
        self.songs.remove(song)

    def get_song_count(self):
        return len(self.songs)

    def get_total_duration(self):
        return sum(song.duration for song in self.songs)

class User:
    def __init__(self, name: str):
        self.name = name
        self.playlists = []

    def create_playlist(self, playlist_name: str):
        playlist = Playlist(playlist_name)
        self.playlists.append(playlist)
        return playlist

    def delete_playlist(self, playlist: Playlist):
        self.playlists.remove(playlist)

class Library:
    def __init__(self):
        self.songs = []

    def add_song(self, song: Song):
        self.songs.append(song)

    def get_song_count(self):
        return len(self.songs)

# Usage
if __name__ == "__main__":
    coldplay = Artist("Coldplay")
    adele = Artist("Adele")

    yellow = Song("Yellow", coldplay, 269)
    clocks = Song("Clocks", coldplay, 307)
    hello = Song("Hello", adele, 295)
    someone = Song("Someone Like You", adele, 285)

    library = Library()
    library.add_song(yellow)
    library.add_song(clocks)
    library.add_song(hello)
    library.add_song(someone)

    alice = User("Alice")
    workout = alice.create_playlist("Workout Mix")
    chill = alice.create_playlist("Chill Vibes")

    workout.add_song(yellow)
    workout.add_song(clocks)
    workout.add_song(hello)

    chill.add_song(hello)
    chill.add_song(someone)

    print(f"Library has {library.get_song_count()} songs")
    print()

    print(f"{workout.name} ({workout.get_song_count()} songs, {workout.get_total_duration()}s):")
    for s in workout.songs:
        print(f"  - {s}")
    print()

    print(f"{chill.name} ({chill.get_song_count()} songs, {chill.get_total_duration()}s):")
    for s in chill.songs:
        print(f"  - {s}")
    print()

    alice.delete_playlist(workout)
    print(f"After deleting '{workout.name}':")
    print(f"  Library still has {library.get_song_count()} songs")
    print(f"  '{chill.name}' still has {chill.get_song_count()} songs")
    print(f"  'Yellow' still exists: {yellow.title}")
    
    
    
    
    
    
    
    
    
# Exercise 1: Shopping Cart System
# Design Shopping Cart Class
# Solved
# Problem: Build an e-commerce system where products exist in a catalog and customers add them to shopping carts. This exercise practices aggregation where parts (products) are shared across multiple wholes (carts) and survive when a cart is cleared.

# Requirements:

# Product with a name and price.
# Catalog with a list of Product objects. A findByName(name) method that returns the matching product.
# Cart with a list of Product objects. addItem(product) and clearCart() methods. A getTotal() method that sums the prices.
# Customer with a name and a Cart. A checkout() method that prints the cart contents and total, then clears the cart.

class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

class Catalog:
    def __init__(self):
        self.products = []

    def add_product(self, product: Product):
        # TODO: Add product to catalog
        self.products.append(product)

    def find_by_name(self, name: str):
        # TODO: Find and return product by name, return None if not found
        for product in self.products:
            if product.name == name:
                return product
        return None

    def get_product_count(self):
        return len(self.products)

class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product: Product):
        # TODO: Add product to cart
        self.items.append(product)

    def clear_cart(self):
        # TODO: Remove all items (don't destroy the products!)
        self.items = []

    def get_total(self):
        # TODO: Sum prices of all items
        return sum(item.price for item in self.items)

    def get_item_count(self):
        return len(self.items)

class Customer:
    def __init__(self, name: str, cart: Cart):
        self.name = name
        self.cart = cart

    def checkout(self):
        print(f"{self.name} checking out:")
        for p in self.cart.items:
            print(f"  - {p.name}: ${p.price}")
        print(f"  Total: ${self.cart.get_total()}")
        self.cart.clear_cart()

if __name__ == "__main__":
    laptop = Product("Laptop", 999.99)
    mouse = Product("Mouse", 29.99)
    keyboard = Product("Keyboard", 79.99)

    catalog = Catalog()
    catalog.add_product(laptop)
    catalog.add_product(mouse)
    catalog.add_product(keyboard)

    cart1 = Cart()
    cart2 = Cart()

    alice = Customer("Alice", cart1)
    bob = Customer("Bob", cart2)

    cart1.add_item(laptop)
    cart1.add_item(mouse)
    cart2.add_item(laptop)
    cart2.add_item(keyboard)

    print(f"Alice's cart: {cart1.get_item_count()} items, ${cart1.get_total()}")
    print(f"Bob's cart: {cart2.get_item_count()} items, ${cart2.get_total()}")

    alice.checkout()

    print(f"Catalog still has {catalog.get_product_count()} products")
    print(f"Bob's cart still has {cart2.get_item_count()} items")
    print(f"Laptop still exists: {laptop.name}")
    
    
    
    
# Exercise 2: Company Team Management
# Design Company Team Management
# Solved
# Problem: Build a company system where employees can belong to multiple teams. Dissolving a team doesn't remove the employees. This exercise reinforces that aggregation parts survive the deletion of the whole and can be shared.

# Requirements:

# Employee with a name and role. A getTeamNames() method that returns the names of all teams the employee belongs to.
# Team with a name and a list of Employee objects. An addMember(employee) method that adds the employee and registers the team on the employee. A dissolve() method that clears the member list without destroying employees.
# Company with a name and lists of both Employee and Team objects. A dissolveTeam(team) method that dissolves the team and removes it from the company.




class Employee:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.teams = []

    def add_team(self, team):
        self.teams.append(team)

    def remove_team(self, team):
        self.teams.remove(team)

    def get_team_names(self):
        return [t.name for t in self.teams]

class Team:
    def __init__(self, name: str):
        self.name = name
        self.members = []

    def add_member(self, employee: Employee):
        self.members.append(employee)
        employee.add_team(self)

    def dissolve(self):
        for e in self.members:
            e.remove_team(self)
        self.members.clear()

    def get_member_count(self):
        return len(self.members)

class Company:
    def __init__(self, name: str):
        self.name = name
        self.employees = []
        self.teams = []

    def add_employee(self, employee: Employee):
        self.employees.append(employee)

    def add_team(self, team: Team):
        self.teams.append(team)

    def dissolve_team(self, team: Team):
        team.dissolve()
        self.teams.remove(team)

    def get_employee_count(self):
        return len(self.employees)

    def get_team_count(self):
        return len(self.teams)

if __name__ == "__main__":
    company = Company("TechCorp")

    alice = Employee("Alice", "Engineer")
    bob = Employee("Bob", "Designer")
    charlie = Employee("Charlie", "Engineer")

    company.add_employee(alice)
    company.add_employee(bob)
    company.add_employee(charlie)

    backend = Team("Backend")
    frontend = Team("Frontend")

    company.add_team(backend)
    company.add_team(frontend)

    backend.add_member(alice)
    backend.add_member(charlie)
    frontend.add_member(alice)
    frontend.add_member(bob)

    print("Before dissolving:")
    print(f"  {alice.name}'s teams: [{', '.join(alice.get_team_names())}]")
    print(f"  Backend has {backend.get_member_count()} members")
    print(f"  Company has {company.get_team_count()} teams, {company.get_employee_count()} employees")

    company.dissolve_team(backend)

    print("\nAfter dissolving Backend:")
    print(f"  {alice.name}'s teams: [{', '.join(alice.get_team_names())}]")
    print(f"  {charlie.name}'s teams: [{', '.join(charlie.get_team_names())}]")
    print(f"  Company has {company.get_team_count()} teams, {company.get_employee_count()} employees")
    print(f"  {alice.name} still exists: {alice.role}")
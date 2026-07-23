. What is Composition?
Composition is a special type of association that signifies strong ownership between objects. The “whole” class is fully responsible for creating, managing, and destroying the “part” objects. In fact, the parts cannot exist without the whole.

Key Characteristics of Composition:
Represents a strong “has-a” relationship.
The whole owns the part and controls its lifecycle.
When the whole is destroyed, the parts are also destroyed.
The parts are not shared with any other object.
The part has no independent meaning or identity outside the whole.
If the part makes no sense without the whole, use composition.



Real-World Analogy

Imagine a House and its Rooms:

A house has a living room, a kitchen, a bedroom.
These rooms do not exist on their own. They are part of the house.
When the house is demolished, the rooms are gone with it.
You don’t transfer a bedroom from one house to another.
This is a textbook example of composition. The rooms are tightly bound to the house—not just logically, but in lifecycle and ownership as well.




4. When to Use Composition
Use composition when you can answer "yes" to these questions:

Is the part meaningless without the whole? A line item without an order has no purpose. A room without a house makes no sense. If the part loses its identity outside the whole, that's composition.
Should the whole control the part's lifecycle? If the whole creates the parts and destroys them, that's composition. If the parts are created externally and passed in, that leans toward aggregation.
Are the parts exclusive to one whole? If a part belongs to exactly one whole and is never shared, that's composition. If the same part can appear in multiple wholes (like a song in multiple playlists), that's aggregation.
Do you want to model strong containment? When the relationship is "is composed of" rather than "groups together," composition is the right choice.
Composition is a preferred alternative to inheritance when building flexible systems.

“Favor composition over inheritance.” — GoF Design Principle



Why?
You can build complex behavior by composing smaller, reusable parts.
It avoids the tight coupling and fragility of inheritance hierarchies.
You can swap out parts dynamically to modify behavior.
For example:

A Vehicle can compose an Engine interface.
Swap between PetrolEngine, ElectricEngine, or HybridEngine at runtime.
This leads to cleaner, testable, and decoupled code.



 Composition vs Aggregation vs Association
Let’s compare association, aggregation, and composition side-by-side to understand how they differ in ownership, lifecycle, reusability, and usage in real systems.

Feature	Association	Aggregation	Composition
Ownership	None	Weak -- has-a	Strong -- owns-a
Lifecycle	Independent	Independent	Dependent -- part dies with whole
Tightness	Loose coupling	Moderate coupling	Tight coupling
Multiplicity	Flexible (1:1, 1:N, N:N)	Whole can group many parts	Whole composed of integral parts
Reusability	High -- parts reusable	Moderate -- parts often reused	Low -- parts not reused outside
UML Symbol	Solid Line	Hollow Diamond (◊)	Filled Diamond (◆)
Who creates parts?	Either side or external	External -- passed in	Whole -- created internally
Real Example	Student ↔ Course	Playlist → Song	Order → LineItem
Think of it like this:
Association is a general connection: two classes simply know about each other.
Aggregation is a grouping: the whole and parts can exist independently.
Composition is an ownership: the part’s existence is bound to the whole.
# Exercise 1: OrderService and Database
# Refactor OrderService
# Problem: An OrderService directly creates and uses a MySQLDatabase object to save orders. If you want to switch to PostgreSQL or MongoDB, you would have to rewrite OrderService. Refactor by introducing a Database interface so OrderService depends on the abstraction, not the concrete database. Then add a PostgresDatabase implementation and show both databases working with the same OrderService.

# Requirements:

# Create a Database interface with insert(table, data) and query(table, id) methods
# Make MySQLDatabase implement the Database interface
# Create a PostgresDatabase implementation that prints "PostgreSQL: ..." instead of "MySQL: ..."
# Refactor OrderService to accept a Database through its constructor instead of creating one internally
# Show OrderService working with both databases without changing OrderService


# before DIP

# Before: OrderService is tightly coupled to MySQLDatabase
class MySQLDatabase:
    def insert(self, table: str, data: str) -> None:
        print(f"MySQL: Inserting into {table} -> {data}")

    def query(self, table: str, id: str) -> str:
        print(f"MySQL: Querying {table} for id {id}")
        return f"{{ id: {id}, item: 'Widget' }}"

class OrderService:
    def __init__(self):
        self.database = MySQLDatabase()  # Direct dependency!

    def place_order(self, order_id: str, order_data: str) -> None:
        print(f"Placing order: {order_id}")
        self.database.insert("orders", order_data)
        print("Order placed successfully.")

    def get_order(self, order_id: str) -> str:
        return self.database.query("orders", order_id)

if __name__ == "__main__":
    service = OrderService()
    service.place_order("ORD-001", "{ item: 'Widget', qty: 3 }")
    order = service.get_order("ORD-001")
    print(f"Order: {order}")

# TODO: Create a Database ABC with insert() and query() methods.
# TODO: Make MySQLDatabase implement the interface.
# TODO: Create a PostgresDatabase that prints "PostgreSQL: ..." instead of "MySQL: ...".
# TODO: Refactor OrderService to accept a Database via its constructor.


# after DIP

from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    def insert(self, table: str, data: str) -> None:
        pass

    @abstractmethod
    def query(self, table: str, id: str) -> str:
        pass


class MySQLDatabase(Database):
    def insert(self, table: str, data: str) -> None:
        print(f"MySQL: Inserting into {table} -> {data}")

    def query(self, table: str, id: str) -> str:
        print(f"MySQL: Querying {table} for id {id}")
        return f"{{ id: {id}, item: 'Widget' }}"


class PostgresDatabase(Database):
    def insert(self, table: str, data: str) -> None:
        print(f"PostgreSQL: Inserting into {table} -> {data}")

    def query(self, table: str, id: str) -> str:
        print(f"PostgreSQL: Querying {table} for id {id}")
        return f"{{ id: {id}, item: 'Widget' }}"


class OrderService:
    def __init__(self, database: Database):
        self.database = database

    def place_order(self, order_id: str, order_data: str) -> None:
        print(f"Placing order: {order_id}")
        self.database.insert("orders", order_data)
        print("Order placed successfully.")

    def get_order(self, order_id: str) -> str:
        return self.database.query("orders", order_id)


if __name__ == "__main__":
    print("--- MySQL ---")
    mysql = MySQLDatabase()
    mysql_service = OrderService(mysql)
    mysql_service.place_order("ORD-001", "{ item: 'Widget', qty: 3 }")
    order1 = mysql_service.get_order("ORD-001")
    print(f"Order: {order1}")

    print()
    print("--- PostgreSQL ---")
    postgres = PostgresDatabase()
    pg_service = OrderService(postgres)
    pg_service.place_order("ORD-001", "{ item: 'Widget', qty: 3 }")
    order2 = pg_service.get_order("ORD-001")
    print(f"Order: {order2}")
    
    

# Exercise 2: WeatherApp and Weather Provider
# Refactor WeatherApp
# Problem: A WeatherApp directly calls OpenWeatherMapAPI to fetch weather data. If you want to switch to a different weather API (like WeatherStack or a local mock for testing), you would have to modify WeatherApp. Refactor by introducing a WeatherProvider interface so the app can work with any weather data source.

# Requirements:

# Create a WeatherProvider interface with a getWeather(city) method
# Create OpenWeatherMapProvider that implements the interface (wrapping the API call)
# Create WeatherStackProvider as a second implementation that returns different simulated data
# Refactor WeatherApp to accept a WeatherProvider through its constructor
# Show the app working with both providers without changing WeatherApp


# before DIP

# Before: WeatherApp is tightly coupled to OpenWeatherMapAPI
class OpenWeatherMapAPI:
    def fetch_weather(self, city: str) -> str:
        print(f"Calling OpenWeatherMap API for: {city}")
        return "Sunny, 25C"

class WeatherApp:
    def __init__(self):
        self.api = OpenWeatherMapAPI()  # Direct dependency!

    def display_weather(self, city: str) -> None:
        weather = self.api.fetch_weather(city)
        print(f"Weather in {city}: {weather}")

if __name__ == "__main__":
    app = WeatherApp()
    app.display_weather("London")

# TODO: Create a WeatherProvider ABC with a get_weather(city) method.
# TODO: Refactor WeatherApp to accept a WeatherProvider via its constructor.



# after DIP

from abc import ABC, abstractmethod


class WeatherProvider(ABC):
    @abstractmethod
    def get_weather(self, city: str) -> str:
        pass


class OpenWeatherMapProvider(WeatherProvider):
    def get_weather(self, city: str) -> str:
        print(f"Calling OpenWeatherMap API for: {city}")
        return "Sunny, 25C"


class WeatherStackProvider(WeatherProvider):
    def get_weather(self, city: str) -> str:
        print(f"Calling WeatherStack API for: {city}")
        return "Cloudy, 18C"


class WeatherApp:
    def __init__(self, provider: WeatherProvider):
        self.provider = provider

    def display_weather(self, city: str) -> None:
        weather = self.provider.get_weather(city)
        print(f"Weather in {city}: {weather}")


if __name__ == "__main__":
    print("--- OpenWeatherMap ---")
    app1 = WeatherApp(OpenWeatherMapProvider())
    app1.display_weather("London")

    print()
    print("--- WeatherStack ---")
    app2 = WeatherApp(WeatherStackProvider())
    app2.display_weather("London")
# Let's build the logging system from the opening scenario.
# The abstract Logger class has a level field, an abstract log() method that each subclass must implement, and a concrete formatMessage() method that adds a timestamp and log level prefix. 
# Every logger formats messages the same way, but each one delivers the formatted message differently.

from abc import ABC, abstractmethod
from datetime import datetime

class Logger(ABC):
    def __init__(self, level: str):
        self._level = level

    # Abstract method: subclasses decide HOW to deliver the message
    @abstractmethod
    def log(self, message: str) -> None:
        pass

    # Concrete method: shared formatting logic inherited by all subclasses
    def format_message(self, message: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self._level}] {message}"

class ConsoleLogger(Logger):
    def __init__(self, level: str):
        super().__init__(level)

    def log(self, message: str) -> None:
        print(self.format_message(message))

class FileLogger(Logger):
    def __init__(self, level: str, file_path: str):
        super().__init__(level)
        self._file_path = file_path

    def log(self, message: str) -> None:
        # In production, this would write to a file
        print(f"Writing to {self._file_path}: {self.format_message(message)}")
        


if __name__ == "__main__":
    console_logger = ConsoleLogger(level="INFO")
    flie_logger = FileLogger(level="ERROR", file_path="errors.txt")
    
    console_logger.log("System initialized successfully.")
    
    flie_logger.log("Database connection failed.")
        
        
# Interfaces as Abstraction
# While abstract classes abstract a family of related classes that share behavior,
# interfaces abstract a capability that unrelated classes can share. Consider data export: 
# you might need to export user data as CSV, order data as JSON, or analytics data as XML. 
# These classes have nothing in common structurally, but they all share the capability of exporting data.



class Exportable(ABC):
    @abstractmethod
    def export(self) -> str:
        pass

class CSVExporter(Exportable):
    def export(self) -> str:
        return "name,email,age\nAlice,alice@example.com,30"

class JSONExporter(Exportable):
    def export(self) -> str:
        return '{"name": "Alice", "email": "alice@example.com"}'
    
    
if __name__ == "__main__":
    csv_tool = CSVExporter()
    json_tool = JSONExporter()
    
    print(csv_tool.export())
    
    print(json_tool.export())
    
    

# 3. Public APIs as Abstraction
# You don't always need abstract classes or interfaces to achieve abstraction. 
# Sometimes a well-designed public API on a regular class is enough. 
# When a class hides its internal complexity behind a few clean public methods, that's abstraction in action.

# Consider a DatabaseClient. The caller sees connect() and query(). 
# Behind the scenes, the class manages connection pooling, socket lifecycle, 
# authentication handshakes, query parsing, and retry logic. None of that is the caller's concern.


class DatabaseClient:
    def __init__(self, max_connections: int, retry_attempts: int):
        self.__max_connections = max_connections
        self.__retry_attempts = retry_attempts
        
    # Clean public API: the caller's view
    def connect(self, host: str, port: int) -> None:
        self.__open_socket(host, port)
        self.__authenticate()
        self.__initialize_connection_pool()
    
    def query(self, sql: str) -> str:
        parsed_query = self.__parse_query(sql)
        return self.__execute_with_retry(parsed_query)

    
    # Hidden complexity: the implementation details
    def __open_socket(self, host: str, port: int) -> None: pass
    def __authenticate(self) -> None: pass
    def __initialize_connection_pool(self) -> None: pass
    def __parse_query(self, sql: str) -> str: return sql.strip()
    def __execute_with_retry(self, query: str) -> str:
        for i in range(self.__retry_attempts):
            try:
                return self.__execute_query(query)
            except Exception:
                if i == self.__retry_attempts - 1:
                    raise
        return ""
    def __execute_query(self, query: str) -> str: return "result"
    
    

if __name__ == "__main__":
    db = DatabaseClient(10, 3);
    db.connect("localhost", 5432);
    result = db.query("SELECT * FROM users");
    print(result)
    
    
    

# Media Player
# Let's apply abstraction to a different domain. 
# Imagine you're building a media application 
# that needs to play different types of content: audio files, video files, and streaming content.
# Each type has a completely different playback mechanism, but they all share certain behaviors: displaying the current status and logging user actions.


# The abstract MediaPlayer defines three abstract methods (play(), pause(), stop()) that each subclass must implement, 
# plus two concrete methods (displayStatus() and logAction()) that all players inherit.

# The PlayerController depends only on the abstract MediaPlayer, so it works with any player type without modification.


from abc import ABC, abstractmethod

class MediaPlayer(ABC):
    def __init__(self, player_name: str):
        self._player_name = player_name

    @abstractmethod
    def play(self) -> None:
        pass

    @abstractmethod
    def pause(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    def display_status(self) -> None:
        print(f"[{self._player_name}] Status: Ready")

    def log_action(self, action: str) -> None:
        print(f"[{self._player_name}] Action: {action}")


class AudioPlayer(MediaPlayer):
    def __init__(self, audio_file: str):
        super().__init__("AudioPlayer")
        self._audio_file = audio_file

    def play(self) -> None:
        self.log_action(f"Playing audio: {self._audio_file}")

    def pause(self) -> None:
        self.log_action(f"Paused audio: {self._audio_file}")

    def stop(self) -> None:
        self.log_action(f"Stopped audio: {self._audio_file}")


class VideoPlayer(MediaPlayer):
    def __init__(self, video_file: str, resolution: str):
        super().__init__("VideoPlayer")
        self._video_file = video_file
        self._resolution = resolution

    def play(self) -> None:
        self.log_action(f"Playing video: {self._video_file} at {self._resolution}")

    def pause(self) -> None:
        self.log_action(f"Paused video: {self._video_file}")

    def stop(self) -> None:
        self.log_action(f"Stopped video: {self._video_file}")


class StreamingPlayer(MediaPlayer):
    def __init__(self, stream_url: str, buffer_size: int):
        super().__init__("StreamingPlayer")
        self._stream_url = stream_url
        self._buffer_size = buffer_size

    def play(self) -> None:
        self.log_action(f"Streaming from: {self._stream_url} (buffer: {self._buffer_size}KB)")

    def pause(self) -> None:
        self.log_action(f"Paused stream: {self._stream_url}")

    def stop(self) -> None:
        self.log_action(f"Stopped stream: {self._stream_url}")


class PlayerController:
    def __init__(self, player: MediaPlayer):
        self._player = player

    def start_playback(self) -> None:
        self._player.display_status()
        self._player.play()

    def pause_playback(self) -> None:
        self._player.pause()

    def stop_playback(self) -> None:
        self._player.stop()


if __name__ == "__main__":
    audio_ctrl = PlayerController(AudioPlayer("song.mp3"))
    audio_ctrl.start_playback()
    audio_ctrl.pause_playback()

    print()

    video_ctrl = PlayerController(VideoPlayer("movie.mp4", "1080p"))
    video_ctrl.start_playback()
    video_ctrl.stop_playback()

    print()

    stream_ctrl = PlayerController(
        StreamingPlayer("https://stream.example.com/live", 2048))
    stream_ctrl.start_playback()
    stream_ctrl.stop_playback()
    
    
    
    
    
    
    
    
    
# Exercise 1: Shape Calculator
# Design Shape Calculator Class
# Solved
# Problem: Build a shape calculation system using an abstract class. The abstract Shape class has abstract methods for calculating area and perimeter, plus a concrete describe() method that all shapes inherit.

# Requirements:

# Abstract Shape class with: abstract area() and perimeter() methods, plus a concrete describe() method that prints "Shape: [name], Area: [area], Perimeter: [perimeter]"
# Circle: takes a radius. Area = pi r^2, Perimeter = 2 pi * r
# Rectangle: takes width and height. Area = w h, Perimeter = 2 (w + h)
# describe() should work for any shape without modification




import math

class Shape(ABC):
    def __init__(self, name: str):
        self._name = name

    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

    def describe(self) -> None:
        # Print: "Shape: [name], Area: [area], Perimeter: [perimeter]"
        # Use f-string with :.2f for formatting
        print(f"Shape: {self._name}, Area: {self.area():.2f}, Perimeter: {self.perimeter():.2f}")

class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("Circle")
        self._radius = radius

    def area(self) -> float:
        # Area = pi * r^2
        return math.pi * self._radius * self._radius

    def perimeter(self) -> float:
        # Perimeter = 2 * pi * r
        return 2 * math.pi * self._radius

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        super().__init__("Rectangle")
        self._width = width
        self._height = height

    def area(self) -> float:
        # Area = width * height
        return self._width * self._height

    def perimeter(self) -> float:
        # Perimeter = 2 * (width + height)
        return 2 * (self._width + self._height)


if __name__ == "__main__":
    circle = Circle(5.0)
    circle.describe()

    rectangle = Rectangle(4.0, 6.0)
    rectangle.describe()
    
    
    
    
    
    
# Exercise 2: Data Exporter
# Design Data Exporter Class
# Solved
# Problem: Build a data export system where the abstract class provides shared validation logic, and subclasses handle the actual export format.

# Requirements:

# Abstract DataExporter class with: a concrete validate(data) method that checks if data is not null/empty and prints a validation message, plus an abstract export(data) method
# CSVExporter: formats data as comma-separated values
# JSONExporter: formats data as a JSON array
# The validate() method should be called inside export() before formatting, so all exporters validate automatically
    
class DataExporter(ABC):
    def validate(self, data: list) -> bool:
        # Return False and print "Export failed: No data to export." if data is empty
        # Return True and print "Validation passed. Exporting N records." otherwise
        if not data:
            print("Export failed: No data to export.")
            return False
        print(f"Validation passed. Exporting {len(data)} records.")
        return True

    @abstractmethod
    def export(self, data: list) -> None:
        pass

class CSVExporter(DataExporter):
    def export(self, data: list) -> None:
        # Call self.validate(data) first. If validation fails, return early.
        # Otherwise, print CSV format: "CSV: Alice,Bob,Charlie"
        # Hint: use ",".join(data)
        if not self.validate(data):
            return
        print("CSV: " + ",".join(data))

class JSONExporter(DataExporter):
    def export(self, data: list) -> None:
        # Call self.validate(data) first. If validation fails, return early.
        # Otherwise, print JSON array format: JSON: ["Alice", "Bob", "Charlie"]
        if not self.validate(data):
            return
        items = ", ".join(f'"{item}"' for item in data)
        print(f"JSON: [{items}]")


if __name__ == "__main__":
    csv = CSVExporter()
    csv.export(["Alice", "Bob", "Charlie"])

    print()

    json_exp = JSONExporter()
    json_exp.export(["Alice", "Bob", "Charlie"])

    print()

    csv.export([])  # Should fail validation
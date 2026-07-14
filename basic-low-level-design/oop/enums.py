# Exercise 1: Traffic Light
# Design Traffic Light Class
# easy
# Solved
# Problem: Create a TrafficLight enum where each light has a color (RED, YELLOW, GREEN), a duration in seconds, and a next() method that returns the next light in the cycle (RED -> GREEN -> YELLOW -> RED).

# Requirements:

# Each light has a duration property: RED = 30s, YELLOW = 5s, GREEN = 25s
# next() method returns the next TrafficLight in the cycle
# display() method prints the color and duration


from enum import Enum

class TrafficLight(Enum):
    # Set values to duration: RED = 30, YELLOW = 5, GREEN = 25
    RED = 30
    YELLOW = 5
    GREEN = 25


    def next(self) -> "TrafficLight":
        # Return next light: RED->GREEN, GREEN->YELLOW, YELLOW->RED
        if self == TrafficLight.RED:
            return TrafficLight.GREEN
        elif self == TrafficLight.GREEN:
            return TrafficLight.YELLOW
        else:
            return TrafficLight.RED

    def display(self) -> None:
        print(f"{self.name} ({self.value}s)")

if __name__ == "__main__":
    light = TrafficLight.RED
    for _ in range(6):
        light.display()
        light = light.next()
        
        
        
        
        
# Exercise 2: HTTP Status Code
# Implement HTTP Status Code
# medium
# Solved
# Problem: Create an HttpStatus enum where each status has a numeric code and a message string.

# Requirements:

# Values: OK(200, "OK"), BAD_REQUEST(400, "Bad Request"), NOT_FOUND(404, "Not Found"), INTERNAL_SERVER_ERROR(500, "Internal Server Error")
# isSuccess() method that returns true if the code is less than 400
# display() method that prints "CODE MESSAGE" (e.g. "200 OK")
# A static fromCode(int) method that returns the HttpStatus for a given code, or null/None if not found




from enum import Enum

class HttpStatus(Enum):
    # Set values to (code, message) tuples:
    # OK = (200, "OK"), BAD_REQUEST = (400, "Bad Request"),
    # NOT_FOUND = (404, "Not Found"), INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    OK = (200, "OK")
    BAD_REQUEST = (400, "Bad Request")
    NOT_FOUND = (404, "Not Found")
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    def is_success(self) -> bool:
        return self.code < 400

    def display(self) -> None:
        print(f"{self.code} {self.message}")

    @staticmethod
    def from_code(code: int):
        for status in HttpStatus:
            if status.code == code:
                return status
        return None


if __name__ == "__main__":
    HttpStatus.OK.display()
    HttpStatus.NOT_FOUND.display()

    print(f"Is 200 success? {str(HttpStatus.OK.is_success()).lower()}")
    print(f"Is 404 success? {str(HttpStatus.NOT_FOUND.is_success()).lower()}")

    found = HttpStatus.from_code(500)
    if found is not None:
        print("Found by code 500: ", end="")
        found.display()
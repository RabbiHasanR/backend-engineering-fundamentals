1. The Problem: Building Complex HttpRequest Objects


Imagine you're building a system that needs to configure and create HTTP requests.

Each HttpRequest can contain a mix of required and optional fields:

URL (required)
HTTP Method (e.g., GET, POST, PUT, defaults to GET)
Headers (optional, multiple key-value pairs)
Query Parameters (optional, multiple key-value pairs)
Request Body (optional, typically for POST/PUT)
Timeout (optional, default to 30 seconds)
At first glance, it seems manageable. But as the number of optional fields increases, so does the complexity of object construction.

The Naive Approach: Telescoping Constructors
A common approach is constructor overloading, often called the telescoping constructor anti-pattern. You define multiple constructors with increasing numbers of parameters:

```python
class HttpRequestTelescoping:
    def __init__(self, url, method="GET", headers=None, query_params=None, body=None, timeout=30000):
        self.url = url
        self.method = method
        self.headers = headers if headers is not None else {}
        self.query_params = query_params if query_params is not None else {}
        self.body = body
        self.timeout = timeout

        print(f"HttpRequest Created: URL={url}, "
              f"Method={method}, "
              f"Headers={len(self.headers)}, "
              f"Params={len(self.query_params)}, "
              f"Body={body is not None}, "
              f"Timeout={timeout}")

    # Optional: add getter methods if needed
```


Example Client Code


```python
if __name__ == "__main__":
    req1 = HttpRequestTelescoping("https://api.example.com/data")

    req2 = HttpRequestTelescoping(
        "https://api.example.com/submit",
        "POST",
        None,
        None,
        '{"key":"value"}'
    )

    req3 = HttpRequestTelescoping(
        "https://api.example.com/config",
        "PUT",
        {"X-API-Key": "secret"},
        None,
        "config_data",
        5000
    )
```


What’s Wrong with This Approach?
While it works functionally, this design quickly becomes unwieldy and error-prone as the object becomes more complex.

1. Hard to Read and Write
Multiple parameters of the same type (e.g., String, Map) make it easy to accidentally swap arguments. Code is difficult to understand at a glance, especially when most parameters are null.

2. Error-Prone
Clients must pass null for optional parameters they do not want to set, increasing the risk of bugs. One wrong position and you silently assign a value to the wrong field.

3. Inflexible and Fragile
If you want to set parameter 5 but not 3 and 4, you are forced to pass null for 3 and 4. You must follow the exact parameter order, which hurts both readability and usability.

4. Poor Scalability
Adding a new optional parameter requires adding or changing constructors, which may break existing code. Testing and documentation become increasingly difficult to maintain.

We need a more flexible, readable, and maintainable way to construct HttpRequest objects. This is exactly where the Builder pattern comes in.



2. What is the Builder Pattern
The Builder pattern separates the construction of a complex object from its representation, allowing the same construction process to create different configurations.

Two ideas define the pattern:

Step-by-step construction: Instead of passing everything to a constructor at once, you set each field through individual method calls. You only call the methods for the fields you need.
Fluent interface: Each setter method returns the builder itself, allowing you to chain calls into a single readable expression that ends with build().

Before: Telescoping Constructor

```python
req = HttpRequest(
    url,                 # url
    method,              # method
    headers,             # headers
    None,                # body
    None,                # query_params
    30000                # timeout_ms
)
```

After: Builder Pattern

```python
req = (HttpRequest.Builder(url)
       .method("POST")
       .add_header("key", "val")
       .build())
```


3. How It Works
The Builder workflow follows a simple four-step process:

Step 1: Create the Builder
The client creates a Builder, passing any required parameters to its constructor.

Step 2: Configure Optional Fields
The client calls setter methods on the Builder for each optional field it needs. Each method returns the Builder itself, enabling chaining. The order of these calls does not matter.

Step 3: Build the Product
The client calls build(). The Builder passes itself to the Product's private constructor, which copies the configured state into immutable fields.

Step 4: Use the Product
The client receives a fully constructed, immutable Product. The Builder can be discarded or reused to create a different configuration
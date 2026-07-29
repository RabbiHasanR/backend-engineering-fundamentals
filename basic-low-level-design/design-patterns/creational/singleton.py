# Practical Example: In-Memory Cache Manager
# Lets say you are building an application where multiple components (HTTP handlers, database layer, background jobs) all need to cache expensive data like user profiles, configuration, and query results.

# You want one shared cache so that any component's writes are immediately visible to all others, without duplicate maps, stale reads, or wasted memory.

# Without Singleton:

# CacheManager cacheA = new CacheManager();
# cacheA.put("user:42", userData);

# CacheManager cacheB = new CacheManager();
# cacheB.get("user:42"); // null! Different instance, different map

# // Problems:
# // - Duplicate HashMaps wasting memory
# // - Writes in one component invisible to others
# // - TTL cleanup duplicated across instances

import threading
import time

class _CacheManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._cache: dict[str, tuple[str, float | None]] = {}
    
    def put(self, key: str, value: str, ttl_seconds: int = 0):
        expiry = time.time() + ttl_seconds if ttl_seconds > 0 else None
        with self._lock:
            self._cache[key] = (value, expiry)
            
    def get(self, key: str) -> str | None:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            value, expiry = entry
            
            if expiry is not None and time.time() > expiry:
                del self._cache[key]
                return None
            return value
    
    def remove(self, key: str):
        with self._lock:
            self._cache.pop(key, None)
    
    def size(self) -> int:
        now = time.time()
        with self._lock:
            self._cache = {
                k: (v, exp) for k, (v, exp) in self._cache.items()
                if exp is None or now <= exp
            }
            return len(self._cache)


# Module-level singleton
cache_manager = _CacheManager()




# --- Main ---
if __name__ == "__main__":
    # Both references point to the same CacheManager instance
    cache1 = cache_manager
    cache2 = cache_manager

    print(f"Same instance? {cache1 is cache2}")  # True

    # Component A caches data
    cache1.put("user:42", "{name: 'Alice'}", 5)  # 5-second TTL
    cache1.put("config:theme", "dark")            # no expiry

    # Component B reads from the same cache
    print(f"user:42 = {cache2.get('user:42')}")         # {name: 'Alice'}
    print(f"config:theme = {cache2.get('config:theme')}") # dark
    print(f"Cache size: {cache2.size()}")                 # 2
    
    



# Exercise 1: Thread-Safe Counter
# Implement Singleton Counter Class
# easy
# Solved
# Problem: Implement a Counter singleton that tracks a count across the application. Multiple components should be able to increment the counter, and all must see the same value.

# Requirements:

# increment() increases the count by 1
# getCount() returns the current count
# Thread-safe: concurrent increments must not lose updates
# Calling the constructor/access method from different places returns the same instance

# before singleton

class Counter:
    # TODO: Implement as singleton (module-level or __new__)

    def __init__(self):
        self._count = 0

    def increment(self):
        # TODO: Make thread-safe
        pass

    def get_count(self):
        # TODO: Return current count
        return 0


if __name__ == "__main__":
    # After implementing, usage should look like:
    # c1 = get_counter()  # or Counter()
    # c2 = get_counter()
    # print(f"Same instance: {c1 is c2}")
    # for _ in range(5):
    #     c1.increment()
    # print(f"Count after 5 increments: {c1.get_count()}")
    pass


# after singleton

import threading

class Counter:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._count = 0
                    cls._instance._count_lock = threading.Lock()
        return cls._instance

    def increment(self):
        with self._count_lock:
            self._count += 1

    def get_count(self):
        return self._count


if __name__ == "__main__":
    c1 = Counter()
    c2 = Counter()
    print(f"Same instance: {c1 is c2}")
    for _ in range(5):
        c1.increment()
    print(f"Count after 5 increments: {c1.get_count()}")
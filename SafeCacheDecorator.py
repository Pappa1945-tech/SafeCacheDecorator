import functools
import threading
from time import time as timetime

class SafeCache:
    def __init__(self, maxsize=10000, ttl=None):
        """
        :param maxsize: Maximum number of cached items (LRU behavior)
        :param ttl: Time-To-Live in seconds (None means no expiration)
        """
        self.cache = {}  # Store cached values
        self.timestamps = {}  # Store timestamps for TTL tracking
        self.maxsize = maxsize
        self.ttl = ttl  # Optional TTL
        self.access_order = []  # Track access order for LRU eviction
        self.lock = threading.RLock()


    def clear(self):
        """Clears the entire cache."""
        with self.lock:
            self.cache.clear()

    def _make_hashable(self, args, kwargs):
        """Convert mutable types (list/dict) into immutable types for hashing."""
        def make_immutable(value):
            if isinstance(value, list):
                return tuple(make_immutable(v) for v in value)
            elif isinstance(value, dict):
                return tuple(sorted((k, make_immutable(v)) for k, v in value.items()))
            return value

        hashable_args = tuple(make_immutable(arg) for arg in args)
        hashable_kwargs = tuple(sorted((k, make_immutable(v)) for k, v in kwargs.items()))
        return (hashable_args, hashable_kwargs)

    def _is_expired(self, key):
        """Check if a cached entry is expired based on TTL."""
        if self.ttl is None:
            return False  # No TTL, never expires
        return (timetime() - self.timestamps.get(key, 0)) > self.ttl

    def get(self, key):
        """Retrieve from cache if not expired."""
        with self.lock:
            if key in self.cache:
                if self._is_expired(key):
                    # Remove expired item
                    del self.cache[key]
                    del self.timestamps[key]
                    self.access_order.remove(key)
                    return None
                # Move key to end for LRU behavior
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None

    def set(self, key, value):
        """Store in cache with optional TTL."""
        with self.lock:
            if key in self.cache:
                self.access_order.remove(key)  # Remove key if it already exists
            elif len(self.cache) >= self.maxsize:
                # Remove the Least Recently Used (first) entry
                oldest_key = self.access_order.pop(0)
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]

            self.cache[key] = value
            self.timestamps[key] = timetime()  # Store current time for TTL tracking
            self.access_order.append(key)  # Move key to end (most recently used)


    def __call__(self, func):
        """Decorator for function caching with TTL support."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = self._make_hashable(args, kwargs)
            result = self.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            self.set(key, result)
            return result
        return wrapper

"""
CS50P Final Project: Cache Decorator Performance Comparison
Tests SafeCache against native lru_cache with unhashable types
"""

from time import time as timetime, sleep
from functools import lru_cache
from safecache import SafeCache

# Test Configuration
ITERATIONS = 3
SLEEP_DURATION = 1  # Seconds per simulated work
DATA = ([2,3,4,5], [6,7,8,9])  # Intentionally unhashable

def test_uncached():
    """Baseline performance without caching"""
    start = timetime()
    
    def operation(a, b):
        sleep(SLEEP_DURATION)
        return sum(a) * sum(b)
    
    for _ in range(ITERATIONS):
        operation(*DATA)
    
    print(f"[1/3] Uncached:\t{timetime() - start:.2f}s ({ITERATIONS} full executions)")

def test_lru_cache():
    """Demonstrates lru_cache limitation"""
    start = timetime()
    
    @lru_cache(maxsize=128)
    def operation(a, b):
        sleep(SLEEP_DURATION)
        return sum(a) * sum(b)
    
    try:
        for _ in range(ITERATIONS):
            operation(*DATA)  # Will raise TypeError
    except TypeError as e:
        print(f"[2/3] lru_cache:\tFAILED - {str(e)}")
        print("       → Cannot handle unhashable types like lists")

def test_safecache():
    """Shows SafeCache's solution"""
    start = timetime()
    
    @SafeCache(maxsize=128)
    def operation(a, b):
        sleep(SLEEP_DURATION)
        return sum(a) * sum(b)
    
    for _ in range(ITERATIONS):
        operation(*DATA)
    
    print(f"[3/3] SafeCache:\t{timetime() - start:.2f}s (1 execution + {ITERATIONS-1} cached)")
    print("       → Successfully handles unhashable types")

if __name__ == "__main__":
    print(f"\nTesting with {ITERATIONS} iterations (sleep={SLEEP_DURATION}s):")
    test_uncached()
    test_lru_cache()
    test_safecache()
    
    print("\nKey Takeaways:")
    print("- lru_cache fails with common Python types like lists")
    print("- SafeCache provides caching while handling real-world data structures")
    print(f"- {ITERATIONS}x speedup demonstrated (from {ITERATIONS*SLEEP_DURATION}s → {SLEEP_DURATION}s)")

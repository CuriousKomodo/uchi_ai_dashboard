from typing import Dict, Optional
from datetime import datetime
from cachetools import TTLCache, cached
from collections import defaultdict

class CacheManager:
    def __init__(self, maxsize: int = 1000, ttl: int = 300):
        """
        Initialize cache manager with configurable size and TTL.

        Args:
            maxsize: Maximum number of items in cache
            ttl: Time to live in seconds (default 5 minutes)
        """
        self._property_cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._extraction_cache = TTLCache(maxsize=maxsize, ttl=ttl)

        # Initialize cache statistics
        self._cache_stats = {
            'property': {
                'hits': 0,
                'misses': 0,
                'size': 0,
                'last_updated': datetime.now()
            },
            'extraction': {
                'hits': 0,
                'misses': 0,
                'size': 0,
                'last_updated': datetime.now()
            }
        }

    def _update_cache_stats(self, cache_type: str, hit: bool):
        """Update cache statistics."""
        stats = self._cache_stats[cache_type]
        if hit:
            stats['hits'] += 1
        else:
            stats['misses'] += 1
        stats['size'] = len(self._property_cache if cache_type == 'property' else self._extraction_cache)
        stats['last_updated'] = datetime.now()

    def get_cache_stats(self, cache_type: Optional[str] = None) -> Dict:
        """
        Get cache statistics.

        Args:
            cache_type: Optional. If specified, returns stats for that cache type only.
                       Can be 'property' or 'extraction'.

        Returns:
            Dictionary containing cache statistics.
        """
        if cache_type:
            return self._cache_stats.get(cache_type, {})
        return self._cache_stats

    def get_cache_hit_rate(self, cache_type: Optional[str] = None) -> float:
        """
        Calculate cache hit rate.

        Args:
            cache_type: Optional. If specified, returns hit rate for that cache type only.
                       Can be 'property' or 'extraction'.

        Returns:
            Hit rate as a float between 0 and 1.
        """
        if cache_type:
            stats = self._cache_stats[cache_type]
            total = stats['hits'] + stats['misses']
            return stats['hits'] / total if total > 0 else 0.0

        total_hits = sum(stats['hits'] for stats in self._cache_stats.values())
        total_accesses = sum(stats['hits'] + stats['misses'] for stats in self._cache_stats.values())
        return total_hits / total_accesses if total_accesses > 0 else 0.0

    def reset_cache_stats(self):
        """Reset all cache statistics."""
        for cache_type in self._cache_stats:
            self._cache_stats[cache_type] = {
                'hits': 0,
                'misses': 0,
                'size': 0,
                'last_updated': datetime.now()
            }

    def get_property_cache(self) -> TTLCache:
        """Get the property cache instance."""
        return self._property_cache

    def get_extraction_cache(self) -> TTLCache:
        """Get the extraction cache instance."""
        return self._extraction_cache
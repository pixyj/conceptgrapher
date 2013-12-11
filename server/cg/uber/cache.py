from django.core.cache import cache

def cache_key_for(key, seconds):
	def decorator(fn):
		def wrapper(*args, **kwargs):
			result = cache.get(key)
			if not result:
				result = fn(*args, **kwargs)
				cache.set(key, result)
			return result
		return wrapper
	return decorator


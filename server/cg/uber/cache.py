from django.core.cache import cache

import collections
import functools

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



class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    '''
    def __init__(self, func):
       self.func = func
       self.cache = {}
    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value
    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__
    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)

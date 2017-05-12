__version__ = '0.1.0'
__license__ = 'BSD'

# name is chosen to match Autobahn RPC decorator.
def register(uri):
   """
   Decorator for RPC procedure endpoints.
   """
   def decorate(f):
      # called once when method is decorated, because we return 'f'.
      assert(callable(f))
      if not hasattr(f, '_wslinkuris'):
         f._wslinkuris = []
      f._wslinkuris.append({ "uri": uri })
      return f
   return decorate


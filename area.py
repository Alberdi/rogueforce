from sieve import Sieve

class Area(object):
  def __init__(self, general, sieve_function=None):
    self.general = general
    self.sieve = None if sieve_function is None else Sieve(general, sieve_function)

  def get_all_tiles(self):
    return []

  def get_all_tiles(self, x, y):
    return self.get_tiles()

  def get_tiles(self, x, y):
    if self.sieve is None:
      return self.get_all_tiles(x, y)
    return filter(self.sieve.apply, self.get_all_tiles(x, y))

class SingleTarget(Area):
  def get_all_tiles(self, x, y):
    if not self.general.bg.is_inside(x, y): return []
    return [self.general.bg.tiles[(x, y)]]

from sieve import Sieve

class Area(object):
  def __init__(self, bg, sieve_function=None, general=None):
    self.bg = bg
    self.general = general
    self.sieve = None if sieve_function is None else Sieve(general, sieve_function)

  def get_all_tiles(self, x, y):
    return self.get_tiles()

  def get_tiles(self, x, y):
    if self.sieve is None:
      return self.get_all_tiles(x, y)
    return filter(self.sieve.apply, self.get_all_tiles(x, y))

class AllBattleground(Area):
  def get_all_tiles(self, x, y):
    return self.bg.tiles.values()

class Circle(Area):
  def __init__(self, bg, sieve_function=None, general=None, radius=5):
    super(Circle, self).__init__(bg, sieve_function, general)
    self.radius = radius

  def get_all_tiles(self, x, y):
    square = [(a,b) for a in range(x-self.radius, x+self.radius+1) for b in range(y-self.radius, y+self.radius+1)]
    return [self.bg.tiles[(a,b)] for (a,b) in square if self.bg.is_inside(a,b) and (a-x)**2+(b-y)**2 <= self.radius**2]
      
class SingleTarget(Area):
  def get_all_tiles(self, x, y):
    if not self.bg.is_inside(x, y): return []
    return [self.bg.tiles[(x, y)]]

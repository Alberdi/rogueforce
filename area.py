from sieve import Sieve
import math

class Area(object):
  def __init__(self, bg, sieve_function=None, general=None, reach_function=None, selfcentered=False):
    self.bg = bg
    self.general = general
    self.sieve = Sieve(general, sieve_function) if sieve_function else None
    self.reach = Sieve(general, reach_function) if reach_function else None
    self.selfcentered = selfcentered

  def get_all_tiles(self, x, y):
    return self.get_tiles()

  def get_tiles(self, x, y):
    if self.selfcentered:
      (x, y) = (self.general.x, self.general.y)
    if self.reach and self.bg.is_inside(x, y) and not self.reach.apply(self.bg.tiles[(x, y)]):
      return []
    if not self.sieve:
      return self.get_all_tiles(x, y)
    return filter(self.sieve.apply, self.get_all_tiles(x, y))

class AllBattleground(Area):
  def get_all_tiles(self, x, y):
    return self.bg.tiles.values()

class Arc(Area):
  def __init__(self, bg, sieve_function=None, general=None, reach_function=None, selfcentered=False,
               origin=(0,0), angle=360, ratio_y=1, steps=50):
    super(Arc, self).__init__(bg, sieve_function, general, reach_function, selfcentered)
    self.origin = origin
    self.ratio_y = ratio_y
    self.start_angle = math.radians(angle)
    self.steps = steps
    self.step_angle = self.start_angle / self.steps

  def get_all_tiles(self, x, y):
    if not self.bg.is_inside(x, y):
      return []
    tiles = []
    center_x = (self.origin[0] + x) / 2.0
    center_y = self.origin[1]
    radius = abs(self.origin[0] - x) / 2.0
    direction = math.copysign(1, self.origin[0] - x)
    xx = int(round(center_x + math.cos(self.start_angle) * radius * direction))
    yy = int(round(center_y + math.sin(self.start_angle) * radius * self.ratio_y))
    if self.bg.is_inside(xx, yy):
      tiles.append(self.bg.tiles[(xx, yy)])
    for i in range(1, self.steps+1):
      angle = self.start_angle + i * self.step_angle
      xx = int(round(center_x + math.cos(angle) * radius * direction))
      yy = int(round(center_y + math.sin(angle) * radius * self.ratio_y))
      if not self.bg.is_inside(xx, yy):
        return []
      if self.bg.tiles[(xx, yy)] not in tiles:
        tiles.append(self.bg.tiles[(xx, yy)])
    return tiles

class Circle(Area):
  def __init__(self, bg, sieve_function=None, general=None, reach_function=None, selfcentered=False, radius=5):
    super(Circle, self).__init__(bg, sieve_function, general, reach_function, selfcentered)
    self.radius = radius

  def get_all_tiles(self, x, y):
    square = [(a,b) for a in range(x-self.radius, x+self.radius+1) for b in range(y-self.radius, y+self.radius+1)]
    return [self.bg.tiles[(a,b)] for (a,b) in square if self.bg.is_inside(a,b) and (a-x)**2+(b-y)**2 <= self.radius**2]
      
class CustomArea(Area):
  def __init__(self, bg, sieve_function=None, general=None, tiles=[]):
    super(CustomArea, self).__init__(bg, sieve_function, general)
    self.tiles = tiles

  def get_all_tiles(self, x, y):
    return self.tiles

class SingleTarget(Area):
  def get_all_tiles(self, x, y):
    if not self.bg.is_inside(x, y): return []
    return [self.bg.tiles[(x, y)]]

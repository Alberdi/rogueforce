from sieve import Sieve
import math

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

class Arc(Area):
  def __init__(self, bg, sieve_function=None, general=None, origin=(0,0), angle=360, ratio_y=1, steps=50):
    super(Arc, self).__init__(bg, sieve_function, general)
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
      if self.bg.is_inside(xx, yy) and self.bg.tiles[(xx, yy)] not in tiles:
        tiles.append(self.bg.tiles[(xx, yy)])
    return tiles

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

class StraightLine(Area):
  def get_all_tiles(self, x_f, y_f):
    step = 1.0
    tiles = []
    x_0 = self.general.x
    y_0 = self.general.y
    if self.bg.is_inside(x_f, y_f) and (x_f - x_0 or y_f - y_0):
      x = x_0
      y = y_0
      if abs(x_f - x_0) > abs(y_f - y_0):
        while self.bg.is_inside(int(round(x)), int(round(y))):
          if (int(round(x)), int(round(y))) not in tiles:
            tiles.append(self.bg.tiles[(int(round(x)), int(round(y)))])
          x += step if x_f > x_0 else -step
          y = (x - x_0) * (y_f - y_0) / (x_f - x_0) + y_0
      else:
        while self.bg.is_inside(int(round(x)), int(round(y))):
          if (int(round(x)), int(round(y))) not in tiles:
            tiles.append(self.bg.tiles[(int(round(x)), int(round(y)))])
          y += step if y_f > y_0 else -step
          x = (y - y_0) * (x_f - x_0) / (y_f - y_0) + x_0
    return tiles
    

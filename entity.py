import libtcodpy as libtcod

class Entity(object):
  def __init__(self, battleground, x, y, char):
    self.bg = battleground
    self.x = x
    self.y = y
    self.char = char
    self.color = libtcod.white
    self.bg.tiles[(x, y)].entity = self

  def move(self, dx, dy):
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    if next_tile.is_passable():
      self.bg.tiles[(self.x, self.y)].entity = None
      next_tile.entity = self
      self.x += dx
      self.y += dy


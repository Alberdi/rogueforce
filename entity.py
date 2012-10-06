import libtcodpy as libtcod

class Entity(object):
  def __init__(self, battleground, x, y, char):
    self.bg = battleground
    self.x = x
    self.y = y
    self.char = char
    self.color = libtcod.white

  def move(self, dx, dy):
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    if next_tile.is_passable():
      self.bg.tiles[(self.x, self.y)].entity = None
      next_tile.entity = self
      self.x += dx
      self.y += dy

  def draw(self, con):
    libtcod.console_set_default_foreground(con, self.color)
    libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)


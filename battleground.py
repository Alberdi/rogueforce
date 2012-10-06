import libtcodpy as libtcod

class Tile(object):
  def __init__(self, x, y, passable = True):
    self.passable = passable
    self.char = "."
    self.color = libtcod.Color(50, 50, 150)
    self.entity = None
    self.x = x
    self.y = y

  def is_passable(self):
    return self.entity == None# and self.passable

  def draw(self, con):
    libtcod.console_set_default_foreground(con, self.color)
    libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)


class Battleground(object):
  def __init__(self, width, height):
    self.height = height
    self.width = width
    self.tiles = {}
    for x in range(width):
      for y in range(height):
        self.tiles[(x,y)] = Tile(x, y)

  def draw(self, con):
    for pos in self.tiles:
      self.tiles[pos].draw(con)
    

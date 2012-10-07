import libtcodpy as libtcod

class Battleground(object):
  def __init__(self, width, height):
    self.height = height
    self.width = width
    self.tiles = {}
    for x in range(width):
      for y in range(height):
        if x in [0, width-1] or y in [0,height-1]: # Walls
          self.tiles[(x,y)] = Tile(x, y, "#", False)
        else: # Floor
          self.tiles[(x,y)] = Tile(x, y)

  def draw(self, con):
    for pos in self.tiles:
      self.tiles[pos].draw(con)
 

class Tile(object):
  def __init__(self, x, y, char = ".", passable = True):
    self.passable = passable
    self.char = char
    self.color = libtcod.Color(50, 50, 150)
    self.entity = None
    self.x = x
    self.y = y

  def is_passable(self):
    return self.passable and self.entity == None

  def draw(self, con):
    char = self.char if self.entity == None else self.entity.char
    color = self.color if self.entity == None else self.entity.color
    libtcod.console_set_default_foreground(con, color)
    libtcod.console_put_char(con, self.x, self.y, char, libtcod.BKGND_NONE)


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
    self.hovered = None

  def draw(self, con):
    for pos in self.tiles:
      self.tiles[pos].draw(con)

  def tile_hovered(self, x, y):
    if self.hovered is not None: self.hovered.unhover()
    self.hovered = self.tiles[(x, y)]
    self.hovered.hover()

class Tile(object):
  def __init__(self, x, y, char = ".", passable = True):
    self.passable = passable
    self.char = char
    self.fg_color = libtcod.Color(50, 50, 150)
    self.bg_color = libtcod.black

    self.entity = None
    self.x = x
    self.y = y

  def is_passable(self):
    return self.passable and self.entity == None

  def draw(self, con):
    char = self.char if self.entity == None else self.entity.char
    color = self.fg_color if self.entity == None else self.entity.color
    libtcod.console_put_char_ex(con, self.x, self.y, char, color, self.bg_color)

  def hover(self):
    self.bg_color = libtcod.blue

  def unhover(self):
    self.bg_color = libtcod.black

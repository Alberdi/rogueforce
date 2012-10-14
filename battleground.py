import libtcodpy as libtcod

class Battleground(object):
  def __init__(self, width, height):
    self.height = height
    self.width = width
    self.effects = []
    self.minions = []
    self.generals = []
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

  def is_inside(self, x, y):
    return 0 <= x < self.width and 0 <= y < self.height

  def tile_hovered(self, x, y):
    if self.hovered is not None: self.hovered.unhover()
    self.hovered = self.tiles[(x, y)]
    self.hovered.hover()

class Tile(object):
  def __init__(self, x, y, char = ".", passable = True):
    self.passable = passable
    self.char = char
    self.color = libtcod.Color(50, 50, 150)
    self.bg_color = libtcod.black
    self.entity = None
    self.effects = []
    self.x = x
    self.y = y

  def is_passable(self, passenger):
    return self.passable and (self.entity == None or self.entity.is_ally(passenger))

  def draw(self, con):
    if len(self.effects) > 0: drawable = self.effects[-1]
    elif self.entity is not None: drawable = self.entity
    else: drawable = self
    libtcod.console_put_char_ex(con, self.x, self.y, drawable.char, drawable.color, self.bg_color)
  
  def hover(self):
    self.bg_color = libtcod.blue

  def unhover(self):
    self.bg_color = libtcod.black

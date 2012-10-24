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
    self.tiles[(-1, -1)] = Tile(-1, -1)
    self.hovered = []

  def draw(self, con):
    for pos in self.tiles:
      self.tiles[pos].draw(con)

  def hover_tiles(self, l, color=libtcod.blue):
    self.unhover_tiles()
    for t in l:
      t.hover(color)
    self.hovered = l

  def is_inside(self, x, y):
    return 0 <= x < self.width and 0 <= y < self.height

  def unhover_tiles(self):
    for t in self.hovered:
      t.unhover()

class Tile(object):
  def __init__(self, x, y, char = ".", passable = True):
    self.passable = passable
    self.char = char
    self.color = libtcod.Color(50, 50, 150)
    self.bg_original_color = libtcod.black
    self.bg_color = libtcod.black
    self.entity = None
    self.effects = []
    self.x = x
    self.y = y

  def get_char(self, x, y):
    return self.char

  def is_passable(self, passenger):
    return self.passable and (self.entity == None or self.entity.is_ally(passenger))

  def draw(self, con):
    if len(self.effects) > 0: drawable = self.effects[-1]
    elif self.entity is not None: drawable = self.entity
    else: drawable = self
    libtcod.console_put_char_ex(con, self.x, self.y, drawable.get_char(drawable.x-self.x,drawable.y-self.y), drawable.color, self.bg_color)
  
  def hover(self, color=libtcod.blue):
    self.bg_color = color

  def unhover(self):
    self.bg_color = self.bg_original_color

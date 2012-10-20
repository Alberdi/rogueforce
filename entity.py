import libtcodpy as libtcod
import cmath as math

NEUTRAL_SIDE = 555

class Entity(object):
  def __init__(self, battleground, x, y, side, char = ' ', color = libtcod.white):
    self.bg = battleground
    self.x = x
    self.y = y
    self.side = side
    self.char = char
    self.color = color
    self.original_color = color
    self.bg.tiles[(x, y)].entity = self
    self.default_next_action = 5
    self.next_action = self.default_next_action
    self.pushed = False
    self.alive = True
    self.statuses = []

  def can_be_attacked(self):
    return False
    
  def can_be_pushed(self, dx, dy):
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    return next_tile.is_passable(self) and (next_tile.entity is None or next_tile.entity.can_be_pushed(dx, dy))
    
  def can_move(self, dx, dy):
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    if not next_tile.is_passable(self): return False
    if next_tile.entity is None: return True
    if not next_tile.entity.is_ally(self): return False
    return next_tile.entity.can_be_pushed(dx, dy)
  
  def get_char(self, x, y):
    return self.char  
  
  def get_pushed(self, dx, dy):
    self.pushed = False
    self.move(dx, dy)
    self.pushed = True

  def die(self):
    self.bg.tiles[(self.x, self.y)].entity = None
    self.alive = False
    
  def is_ally(self, entity):
    return self.side == entity.side

  def move(self, dx, dy):
    if self.pushed:
      self.pushed = False
      return
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    if self.can_move(dx, dy):
      if next_tile.entity is not None:
        next_tile.entity.get_pushed(dx, dy)
      self.bg.tiles[(self.x, self.y)].entity = None
      next_tile.entity = self
      self.x += dx
      self.y += dy

  def reset_action(self):
    self.next_action = self.default_next_action

  def update(self):
    for s in self.statuses: s.update()

class Big_Entity(Entity):
  def __init__(self, battleground, x, y, side, chars = ["a", "b", "c", "d"], color = libtcod.white):
    super(Big_Entity, self).__init__(battleground, x, y, side, chars, color)
    self.chars = chars
    self.length = int(math.sqrt(len(self.chars)).real)
  
  def can_be_pushed(self, dx, dy):
    return False

  def can_move(self, dx, dy):
    for (x,y) in [(self.x+dx+x,self.y+dy+y) for x in range (0, self.length) for y in range (0, self.length)]:
      next_tile = self.bg.tiles[(x, y)]
      if not next_tile.is_passable(self): return False
      if next_tile.entity is None: continue
      if not next_tile.entity.is_ally(self): return False
      if next_tile.entity is self: continue
      if not next_tile.entity.can_be_pushed(dx, dy): return False
    return True  

  def clear_body(self):
    x = self.x
    y = self.y
    self.bg.tiles[(x, y)].entity = None
    self.bg.tiles[(x+1, y)].entity = None
    self.bg.tiles[(x, y+1)].entity = None
    self.bg.tiles[(x+1, y+1)].entity = None
    
  def die(self):
    self.clear_body()
    self.alive = False
  
  def get_char(self, dx, dy):
    return self.chars[self.length*dx + dy]
    
  def move(self, dx, dy):
    if self.pushed:
      self.pushed = False
      return
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    if self.can_move(dx, dy):
      if next_tile.entity is not None and next_tile.entity is not self:
        next_tile.entity.get_pushed(dx, dy)
      self.clear_body()
      next_tile.entity = self
      self.x += dx
      self.y += dy
      self.update_body()

  def update_body(self):
    self.bg.tiles[(self.x+1, self.y)].entity = self
    self.bg.tiles[(self.x, self.y+1)].entity = self
    self.bg.tiles[(self.x+1, self.y+1)].entity = self      
      
class Mine(Entity):
  def __init__(self, battleground, x, y, power):
    super(Mine, self).__init__(battleground, x, y, NEUTRAL_SIDE, 'X', libtcod.red)
    self.power = power

  def can_be_attacked(self):
    return True

  def get_attacked(self, attacker):
    if attacker.can_be_attacked():
      attacker.get_attacked(self)
      self.bg.tiles[(self.x, self.y)].entity = None
      

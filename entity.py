import libtcodpy as libtcod
import cmath as math

NEUTRAL_SIDE = 555

class Entity(object):
  def __init__(self, battleground, x=-1, y=-1, side=NEUTRAL_SIDE, char=' ', color=libtcod.white):
    self.bg = battleground
    self.x = x
    self.y = y
    self.side = side
    self.char = char
    self.original_char = char
    self.color = color
    self.original_color = color
    self.bg.tiles[(x, y)].entity = self
    self.default_next_action = 5
    self.next_action = self.default_next_action
    self.pushed = False
    self.alive = True
    self.statuses = []
    self.path = []

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

  def change_battleground(self, bg, x, y):
    self.bg.tiles[(self.x, self.y)].entity = None
    self.bg = bg
    (self.x, self.y) = (x, y)
    self.bg.tiles[(self.x, self.y)].entity = self

  def clone(self, x, y): 
    if self.bg.is_inside(x, y) and self.bg.tiles[(x, y)].entity is None and self.bg.tiles[(x, y)].is_passable(self):
      return self.__class__(self.bg, x, y, self.side, self.char, self.original_color)
    return None

  def die(self):
    self.bg.tiles[(self.x, self.y)].entity = None
    self.alive = False
  
  def get_char(self, x, y):
    return self.char  

  def get_passable_neighbours(self):
    neighbours = [(self.x+i, self.y+j) for i in range(-1,2) for j in range(-1,2)] 
    return filter(lambda t: self.bg.tiles[t].passable and t != (self.x, self.y), neighbours)

  def get_pushed(self, dx, dy):
    self.pushed = False
    self.move(dx, dy)
    self.pushed = True
   
  def is_ally(self, entity):
    return self.side == entity.side

  def move(self, dx, dy):
    if self.pushed:
      self.pushed = False
      return False
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    if self.can_move(dx, dy):
      if next_tile.entity is not None:
        next_tile.entity.get_pushed(dx, dy)
      self.bg.tiles[(self.x, self.y)].entity = None
      next_tile.entity = self
      self.x += dx
      self.y += dy
      return True
    return False

  def move_path(self):
    if self.path:
      next_tile = self.path.pop(0)
      if self.move(next_tile.x - self.x, next_tile.y - self.y):
        return True
      else:
        self.path.insert(0, next_tile)
    return False

  def reset_action(self):
    self.next_action = self.default_next_action

  def teleport(self, x, y):
    if self.bg.tiles[(x, y)].entity is None:
      self.bg.tiles[(x, y)].entity = self
      self.bg.tiles[(self.x, self.y)].entity = None
      (self.x, self.y) = (x, y)
      return True
    return False

  def update(self):
    for s in self.statuses:
      s.update()

class BigEntity(Entity):
  def __init__(self, battleground, x, y, side, chars=["a", "b", "c", "d"], colors=[libtcod.white]*4):
    super(BigEntity, self).__init__(battleground, x, y, side, chars[0], colors[0])
    self.chars = chars
    self.colors = colors
    self.length = int(math.sqrt(len(self.chars)).real)
    self.update_body()
  
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
    for i in range(self.length):
      for j in range(self.length):
        self.bg.tiles[(self.x+i, self.y+j)].entity = None
    
  def die(self):
    self.clear_body()
    self.alive = False
  
  def get_char(self, dx, dy):
    self.color = self.colors[self.length*dx+dy]
    return self.chars[self.length*dx+dy]
    
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
    for i in range(self.length):
      for j in range(self.length):
        self.bg.tiles[(self.x+i, self.y+j)].entity = self
      
class Fortress(BigEntity):
  def __init__(self, battleground, x, y, side=NEUTRAL_SIDE, chars=[':']*4, colors=[libtcod.white]*4, requisition_production=1):
    super(Fortress, self).__init__(battleground, x, y, side, chars, colors)
    self.capacity = len(chars)
    self.connected_fortresses = []
    self.guests = []
    self.requisition_production = requisition_production

  def can_be_attacked(self):
    return True

  def can_host(self, entity):
    return self.side == entity.side or self.side == NEUTRAL_SIDE

  def can_move(self, dx, dy):
    return False

  def get_connections(self):
    # Gather all tiles inside and surrounding the fortress
    starting_tiles = [(self.x+i, self.y+j) for i in range(-1,3) for j in range(-1,3)] 
    # Remove those inside it
    checked = [(self.x+i, self.y+j) for i in range(0,2) for j in range(0,2)]
    starting_tiles = filter(lambda t: self.bg.tiles[t].passable and t not in checked, starting_tiles)
    # Try every reachable tile from the fortress and save the connections
    for starting in starting_tiles:
      tiles = [starting]
      while tiles:
        (x, y) = tiles.pop()
        checked.append((x, y))
        for t in [(x+i, y+j) for i in range(-1,2) for j in range(-1,2)]:
          entity = self.bg.tiles[t].entity
          if entity in self.bg.fortresses and entity is not self and entity not in self.connected_fortresses:
            self.connected_fortresses.append((entity, starting))
          if self.bg.tiles[t].passable and t not in checked:
            tiles.append(t)

  def host(self, entity):
    if not self.can_host(entity) or len(self.guests) >= self.capacity: return
    if not self.guests:
      self.side = entity.side
    self.bg.tiles[(entity.x, entity.y)].entity = None
    (entity.x, entity.y) = (self.x, self.y)
    self.bg.generals.remove(entity)
    self.chars[len(self.guests)] = entity.char
    self.colors[len(self.guests)] = entity.color
    self.guests.append(entity)
    self.update_body()

  def refresh_chars(self):
    self.chars = [':']*len(self.chars)
    self.colors = [libtcod.white]*len(self.colors)
    for i in range(len(self.guests)):
      self.chars[i] = self.guests[i].char
      self.colors[i] = self.guests[i].color

  def unhost(self, entity):
    self.guests.remove(entity)
    self.bg.generals.append(entity)
    self.refresh_chars()
    if not self.guests:
      self.side = NEUTRAL_SIDE

class Mine(Entity):
  def __init__(self, battleground, x=-1, y=-1, power=50):
    super(Mine, self).__init__(battleground, x, y, NEUTRAL_SIDE, 'X', libtcod.red)
    self.power = power

  def can_be_attacked(self):
    return True

  def clone(self, x, y):
    if self.bg.is_inside(x, y) and self.bg.tiles[(x, y)].entity is None and self.bg.tiles[(x, y)].is_passable(self):
      return self.__class__(self.bg, x, y, self.power)
    return None

  def get_attacked(self, attacker):
    if attacker.can_be_attacked():
      attacker.get_attacked(self)
    self.die()
      

import libtcodpy as libtcod

NEUTRAL_SIDE = 555

class Entity(object):
  def __init__(self, battleground, x, y, side, char = ' ', color = libtcod.white):
    self.bg = battleground
    self.x = x
    self.y = y
    self.side = side
    self.char = char
    self.color = color
    self.bg.tiles[(x, y)].entity = self
    self.default_next_action = 5
    self.next_action = self.default_next_action
    self.pushed = False
    self.alive = True

  def can_be_attacked(self):
    return False

  def move(self, dx, dy):
    if self.pushed:
      self.pushed = False
      return
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    if next_tile.is_passable(self):
      if next_tile.entity is not None and next_tile.entity.is_ally(self):
        if not next_tile.entity.can_be_pushed(dx, dy): return
        next_tile.entity.get_pushed(dx, dy)
      self.bg.tiles[(self.x, self.y)].entity = None
      next_tile.entity = self
      self.x += dx
      self.y += dy

  def can_be_pushed(self, dx, dy):
    next_tile = self.bg.tiles[(self.x+dx, self.y+dy)]
    return next_tile.is_passable(self) and (next_tile.entity is None or next_tile.entity.can_be_pushed(dx, dy))

  def get_pushed(self, dx, dy):
    self.move(dx, dy)
    self.pushed = True

  def is_ally(self, entity):
    return self.side == entity.side

  def reset_action(self):
    self.next_action = self.default_next_action

  def update(self):
    pass

class Effect(Entity):
  def __init__(self, battleground, x, y, side, char = ' ', color = libtcod.white):
    saved = battleground.tiles[(x, y)].entity
    super(Effect, self).__init__(battleground, x, y, side, char, color)
    self.bg.tiles[(x, y)].entity = saved
    self.bg.tiles[(x, y)].effects.append(self)

  def can_be_pushed(self, dx, dy):
    return False

  def dissapear(self):
    self.bg.tiles[(self.x, self.y)].effects.remove(self)
    self.alive = False

  def move(self, dx, dy):
    self.bg.tiles[(self.x, self.y)].effects.remove(self)
    self.x += dx
    self.y += dy
    self.bg.tiles[(self.x, self.y)].effects.append(self)

class Mine(Entity):
  def __init__(self, battleground, x, y):
    super(Mine, self).__init__(battleground, x, y, NEUTRAL_SIDE, 'X', libtcod.red)
    self.power = 50

  def can_be_attacked(self):
    return True

  def get_attacked(self, attacker):
    if attacker.can_be_attacked():
      attacker.get_attacked(self)
      self.bg.tiles[(self.x, self.y)].entity = None

class Arrow(Effect):
  def __init__(self, battleground, x, y, side, power):
    super(Arrow, self).__init__(battleground, x, y, side, '>' if side == 0 else '<', libtcod.light_red)
    self.power = power
    self.do_attack()

  def do_attack(self):
    entity = self.bg.tiles[(self.x, self.y)].entity
    if entity is not None and entity.can_be_attacked():
      if not entity.is_ally(self): entity.get_attacked(self)
      self.dissapear()

  def update(self):
    #TODO This is too ugly :/
    if not self.alive: return
    if self.x >= self.bg.width-1 or self.x <= 0:
      self.dissapear()
    self.do_attack()
    if not self.alive: return
    self.move(1 if self.side == 0 else -1, 0)
    self.do_attack()

class Wave(Effect):
  def __init__(self, battleground, x, y, side):
    super(Wave, self).__init__(battleground, x, y, side, '~', libtcod.light_blue)
    self.power = 10
    self.entities_attacked = []
    self.do_attack()
 
  def do_attack(self):
    entity = self.bg.tiles[(self.x, self.y)].entity
    if entity is not None and entity not in self.entities_attacked and entity.can_be_attacked():
      entity.get_attacked(self)
      self.entities_attacked.append(entity)

  def update(self):
    if not self.alive: return
    if self.x >= self.bg.width-1 or self.x <= 0:
      self.dissapear()
      return
    self.do_attack()
    self.move(1 if self.side == 0 else -1, 0)
    self.do_attack()

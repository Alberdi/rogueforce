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

  def die(self):
    self.bg.tiles[(self.x, self.y)].entity = None
    self.alive = False

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
    self.pushed = False
    self.move(dx, dy)
    self.pushed = True

  def is_ally(self, entity):
    return self.side == entity.side

  def reset_action(self):
    self.next_action = self.default_next_action

  def update(self):
    pass

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
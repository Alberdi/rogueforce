import entity

import libtcodpy as libtcod

class Effect(entity.Entity):
  def __init__(self, battleground, x, y, side = entity.NEUTRAL_SIDE, char = ' ', color = libtcod.white):
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

class Arrow(Effect):
  def __init__(self, battleground, x, y, side, power, attack_effects = ['>', '<']):
    super(Arrow, self).__init__(battleground, x, y, side, attack_effects[side], libtcod.light_red)
    self.power = power
    self.do_attack()

  def do_attack(self):
    entity = self.bg.tiles[(self.x, self.y)].entity
    if entity is not None and entity.can_be_attacked():
      if not entity.is_ally(self): entity.get_attacked(self)
      self.dissapear()

  def update(self):
    if not self.alive: return
    if not self.bg.is_inside(self.x + (1 if self.side == 0 else -1), self.y):
      self.dissapear()
    self.do_attack()
    if not self.alive: return
    self.move(1 if self.side == 0 else -1, 0)
    self.do_attack()

class Darkness(Effect):
  def __init__(self, battleground, x, y, duration):
    super(Darkness, self).__init__(battleground, x, y, entity.NEUTRAL_SIDE, ' ')
    self.duration = duration

  def update(self):
    if not self.alive: return
    self.duration -= 1
    if self.duration <= 0: self.dissapear()

class Wave(Effect):
  def __init__(self, battleground, x, y, side, power):
    super(Wave, self).__init__(battleground, x, y, side, '~', libtcod.light_blue)
    self.power = power
    self.entities_attacked = []
    self.do_attack()
 
  def do_attack(self):
    entity = self.bg.tiles[(self.x, self.y)].entity
    if entity is not None and entity not in self.entities_attacked and entity.can_be_attacked():
      entity.get_attacked(self)
      self.entities_attacked.append(entity)

  def update(self):
    if not self.alive: return
    if not self.bg.is_inside(self.x + (1 if self.side == 0 else -1), self.y):
      self.dissapear()
      return
    self.do_attack()
    self.move(1 if self.side == 0 else -1, 0)
    self.do_attack()

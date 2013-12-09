import tactic

import libtcodpy as libtcod

class Status(object):
  def __init__(self, entity, duration=9999, name="Status"):
    self.duration = duration
    self.entity = entity
    self.name = name
    self.attack_effect = None
    self.attack_type = "magical"
    self.owner = None
    if entity: # Not a prototype
      for s in self.entity.statuses:
        if s.name == self.name:
          # We refresh the duration if it's bigger
          s.duration = max(s.duration, self.duration)
          return
      self.entity.statuses.append(self)
  
  def clone(self, entity):
    return self.__class__(entity, self.duration, self.name)

  def end(self):
    self.duration = -1
    self.entity.statuses.remove(self)

  def tick(self):
    pass

  def update(self):
    if self.duration > 0:
      self.duration -= 1
      self.tick()
      if self.duration <= 0:
        self.end()

class Blind(Status):
  def __init__(self, entity, duration=9999, name="Blindness"):
    super(Blind, self).__init__(entity, duration, name)
    self.saved_power = 0
    if entity != None:
      (self.saved_power, entity.power) = (entity.power, self.saved_power)

  def end(self):
    self.entity.power = self.saved_power
    super(Blind, self).end()

class FreezeCooldowns(Status):
  def __init__(self, entity, duration=9999, name="Freeze cooldowns"):
    super(FreezeCooldowns, self).__init__(entity, duration, name)

  def tick(self):
    for s in self.entity.skills:
      s.change_cd(-1)

class Haste(Status):
  def __init__(self, entity, duration=9999, name="Haste", speedup=0):
    super(Haste, self).__init__(entity, duration, name)
    self.speedup = speedup

  def tick(self):
    self.entity.next_action -= 1

class Poison(Status):
  # tbt = time between ticks
  def __init__(self, entity, power, tbt=0, ticks=9999, name="Poison"):
    # Duration is not exact, it lasts a few more updates, but that shouldn't be a problem.
    super(Poison, self).__init__(entity, ticks*(tbt+1), name)
    self.tbt = tbt
    self.ticks = ticks
    self.power = power
    self.timer = 0

  def clone(self, entity):
    return self.__class__(entity, self.power, self.tbt, self.ticks, self.name)

  def tick(self):
    self.timer -= 1
    if self.timer < 0:
      self.entity.get_attacked(self)
      self.timer = self.tbt
      #self.ticks -= 1
      #if self.ticks == 0: self.duration = -1 # end

class PoisonHunger(Poison):
  def __init__(self, entity, power, tbt=0, ticks=9999, name="PoisonHunger"):
    super(PoisonHunger, self).__init__(entity, power, tbt, ticks, name)
    if entity:
      self.entity_kills = entity.kills

  def tick(self):
    if not self.entity.alive or self.entity.kills > self.entity_kills:
      self.duration = -1
    else:
      self.entity.next_action += 1
      self.owner.next_action -= 1
      super(PoisonHunger, self).tick()

class Recalling(Status):
  def __init__(self, entity, duration=9999, name="Recalling"):
    super(Recalling, self).__init__(entity, duration, name)
    self.color = self.entity.color

  def update(self):
    super(Recalling, self).update()
    if self.duration > 0:
      self.entity.next_action = 100
      tile = self.entity.bg.tiles[(self.entity.x, self.entity.y)]
      self.entity.color = libtcod.color_lerp(tile.bg_color, self.color, 1-(self.duration/10.0))

  def end(self):
    super(Recalling, self).end()
    self.entity.update_color()
    self.entity.reset_action()

class Shield(Status):
  def __init__(self, entity, duration=9999, name="Shield", armor=0, armor_type="physical"):
    super(Shield, self).__init__(entity, duration, name)
    self.armor = armor
    self.armor_type = armor_type
    if entity:
      entity.armor[armor_type] += armor
      entity.color = libtcod.dark_yellow

  def clone(self, entity):
    return self.__class__(entity, self.duration, self.name, self.armor, self.armor_type)

  def end(self):
    super(Shield, self).end()
    self.entity.update_color()
    self.entity.armor[self.armor_type] -= self.armor

class Taunted(Status):
  def __init__(self, entity, taunter, armor=0, duration=9999, name="Taunted"):
    super(Taunted, self).__init__(entity, duration, name)
    self.taunter = taunter
    self.armor = armor
    shield_name = name + " shield"
    if entity:
      for s in taunter.statuses:
        if s.name == shield_name:
          return
      Shield(taunter, duration, shield_name, armor)

  def clone(self, entity):
    return self.__class__(entity, self.taunter, self.armor, self.duration, self.name)

  def end(self):
    super(Taunted, self).end()
    if self.entity in self.entity.bg.minions:
      self.entity.bg.generals[self.entity.side].recommand_tactic()

  def update(self):
    super(Taunted, self).update()
    if self.entity in self.entity.bg.generals:
      self.entity.place_flag(self.taunter.x, self.taunter.y)
    elif self.entity in self.entity.bg.minions:
      self.entity.tactic = tactic.attack_general

class Vanished(Status):
  def __init__(self, entity, duration=9999, name="Vanished"):
    super(Vanished, self).__init__(entity, duration, name)
    if entity:
      (self.x, self.y) = (entity.x, entity.y)
      entity.bg.tiles[(entity.x, entity.y)].entity = None
      (entity.x, entity.y) = (-1, -1)
      entity.next_action = 100

  def update(self):
    super(Vanished, self).update()
    self.entity.next_action = 100

  def end(self):
    super(Vanished, self).end()
    if self.entity.teleport(self.x, self.y):
      self.entity.reset_action()
    else:
      self.entity.die()

class Vanishing(Status):
  def __init__(self, entity, duration=9999, vanished_duration=9999, name="Vanishing"):
    super(Vanishing, self).__init__(entity, duration, name)
    self.vanished_duration = vanished_duration

  def clone(self, entity):
    return self.__class__(entity, self.duration, self.vanished_duration, self.name)

  def update(self):
    super(Vanishing, self).update()
    if self.duration > 0:
      self.entity.next_action = 100
      tile = self.entity.bg.tiles[(self.entity.x, self.entity.y)]
      self.entity.color = libtcod.color_lerp(self.entity.color, tile.bg_color, 1-(self.duration/10.0))

  def end(self):
    super(Vanishing, self).end()
    self.entity.update_color()
    self.entity.reset_action()
    Vanished(self.entity, self.vanished_duration)

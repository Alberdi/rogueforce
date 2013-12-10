import effect
import skill
import tactic

import libtcodpy as libtcod

class Status(object):
  def __init__(self, entity=None, owner=None, duration=9999, name="Status"):
    self.entity = entity
    self.owner = owner
    self.duration = duration
    self.name = name
    self.attack_effect = None
    self.attack_type = "magical"
    self.kills = 0
    self.duplicated = False
    if entity: # Not a prototype
      for s in self.entity.statuses:
        if s.name == self.name:
          # We refresh the duration if it's bigger
          s.duration = max(s.duration, self.duration)
          self.duplicated = True
          return
      self.entity.statuses.append(self)
  
  def clone(self, entity):
    return self.__class__(entity, self.owner, self.duration, self.name)

  def end(self):
    self.duration = -1
    self.entity.statuses.remove(self)

  def register_kill(self, killed):
    self.kills += 1
    if self.owner:
      self.owner.kills += 1

  def tick(self):
    pass

  def update(self):
    if self.duration > 0:
      self.duration -= 1
      self.tick()
      if self.duration <= 0:
        self.end()

class Bleeding(Status):
  def __init__(self, entity=None, owner=None, power=0, duration=9999, name="Bleeding"):
    super(Bleeding, self).__init__(entity, owner, duration, name)
    self.power = power
    if entity:
      (self.last_x, self.last_y) = (entity.x, entity.y)

  def clone(self, entity):
    return self.__class__(entity, self.owner, self.power, self.duration, self.name)

  def tick(self):
    if (self.last_x, self.last_y) != (self.entity.x, self.entity.y):
      diff = max(abs(self.last_x - self.entity.x), abs(self.last_y - self.entity.y))
      self.entity.get_attacked(self.owner, diff*self.power, None, "magical")
      effect.TempEffect(self.entity.bg, self.entity.side, self.last_x, self.last_y, '*', libtcod.darker_red)
      (self.last_x, self.last_y) = (self.entity.x, self.entity.y)

class Blind(Status):
  def __init__(self, entity=None, duration=9999, name="Blindness"):
    super(Blind, self).__init__(entity, None, duration, name)
    self.saved_power = 0
    if entity != None:
      (self.saved_power, entity.power) = (entity.power, self.saved_power)

  def end(self):
    self.entity.power = self.saved_power
    super(Blind, self).end()

class Empower(Status):
  def __init__(self, entity=None, owner=None, duration=9999, name="Empower", power_ratio=0):
    super(Empower, self).__init__(entity, owner, duration, name)
    self.power_ratio = power_ratio
    if entity:
      self.bonus_power = int(entity.power * power_ratio)
      entity.power += self.bonus_power

  def clone(self, entity):
    return self.__class__(entity, self.owner, self.duration, self.name, self.power_ratio)

  def end(self):
    super(Empower, self).end()
    self.entity.power -= self.bonus_power

class FreezeCooldowns(Status):
  def __init__(self, entity=None, owner=None, duration=9999, name="Freeze cooldowns"):
    super(FreezeCooldowns, self).__init__(entity, owner, duration, name)
    if self.entity and self.entity not in entity.bg.generals:
      self.end()

  def tick(self):
    for s in self.entity.skills:
      s.change_cd(-1)

class Haste(Status):
  def __init__(self, entity=None, duration=9999, name="Haste", speedup=0):
    super(Haste, self).__init__(entity, None, duration, name)
    self.speedup = speedup

  def clone(self, entity):
    return self.__class__(entity, self.duration, self.name, self.speedup)

  def tick(self):
    self.entity.next_action -= self.speedup

class Lifted(Status):
  def __init__(self, entity=None, owner=None, duration=9999, name="Lifted", land_area=None, land_status=None):
    super(Lifted, self).__init__(entity, owner, duration, name)
    self.land_area = land_area
    self.land_status = land_status
    self.skill = skill.Skill(owner, skill.apply_status, 0, [land_status], area=land_area)
    if entity:
      effect.TempEffect(entity.bg, x=entity.x, y=entity.y, char='^', color=owner.color, duration=duration)

  def clone(self, entity):
    return self.__class__(entity, self.owner, self.duration, self.name, self.land_area, self.land_status)

  def tick(self):
    self.entity.reset_action()
  
  def end(self):
    if self.land_status:
      self.skill.use(self.entity.x, self.entity.y)
      for t in self.land_area.get_tiles():
        effect.TempEffect(self.entity.bg, x=t.x, y=t.y, char=',')

class Poison(Status):
  # tbt = time between ticks
  def __init__(self, entity=None, owner=None, power=0, tbt=0, ticks=9999, name="Poison"):
    # Duration is not exact, it lasts a few more updates, but that shouldn't be a problem.
    super(Poison, self).__init__(entity, owner, ticks*(tbt+1), name)
    self.tbt = tbt
    self.ticks = ticks
    self.power = power
    self.timer = 0

  def clone(self, entity):
    return self.__class__(entity, self.owner, self.power, self.tbt, self.ticks, self.name)

  def tick(self):
    self.timer -= 1
    if self.timer < 0:
      self.entity.get_attacked(self)
      self.timer = self.tbt

class PoisonHunger(Poison):
  def __init__(self, entity=None, owner=None, power=0, tbt=0, ticks=9999, name="PoisonHunger"):
    super(PoisonHunger, self).__init__(entity, owner, power, tbt, ticks, name)
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
  def __init__(self, entity=None, duration=9999, name="Recalling"):
    super(Recalling, self).__init__(entity, None, duration, name)
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
  def __init__(self, entity=None, duration=9999, name="Shield", armor=0, armor_type="physical"):
    super(Shield, self).__init__(entity, None, duration, name)
    self.armor = armor
    self.armor_type = armor_type
    if entity and not self.duplicated:
      entity.armor[armor_type] += armor
      entity.color = libtcod.dark_yellow

  def clone(self, entity):
    return self.__class__(entity, self.duration, self.name, self.armor, self.armor_type)

  def end(self):
    super(Shield, self).end()
    self.entity.update_color()
    self.entity.armor[self.armor_type] -= self.armor

class Stunned(Status):
  def __init__(self, entity=None, owner=None, duration=9999, name="Stunned"):
    super(Stunned, self).__init__(entity, owner, duration, name)
    if entity:
      self.effect = effect.Blinking(entity.bg, x=entity.x, y=entity.y, char='~', color=entity.color)

  def end(self):
    self.effect.dissapear()

  def tick(self):
    self.entity.reset_action()

class Taunted(Status):
  def __init__(self, entity=None, owner=None, duration=9999, name="Taunted"):
    super(Taunted, self).__init__(entity, owner, duration, name)

  def tick(self):
    if self.entity in self.entity.bg.generals:
      self.entity.place_flag(self.owner.x, self.owner.y)
    elif self.entity in self.entity.bg.minions:
      self.entity.tactic = tactic.attack_general

class Vanished(Status):
  def __init__(self, entity=None, duration=9999, name="Vanished"):
    super(Vanished, self).__init__(entity, None, duration, name)
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
  def __init__(self, entity=None, duration=9999, vanished_duration=9999, name="Vanishing"):
    super(Vanishing, self).__init__(entity, None, duration, name)
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

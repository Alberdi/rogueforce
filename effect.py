import entity
import status

from math import copysign

import libtcodpy as libtcod

class Effect(entity.Entity):
  def __init__(self, battleground, x=-1, y=-1, side=entity.NEUTRAL_SIDE, char=' ', color=libtcod.white):
    saved = battleground.tiles[(x, y)].entity
    super(Effect, self).__init__(battleground, x, y, side, char, color)
    self.bg.tiles[(x, y)].entity = saved
    self.bg.tiles[(x, y)].effects.append(self)
    if x != -1:
      self.bg.effects.append(self)

  def can_be_pushed(self, dx, dy):
    return False

  def clone(self, x, y): 
    if self.bg.is_inside(x, y):
      return self.__class__(self.bg, x, y, self.side, self.char, self.original_color)
    return None

  def dissapear(self):
    self.bg.tiles[(self.x, self.y)].effects.remove(self)
    self.alive = False

  def do_attack(self, dissapear=False):
    entity = self.bg.tiles[(self.x, self.y)].entity
    if entity is not None and entity.can_be_attacked():
      if not entity.is_ally(self): entity.get_attacked(self)
      if dissapear:
        self.dissapear()

  def move(self, dx, dy):
    self.bg.tiles[(self.x, self.y)].effects.remove(self)
    self.x += dx
    self.y += dy
    self.bg.tiles[(self.x, self.y)].effects.append(self)
    return True

  def teleport(self, x, y):
    self.bg.tiles[(self.x, self.y)].effects.remove(self)
    self.x = x
    self.y = y
    self.bg.tiles[(self.x, self.y)].effects.append(self)
    return True


class Arrow(Effect):
  def __init__(self, battleground, x, y, side, power, attack_effects = ['>', '<']):
    super(Arrow, self).__init__(battleground, x, y, side, attack_effects[side], libtcod.light_red)
    self.power = power
    self.do_attack()

  def update(self):
    if not self.alive: return
    if not self.bg.is_inside(self.x + (1 if self.side == 0 else -1), self.y):
      self.dissapear()
    self.do_attack(True)
    if not self.alive: return
    self.move(1 if self.side == 0 else -1, 0)
    self.do_attack(True)

class Blinking(Effect):
  def __init__(self, battleground, x=-1, y=-1, side=entity.NEUTRAL_SIDE, char=' ', color=libtcod.white):
    super(Blinking, self).__init__(battleground, x, y, side, char, color)
    self.visible = True

  def dissapear(self):
    if self.visible:
      self.bg.tiles[(self.x, self.y)].effects.remove(self)
    self.alive = False

  def update(self):
    if not self.alive:
      return
    if self.next_action <= 0:
      self.reset_action()
      if self.visible:
        self.bg.tiles[(self.x, self.y)].effects.remove(self)
      else:
        self.bg.tiles[(self.x, self.y)].effects.append(self)
      self.visible = not self.visible
    else:
      self.next_action -= 1

class Boulder(Effect):
  def __init__(self, battleground, x=-1, y=-1, side=entity.NEUTRAL_SIDE, char='O', color=libtcod.white, power=10, delay=0, delta_power=-2):
    super(Boulder, self).__init__(battleground, x, y, side, char, color)
    self.power = power
    self.delta_power = delta_power
    self.delay = delay

  def clone(self, x, y): 
    if self.bg.is_inside(x, y):
      return self.__class__(self.bg, x, y, self.side, self.char, self.original_color, self.power, self.delay, self.delta_power)
    return None

  def update(self):
    if not self.alive:
      return
    self.move_path()
    if self.delay > 0:
      self.delay -= 1
      if self.delay == 0:
        self.char = self.char.lower()
      return
    entity = self.bg.tiles[(self.x, self.y)].entity
    if entity:
      entity.get_attacked(self)
      #self.dissapear()
      #return
    self.power += self.delta_power
    if not self.path or self.power == 0:
      self.dissapear()
      return

class Darkness(Effect):
  def __init__(self, battleground, x, y, duration):
    super(Darkness, self).__init__(battleground, x, y, entity.NEUTRAL_SIDE, ' ')
    self.duration = duration

  def update(self):
    if not self.alive: return
    self.duration -= 1
    if self.duration <= 0: self.dissapear()

class Explosion(Effect):
  def __init__(self, battleground, x=-1, y=-1, side=entity.NEUTRAL_SIDE, char='*', color=libtcod.lighter_red, power=10):
    super(Explosion, self).__init__(battleground, x, y, side, char, color)
    self.power = power

  def clone(self, x, y): 
    if self.bg.is_inside(x, y):
      return self.__class__(self.bg, x, y, self.side, self.char, self.original_color, self.power)
    return None

  def update(self):
    #TODO: generalize it to work with any starting color
    if not self.alive: return
    if self.color == libtcod.lighter_red:
      self.color = libtcod.light_red
    elif self.color == libtcod.light_red:
      self.color = libtcod.red
    else:
      self.do_attack()
      self.dissapear()

class Lava(Effect):
  def __init__(self, battleground, x=-1, y=-1, side=entity.NEUTRAL_SIDE, char=None, color=libtcod.red, power=5, duration=10):
    super(Lava, self).__init__(battleground, x, y, side, char, color)
    self.power = power
    self.original_duration = duration
    self.duration = duration
    self.bg.tiles[(self.x, self.y)].hover(color)
    self.burning_status =  status.Poison(None, power=1, tbt=2, ticks=1, name="Burnt")
    entity = self.bg.tiles[(self.x, self.y)].entity
    if entity:
      entity.get_attacked(self)

  def clone(self, x, y): 
    if self.bg.is_inside(x, y):
      return self.__class__(self.bg, x, y, self.side, self.char, self.original_color, self.power, self.original_duration)
    return None

  def update(self):
    if not self.alive:
      return
    if self.duration == 0:
      self.bg.tiles[(self.x, self.y)].unhover()
      self.dissapear()
    if self.path:
      tile = self.path.pop(0)
      self.clone(tile.x, tile.y)
    entity = self.bg.tiles[(self.x, self.y)].entity
    if entity:
      self.burning_status.clone(entity)
    self.duration -= 1

class Pathing(Effect):
  def __init__(self, battleground, x=-1, y=-1, side=entity.NEUTRAL_SIDE, char=' ', color=libtcod.white):
    super(Pathing, self).__init__(battleground, x, y, side, char, color)

  def update(self):
    if not self.alive:
      return
    self.move_path()

class Slash(Effect):
  def __init__(self, battleground, x=-1, y=-1, side=entity.NEUTRAL_SIDE, char='|', color=libtcod.white, power=10, steps=8, goto=1, area=None):
    super(Slash, self).__init__(battleground, x, y, side, color)
    self.general = self.bg.generals[side]
    self.max_steps = steps
    self.step = 0;
    self.power = power
    self.center_x = x
    self.center_y = y
    self.direction = 0; 
    self.chars = ['|', '\\', '-', '/']
    self.goto = goto
    self.directions = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]

  def clone(self, x, y):
    if self.bg.is_inside(x, y):
      return self.__class__(self.bg, self.general.x, self.general.y, self.side, self.char, self.original_color, self.power, self.max_steps, self.goto)
    return None

  def update(self):
    if not self.alive:
      return
    if abs(self.step) >= self.max_steps:
      self.dissapear()
      return
    self.char = self.chars[(self.step+self.direction)%4]
    self.teleport(self.general.x, self.general.y)
    self.move(*self.directions[(self.step+self.direction)%8])
    self.step += int(copysign(1, self.goto))
    self.do_attack()

class Thunder(Effect):
  def __init__(self, battleground, x=-1, y=-1, side=entity.NEUTRAL_SIDE, char='|', color=libtcod.lighter_red, power=30, area=None):
    self.target_y = y
    self.power = power
    self.area = area
    if x != -1:
      y = y-5 if y-5 >= 0 else 0
    super(Thunder, self).__init__(battleground, x, y, side, char, color)

  def clone(self, x, y): 
    if self.bg.is_inside(x, y):
      return self.__class__(self.bg, x, y, self.side, self.char, self.original_color, self.power, self.area)
    return None

  def update(self):
    #TODO: generalize it to work with any starting color
    if not self.alive: return
    if self.color == libtcod.lighter_red:
      self.color = libtcod.light_red
    elif self.color == libtcod.light_red:
      self.color = libtcod.red
    elif self.y != self.target_y:
      self.move(0, 1)
      self.color = libtcod.lighter_red
    else:
      self.dissapear()
      e = Explosion(self.bg, self.x, self.y, self.side, '*', libtcod.lighter_red, self.power)
      if self.area:
        for t in self.area.get_tiles(self.x, self.y):
          if (t.x, t.y) != (e.x, e.y):
            e.clone(t.x, t.y)

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

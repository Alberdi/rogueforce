from entity import Entity
from entity import BigEntity
import libtcodpy as libtcod

import effect
import tactic

from collections import defaultdict

class Minion(Entity):
  def __init__(self, battleground, side, x=-1, y=-1, name="minion", color=libtcod.white):
    super(Minion, self).__init__(battleground, side, x, y, name[0], color)
    self.name = name
    self.max_hp = 20
    self.hp = 20
    self.armor = defaultdict(lambda: 0)
    self.power = 5
    self.tactic = tactic.null
    self.attack_effect = effect.TempEffect(self.bg, char='/' if side else '\\')

  def can_be_attacked(self):
    return True

  def clone(self, x, y):
    if self.bg.is_inside(x, y) and self.bg.tiles[(x, y)].entity is None and self.bg.tiles[(x, y)].is_passable(self):
      return self.__class__(self.bg, self.side, x, y, self.name, self.original_color)
    return None

  def die(self):
    super(Minion, self).die()
    if self in self.bg.minions:
      self.bg.generals[self.side].minions_alive -= 1

  def enemy_reachable(self, diagonals=False):
    # Order: forward, backward, up, down, then diagonals
    order = [(1, 0), (-1, 0), (0, -1), (0, 1)]
    if diagonals:
      order.extend([(1, -1), (1, 1), (-1, -1), (-1, 1)])
    for (i, j) in order:
      enemy = self.bg.tiles[(self.x + (-i if self.side else i), self.y + j)].entity
      if enemy and not self.is_ally(enemy) and enemy.can_be_attacked():
        return enemy
    return None
 
  def follow_tactic(self):
    self.tactic(self)

  def get_attacked(self, enemy, power=None, attack_effect=None, attack_type=None):
    if not power:
      power = enemy.power
    if not attack_effect:
      attack_effect = enemy.attack_effect
    if not attack_type:
      attack_type = enemy.attack_type
    self.hp -= max(0, power - self.armor[attack_type])
    if attack_effect:
      attack_effect.clone(self.x, self.y)
    if self.hp > 0:
      self.update_color()
    else:
      self.hp = 0
      self.die()
      if enemy.owner:
        enemy.owner.kills += 1
      else:
        enemy.kills += 1

  def get_healed(self, amount):
    self.hp += amount
    if self.hp > self.max_hp: self.hp = self.max_hp
    self.update_color()

  def try_attack(self):
    enemy = self.enemy_reachable()
    if enemy:
      enemy.get_attacked(self)
    return enemy != None
    
  def update(self):
    if not self.alive: return
    for s in self.statuses:
      s.update()
    if self.next_action <= 0:
      self.reset_action()
      if not self.try_attack():
        self.follow_tactic()
    else: self.next_action -= 1

  def update_color(self):
    # We change the color to indicate that the minion is wounded
    # More red -> closer to death
    c = int(255*(float(self.hp)/self.max_hp))
    self.color = libtcod.Color(255, c, c)

class BigMinion(BigEntity, Minion):
  def __init__(self, battleground, side, x=-1, y=-1, name="Giant", chars=['G']*4, colors=[libtcod.white]*4):
    BigEntity.__init__(self, battleground, side, x, y, chars, colors)
    Minion.__init__(self, battleground, side, x, y, name, colors[0])
    self.max_hp *= self.length
    self.hp = self.max_hp
    
  def clone(self, x, y):
    for (pos_x, pos_y) in [(x+i, y+j) for i in range (0, self.length) for j in range (0, self.length)]:
      if not self.bg.is_inside(pos_x, pos_y) or self.bg.tiles[(pos_x, pos_y)].entity is not None or not self.bg.tiles[(x, y)].is_passable(self):
        return None
    entity = self.__class__(self.bg, self.side, x, y, self.name, self.color)
    entity.update_body()
    return entity

  def enemy_reachable(self):
    # Order: forward, backward, up, down
    for (dx, dy) in [(1 if self.side == 0 else -1, 0), (1 if self.side == 0 else -1, 0), (0, 1), (0, -1)]:
      for (x,y) in [(self.x+dx+x,self.y+dy+y) for x in range (0, self.length) for y in range (0, self.length)]:
        enemy = self.bg.tiles[(x, y)].entity
        if enemy is not None and not self.is_ally(enemy) and enemy.can_be_attacked():
          return enemy
    return None

class RangedMinion(Minion):
  def __init__(self, battleground, side, x=-1, y=-1, name="archer", color=libtcod.white, attack_effects = ['>', '<']):
    super(RangedMinion, self).__init__(battleground, side, x, y, name)
    self.max_hp = 10
    self.hp = 10
    self.power = 1
    self.ranged_power = 4
    self.attack_effects = attack_effects
    self.default_next_action = 10
    self.reset_action()

  def clone(self, x, y):
    if super(RangedMinion, self).clone(x, y) == None: return None
    return self.__class__(self.bg, self.side, x, y, self.name, self.original_color, self.attack_effects)

  def follow_tactic(self):
    if self.tactic is None: return
    next_x = self.x+1 if self.side == 0 else self.x-1
    if self.tactic == tactic.stop and self.bg.tiles[(next_x, self.y)].entity == None:
      self.bg.effects.append(effect.Arrow(self.bg, self.side, next_x, self.y, self.ranged_power, self.attack_effects))
    else: super(RangedMinion, self).follow_tactic()

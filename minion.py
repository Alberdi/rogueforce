from effect import Arrow
from entity import Entity
import libtcodpy as libtcod
import tactic

class Minion(Entity):
  def __init__(self, battleground, x, y, side, name, color=libtcod.white):
    super(Minion, self).__init__(battleground, x, y, side, name[0], color)
    self.name = name
    self.max_hp = 20
    self.hp = 20
    self.power = 5
    self.tactic = None

  def can_be_attacked(self):
    return True

  def clone(self, x, y):
    return self.__class__(self.bg, x, y, self.side, self.name, self.original_color)

  def enemy_reachable(self):
    # Order: forward, backward, up, down
    enemy = self.bg.tiles[(self.x + (1 if self.side == 0 else -1), self.y)].entity
    if enemy is None or self.is_ally(enemy) or not enemy.can_be_attacked():
      enemy = self.bg.tiles[(self.x + (-1 if self.side == 0 else 1), self.y)].entity
    if enemy is None or self.is_ally(enemy) or not enemy.can_be_attacked():
      enemy = self.bg.tiles[(self.x, self.y-1)].entity
    if enemy is None or self.is_ally(enemy) or not enemy.can_be_attacked():
      enemy = self.bg.tiles[(self.x, self.y+1)].entity
    if enemy != None and not self.is_ally(enemy) and enemy.can_be_attacked(): return enemy
    else: return None
 
  def follow_tactic(self):
    if self.tactic is None: return
    self.tactic(self)

  def get_attacked(self, enemy):
    self.hp -= enemy.power
    if self.hp > 0:
      self.update_color()
    else:
      self.die()

  def get_healed(self, amount):
    self.hp += amount
    if self.hp > self.max_hp: self.hp = self.max_hp
    self.update_color()

  def update(self):
    if not self.alive: return
    if self.next_action <= 0:
      self.reset_action()
      enemy = self.enemy_reachable()
      if enemy != None:
        enemy.get_attacked(self)
      else:
        self.follow_tactic()
    else: self.next_action -= 1

  def update_color(self):
    # We change the color to indicate that the minion is wounded
    # More red -> closer to death
    c = int(255*(float(self.hp)/self.max_hp))
    self.color = libtcod.Color(255, c, c)

class Ranged_Minion(Minion):
  def __init__(self, battleground, x, y, side, name, color=libtcod.white):
    super(Ranged_Minion, self).__init__(battleground, x, y, side, name)
    self.ranged_power = 4
    self.power = 1
    self.max_hp = 10
    self.hp = 10
    self.default_next_action = 10
    self.reset_action()

  def follow_tactic(self):
    if self.tactic is None: return
    next_x = self.x+1 if self.side == 0 else self.x-1
    if self.tactic == tactic.stop and self.bg.tiles[(next_x, self.y)].entity == None:
      self.bg.effects.append(Arrow(self.bg, next_x, self.y, self.side, self.ranged_power))
    else: super(Ranged_Minion, self).follow_tactic()

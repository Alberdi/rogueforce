from entity import Mine, Wave
from minion import Minion
import libtcodpy as libtcod

class General(Minion):
  def __init__(self, battleground, x, y, side, name):
    super(General, self).__init__(battleground, x, y, side, name)
    self.max_hp = 100
    self.hp = 100
    self.max_cd = []
    self.cd = []
    self.skills = [self.heal_target_minion, self.heal_all_minions, self.heal_all_minions, self.mine, self.sonic_wave]
    self.tactics = ["forward", "stop", "go_sides", "go_center"]
    self.selected_tactic = self.tactics[0]
    self.strategies = []
    for i in range(0, len(self.skills)):
      self.max_cd.append(50)
      self.cd.append(0)

  def command_tactic(self, i):
    self.selected_tactic = self.tactics[i]
    for m in self.bg.minions:
      if m.side == self.side:
        m.tactic = self.tactics[i]

  def update(self):
    if not self.alive: return
    for i in range(0, len(self.skills)):
      if self.cd[i] < self.max_cd[i]: self.cd[i] += 1

  def use_skill(self, i):
    if self.cd[i] >= self.max_cd[i]:
      if self.skills[i](): self.cd[i] = 0

  def heal_all_minions(self):
    for m in self.bg.minions:
      m.get_healed(100)
    return True

  def heal_target_minion(self):
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
    # TODO that 16
    (x, y) = (mouse.cx-16, mouse.cy)
    if (x >= self.bg.width or x < 0 or y >= self.bg.height or y < 0): return False
    minion = self.bg.tiles[(mouse.cx-16, mouse.cy)].entity
    if minion is not None and minion.side == self.side and minion != self and minion.hp != minion.max_hp:
      minion.get_healed(100)
      return True
    return False
 
  def mine(self):
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
    # TODO that 16
    (x, y) = (mouse.cx-16, mouse.cy)
    if (x >= self.bg.width or x < 0 or y >= self.bg.height or y < 0): return False
    if self.bg.tiles[(x, y)].entity is not None: return False
    Mine(self.bg, x, y)
    return True 
 
  def sonic_wave(self):
    self.bg.effects.append(Wave(self.bg, self.x, self.y+1, self.side))
    self.bg.effects.append(Wave(self.bg, self.x+1 if self.side == 0 else self.x-1, self.y, self.side))
    self.bg.effects.append(Wave(self.bg, self.x, self.y-1, self.side))
    return True

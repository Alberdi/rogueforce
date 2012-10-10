from minion import Minion
import libtcodpy as libtcod

class General(Minion):
  def __init__(self, battleground, x, y, side, name):
    super(General, self).__init__(battleground, x, y, side, name)
    self.max_hp = 100
    self.hp = 100
    self.max_cd = []
    self.cd = []
    self.skills = [self.heal_target_minion, self.heal_all_minions, self.heal_all_minions]
    for i in range(0, len(self.skills)):
      self.max_cd.append(50)
      self.cd.append(0)

  def update(self):
    if not self.alive: return
    for i in range(0, len(self.skills)):
      if self.cd[i] < self.max_cd[i]: self.cd[i] += 1

  def use_skill(self, i):
    if self.cd[i] >= self.max_cd[i]:
      self.skills[i](i)

  def heal_target_minion(self, i):
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
    # TODO that 16
    (x, y) = (mouse.cx-16, mouse.cy)
    if (self.bg.width < x < 0 or self.bg.height < y < 0): return
    minion = self.bg.tiles[(mouse.cx-16, mouse.cy)].entity
    if minion is not None and minion.side == self.side and minion != self:
      self.cd[i] = 0
      minion.get_healed(100)
  
  def heal_all_minions(self, i):
    self.cd[i] = 0
    for m in self.bg.minions:
      m.get_healed(100)

from minion import Minion

import libtcodpy as libtcod
import skill
import tactic

import inspect

class General(Minion):
  def __init__(self, battleground, x, y, side, name, color=libtcod.white):
    super(General, self).__init__(battleground, x, y, side, name, color)
    self.max_hp = 100
    self.hp = 100
    self.max_cd = []
    self.cd = []
    self.skills = [(skill.heal_target_minion, 100), (skill.heal_all_minions, 20), (skill.mine, 50), (skill.sonic_waves, 10, 3), (skill.water_pusher, 50)]
    self.skill_quotes =["Don't die!", "Heal you all men!", "Mine", "Sonic Waves", "Hidro Pump"]
    self.tactics = [tactic.forward, tactic.stop, tactic.backward, tactic.go_sides, tactic.go_center]
    self.tactic_quotes = ["Forward", "Fire", "Backward", "Go sides", "Go center"]
    self.selected_tactic = self.tactics[0]
    self.command_tactic(0)
    self.strategies = []
    for i in range(0, len(self.skills)):
      self.max_cd.append(50)
      self.cd.append(0)

  def can_be_pushed(self, dx, dy):
    return False

  def command_tactic(self, i):
    self.selected_tactic = self.tactics[i]
    for m in self.bg.minions:
      if m.side == self.side:
        m.tactic = self.tactics[i]

  def update(self):
    if not self.alive: return
    for i in range(0, len(self.skills)):
      if self.cd[i] < self.max_cd[i]: self.cd[i] += 1

  def use_skill(self, i, x, y):
    if self.cd[i] >= self.max_cd[i]:
      params = [self]
      if inspect.getargspec(self.skills[i][0])[0][1:3] == ['x', 'y']: params.extend([x, y])
      params.extend(self.skills[i][1:])
      if self.skills[i][0](*params): # Used properly
        for j in range(0, len(self.skills)):
          if j != i: self.cd[j] -= 5
          else:
            self.max_cd[i] *= 2
            self.cd[i] = 0
        return True
    return False

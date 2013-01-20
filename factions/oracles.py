from area import *
import formation
from general import General
from sieve import *
from skill import *
from status import *

import libtcodpy as libtcod

class Gemekaa(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Gemekaa", color=libtcod.light_crimson):
    super(Gemekaa, self).__init__(battleground, side, x, y, name, color)
    self.max_hp = 70
    self.death_quote = "I did not foresee this..."
    self.formation = formation.InvertedWedge(self, 1)

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, place_entity, 50, [Thunder(self.bg)], "Thunderstruck", SingleTarget(self.bg)))
    self.skills.append(Skill(self, apply_status, 50, [Blind(None, 30)], "Lightstruck", AllBattleground(self.bg, is_minion, self)))

  def use_skill(self, i, x, y):
    splash = range(-1,2)
    # TODO: this is more pseudo than random, maybe we shoud at least add a bit more of entropy
    pseudorandom = (x+1)*19+(y+1)*41+151*(i+1)
    j = 1
    for s in self.skills:
      pseudorandom += s.cd*(83+j)
      j += 6
    (new_x, new_y) = (x+splash[pseudorandom%len(splash)], y+splash[(pseudorandom*x+7*y)%len(splash)])
    if new_x < 0: new_x = 0
    if new_y < 0: new_y = 0
    if new_x > self.bg.width: new_x = self.bg.width
    if new_y > self.bg.height: new_y = self.bg.height
    return super(Gemekaa, self).use_skill(i, new_x, new_y)

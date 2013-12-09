from area import *
from general import General
from sieve import *
from skill import *
from status import *

import libtcodpy as libtcod

import random

class Ox(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Ox", color=libtcod.dark_red):
    super(Ox, self).__init__(battleground, side, x, y, name, color)
    self.rand = random.Random()
    self.max_hp = 300
    self.helix_index = 2

  def get_attacked(self, enemy):
    if self.rand.randint(1,6) == 6:
      self.use_skill(-1, 0, 0)      
    super(Ox, self).get_attacked(enemy)
   
  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, apply_status, 20, [Taunted(None, self, 3, 20)], "Berserker's Call",
                      "Taunts nearby units and gains bonus armor during the duration",
                      Circle(self.bg, is_enemy, self, None, True, 5)))
    self.skills.append(Skill(self, apply_status, 30, [PoisonHunger(None, 1, 6, 20)], "Battle Hunger",
                      "Enemy gets slowed and takes damage over time until it kills a unit",
                      SingleTarget(self.bg, is_enemy, self, is_inrange_close)))
    self.skills.append(Skill(self, place_entity, 5, [Slash(self.bg, side=self.side)], "Counter Helix",
                      "When attacked, performs a helix counter attack", SingleTarget(self.bg)))
    self.skills.append(Skill(self, decapitate, 75, [0.33], "Culling Blade",
                      "Decapitates enemies with low health.", SingleTarget(self.bg, is_enemy, self, is_adjacent)))

  def start_battle(self):
    super(Ox, self).start_battle()
    self.rand.seed(hash(self.name))

  def use_skill(self, i, x, y):
    if i == self.helix_index:
      # Counter helix can't be used like that
      return False
    else:
      if i == -1:
        i = self.helix_index # Forced counter helix
      super(Ox, self).use_skill(i, x, y)

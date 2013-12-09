from area import *
from general import General
from sieve import *
from skill import *
from status import *

import libtcodpy as libtcod

import random

class Starcall(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Starcall", color=libtcod.cyan):
    super(Starcall, self).__init__(battleground, side, x, y, name, color)
    self.rand = random.Random()
   
  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, apply_status, 5, [Vanishing(None, 10)], "Black hole",
                      "Vanishes a group of minions", Circle(self.bg, is_ally_minion, self, radius=3)))
    self.skills.append(Skill(self, apply_status, 5, [Shield(None, 20)], "Watch out!",
                      "Shields minion from upcoming damage", AllBattleground(self.bg, is_ally_minion, self)))
    self.skills.append(Skill(self, place_entity, 5, [Thunder(self.bg, power=30)], "Thunderstruck",
                      "A powerful lightning strikes near the target", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 50, [Thunder(self.bg, power=10, area=Circle(self.bg, radius=5))], "Thunderstruck",
                      "A lightning from above creates a wide explosion", SingleTarget(self.bg)))

  def start_battle(self):
    super(Starcall, self).start_battle()
    self.rand.seed(1574)
    self.alternative_skill = Skill(self, recall_entity, 10, [10], "Black exit",
                             "Recalls the vanished minions", Circle(self.bg, is_inrange_long, self, 3))

  def use_skill(self, i, x, y):
    if i == 0:
      if super(Starcall, self).use_skill(i, x, y):
        (self.skills[0], self.alternative_skill) = (self.alternative_skill, self.skills[0])
        return True
      return False
    (new_x, new_y) = (x+self.rand.randint(-i, i), y+self.rand.randint(-i, i))
    if new_x < 0: new_x = 0
    if new_y < 0: new_y = 0
    if new_x > self.bg.width: new_x = self.bg.width
    if new_y > self.bg.height: new_y = self.bg.height
    return super(Starcall, self).use_skill(i, new_x, new_y)

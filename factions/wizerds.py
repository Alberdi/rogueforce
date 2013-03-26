from area import *
from general import General
from skill import *

import libtcodpy as libtcod

import random

class Starcall(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Starcall", color=libtcod.cyan):
    super(Starcall, self).__init__(battleground, side, x, y, name, color)
    self.rand = random.Random()
    self.rand.seed(1574)
  
  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, null, 5))
    self.skills.append(Skill(self, null, 5))
    self.skills.append(Skill(self, place_entity, 5, [Thunder(self.bg, power=30)], "Thunderstruck",
                      "A powerful lightning strikes near the target", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 5, [Thunder(self.bg, power=10, area=Circle(self.bg, radius=5))], "Thunderstruck",
                      "A lightning from above creates a wide explosion", SingleTarget(self.bg)))

  def use_skill(self, i, x, y):
    (new_x, new_y) = (x+self.rand.randint(-i, i), y+self.rand.randint(-i, i))
    if new_x < 0: new_x = 0
    if new_y < 0: new_y = 0
    if new_x > self.bg.width: new_x = self.bg.width
    if new_y > self.bg.height: new_y = self.bg.height
    return super(Starcall, self).use_skill(i, new_x, new_y)

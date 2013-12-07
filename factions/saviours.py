from area import *
from general import General
from skill import *
from effect import *
from math import copysign
import tactic

import libtcodpy as libtcod

class Ares(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Ares", color=libtcod.red):
    super(Ares, self).__init__(battleground, side, x, y, name, color)
    self.max_hp = 200
    self.death_quote = "I lost a battle, but..."
    self.starting_minions = 0
    self.flag = None
    self.tactics = [tactic.null]
    self.tactic_quotes = ["Slash'em all!"]

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side, steps=5, goto=-1)], "Left slash",
                      "Slashes the right side", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side, steps=5)], "Right slash",
                      "Slashes the left side", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side)], "Round slash",
                      "Slashes all round", SingleTarget(self.bg)))


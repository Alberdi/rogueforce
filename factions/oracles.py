from area import *
import formation
from general import General
from minion import Minion
from sieve import *
from skill import *
from status import *

import libtcodpy as libtcod

import random

class Slave(Minion):
  def __init__(self, battleground, side, x=-1, y=-1, name="slave", color=libtcod.white):
    super(Slave, self).__init__(battleground, side, x, y, name, color)
    self.max_hp = 10
    self.hp = 10
    self.power = 3

class Gemekaa(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Gemekaa", color=libtcod.light_crimson):
    super(Gemekaa, self).__init__(battleground, side, x, y, name, color)
    self.max_hp = 70
    self.death_quote = "I did not foresee this..."
    self.formation = formation.InvertedWedge(self, 3)
    self.minion = Slave(self.bg, self.side)
    self.starting_minions = 251

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, apply_status, 50, [Blind(None, 30)], "Lightstruck",
                      "Blinds all minions", AllBattleground(self.bg, is_minion, self)))
    self.skills.append(Skill(self, place_entity, 25, [Thunder(self.bg)], "Thunderstruck",
                      "A powerful lightning strikes near the target", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 100, [Thunder(self.bg, power=5, area=Circle(self.bg, radius=5))], "Thunderstruck",
                      "A lightning from above creates a wide explosion", SingleTarget(self.bg)))

  def use_skill(self, i, x, y):
    if i == 0:
      return super(Gemekaa, self).use_skill(i, x, y)
    #FIXME: a dedicated player can "cheat" the very first skill used will land, as there's not enough entropy
    rand = random.Random()
    rand.seed((x+1)*19+(y+1)*41+151*(i+1)+self.minions_alive*31+self.skills[2].cd)
    (new_x, new_y) = (x+rand.randint(-i,i), y+rand.randint(-i,i))
    if new_x < 0: new_x = 0
    if new_y < 0: new_y = 0
    if new_x > self.bg.width: new_x = self.bg.width
    if new_y > self.bg.height: new_y = self.bg.height
    return super(Gemekaa, self).use_skill(i, new_x, new_y)

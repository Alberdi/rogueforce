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
    self.death_quote = "We lost a battle, but..."
    self.starting_minions = 0
    self.flag = None
    self.tactics = [tactic.stop, tactic.null]
    self.tactic_quotes = ["Stop", "To the flag"]
    self.previous_tactic = self.tactics[1]

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, place_entity, 10, [Effect(self.bg, char='q', color=libtcod.red)], "Die",
                      "Place a flag to charge against it", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side, steps=6)], "Right Splash",
                      "Hit a right splash", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side, steps=6, goto=-1)], "Left Splash",
                      "Hit a left splash", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side)], "All Splash",
                      "Hit around splash", SingleTarget(self.bg)))


  def update(self):
    super(Ares, self).update()
    if self.selected_tactic == tactic.null:
      if self.next_action <= 0:
        self.reset_action()
        dx = self.flag.x - self.x
        dy = self.flag.y - self.y
        self.move(copysign(1, dx) if dx else 0, copysign(1, dy) if dy else 0)
      else:
        self.next_action -= 1
      

  def use_skill(self, i, x, y):
    if super(Ares, self).use_skill(i, x, y):
      self.skills[i].max_cd = self.skills[i].original_max_cd
      if i == 0:
        if self.flag:
          self.flag.dissapear()
        self.flag = self.bg.effects[-1]

  
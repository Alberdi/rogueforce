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
    self.tactics = [tactic.stop, tactic.null]
    self.tactic_quotes = ["Stop", "To flag"]
    self.previous_tactic = self.tactics[1]

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, place_entity, 10, [Blinking(self.bg, char='q', color=libtcod.red)], "Die",
                      "Place a flag to charge against it", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side, steps=5, goto=-1)], "Left slash",
                      "Slashes the right side", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side, steps=5)], "Right slash",
                      "Slashes the left side", SingleTarget(self.bg)))
    self.skills.append(Skill(self, place_entity, 30, [Slash(self.bg, side=self.side)], "Round slash",
                      "Slashes all round", SingleTarget(self.bg)))

  def update(self):
    super(Ares, self).update()
    if self.selected_tactic == tactic.null:
      if self.next_action <= 0 and self.flag:
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

class Archer(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Ares", color=libtcod.red):
    super(Archer, self).__init__(battleground, side, x, y, name, color)
    self.max_hp = 200
    self.death_quote = "I lost a battle, but..."
    self.starting_minions = 0
    self.flag = None
    self.tactics = [tactic.stop, tactic.null]
    self.tactic_quotes = ["Stop", "To flag"]
    self.previous_tactic = self.tactics[1]
    self.prototype_arrow = Pointing_Arrow(self.bg)

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, place_entity, 10, [Blinking(self.bg, char='q', color=libtcod.red)], "Die",
                      "Place a flag to charge against it", SingleTarget(self.bg)))
    self.skills.append(Skill(self, add_path, 30, [], "Pointing Arrow",
                      "Eat Wood, madafuka", StraightLine(self.bg)))

  def update(self):
    super(Archer, self).update()
    if self.selected_tactic == tactic.null:
      if self.next_action <= 0 and self.flag:
        self.reset_action()
        dx = self.flag.x - self.x
        dy = self.flag.y - self.y
        self.move(copysign(1, dx) if dx else 0, copysign(1, dy) if dy else 0)
      else:
        self.next_action -= 1

  def use_skill(self, i, x, y):
    if i == 1 and self.flag:
      x = self.flag.x
      y = self.flag.y
      self.prototype_arrow.char = "<" if x - self.x < 0 else ">"
      self.skills[1].parameters = [self.prototype_arrow.clone(x, y)]
    if super(Archer, self).use_skill(i, x, y):
      self.skills[i].max_cd = self.skills[i].original_max_cd
      if i == 0:
        if self.flag:
          self.flag.dissapear()
        self.flag = self.bg.effects[-1]

      if i == 1:
        self.skills[1].parameters[0].path.pop(0)
        



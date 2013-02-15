from area import *
from general import General
from minion import Minion, BigMinion
from skill import *
import sieve

import libtcodpy as libtcod

class Flappy(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Flappy", color=libtcod.dark_green):
    super(Flappy, self).__init__(battleground, side, x, y, name, color)
    self.death_quote = "I'll be back, like a boo... me..."
    self.minion = Minion(self.bg, self.side, name="goblin")

  def draw_slingshot(self):
    if self.side:
      self.slingshot.chars[2], self.slingshot.chars[5] = self.slingshot.chars[5], self.slingshot.chars[2]
    else:
      self.slingshot.chars[8], self.slingshot.chars[5] = self.slingshot.chars[5], self.slingshot.chars[8]

  def gobmerang_flying(self):
    return (self.slingshot.x+1, self.slingshot.y+1) != (self.gobmerang.x, self.gobmerang.y)

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, add_path, 5, [self.gobmerang], "Fire the Gobmerang!", "Launches Gobmerang to fly high in the air",
                             Arc(self.bg, origin=(self.gobmerang.x, self.y), ratio_y=0.6)))
    self.skills.append(Skill(self, place_entity, 5, [Boulder(self.bg, char='o', delay=5)], "Drop the boulder!", "Tells Gobmerang to drop a boulder",
                             SingleTarget(self.bg)))

  def start_battle(self):
    self.gobmerang = Pathing(self.bg, self.x + (-3 if self.side else 3), self.y, self.side, char='G')
    self.slingshot = BigMinion(self.bg, self.side, self.x + (-4 if self.side else 2), self.y-1, name="Slingmerang",
                               chars=list("//>\\~ ~\\|") if self.side else list("//|\\~ ~\\<"), colors=[libtcod.white]*9)
    self.draw_slingshot()
    self.slingshot_drawn = False
    self.gobmerang_shot = False
    super(Flappy, self).start_battle()

  def update(self):
    if not self.alive:
      return
    if self.skills[0].cd == self.skills[0].max_cd-1 and not self.slingshot_drawn:
      self.draw_slingshot()
      self.slingshot_drawn = True
    super(Flappy, self).update()

  def use_skill(self, i, x, y):
    if i == 0:
      if self.gobmerang_flying():
        return False
      if super(Flappy, self).use_skill(i, x, y):
        # Gobmerang needs to return to the slingshot afterwards
        self.gobmerang.path.append(self.bg.tiles[(self.gobmerang.x, self.gobmerang.y)])
        self.draw_slingshot()
        self.slingshot_drawn = False
        self.gobmerang_shot = False
        return True
    elif i == 1:
      if not self.gobmerang_shot and len(self.gobmerang.path) > 3:
        if super(Flappy, self).use_skill(i, self.gobmerang.path[2].x, self.gobmerang.path[2].y):
          self.bg.effects[-1].path = self.gobmerang.path[2:15]
          self.gobmerang_shot = True
          return True
    else:
      return super(Flappy, self).use_skill(i, x, y)
    return False


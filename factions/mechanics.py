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

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, add_path, 5, [self.gobmerang], "Fire the Gobmerang!", "Launches Gobmerang to fly high in the air",
                             Arc(self.bg, origin=(self.gobmerang.x, self.y), ratio_y=0.6)))
  def start_battle(self):
    self.gobmerang = Pathing(self.bg, self.x + (-3 if self.side else 3), self.y, self.side, char='G')
    self.slingshot = BigMinion(self.bg, self.side, self.x + (-4 if self.side else 2), self.y-1, name="Slingmerang",
                               chars=['H']*9, colors=[libtcod.white]*9)
    super(Flappy, self).start_battle()


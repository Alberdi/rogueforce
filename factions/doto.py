from area import *
from effect import *
from general import General
from sieve import *
from skill import *
from status import *

import libtcodpy as libtcod

import random

class Bloodrotter(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Bloodrotter", color=libtcod.darker_red):
    super(Bloodrotter, self).__init__(battleground, side, x, y, name, color)
    self.power = 7
    self.thirst_charges = 0
    self.prev_thirst_charges = 0

  def initialize_skills(self):
    self.skills = []
    bloodrage_duration = 30
    self.skills.append(Skill(self, apply_statuses, 20,
                       [[Empower(None, self, bloodrage_duration, "Bloodrage empower", 1),
                         FreezeCooldowns(None, self, bloodrage_duration, "Bloodrage silence"),
                         Poison(None, self, 1, 1, bloodrage_duration/2, "Bloodrage poison")]],
                       "Bloodrage", "Gives higher power to a unit, but takes damage and silence",
                      SingleTarget(self.bg, is_unit, self, is_inrange_close)))
    self.skills.append(Skill(self, null, 1, [], "Blood Bath", "Gain health for every unit killed"))
    self.skills.append(Skill(self, null, 1, [], "Thirst",
                       "Gets damage and speed based on enemy's missing health"))
    self.skills.append(Skill(self, nuke_statuses, 100, [20, TempEffect(self.bg, char='*', color=self.color),
                       "magical", [Bleeding(owner=self, power=5, duration=40, name="Rupture")]],
                       "Rupture", "Deals initial damage plus extra damage if the unit moves",
                       SingleTarget(self.bg, is_enemy, self, is_inrange_close)))

  def register_kill(self, killed):
    super(Bloodrotter, self).register_kill(killed)
    # Blood Bath
    self.get_healed(int(killed.max_hp * 0.25))

  def thirst(self, enemy):
    self.thirst_charges = (enemy.max_hp-enemy.hp)/int(enemy.max_hp*0.2)
    diff = self.thirst_charges - self.prev_thirst_charges
    if diff:
      self.power += 3 * diff
      self.prev_thirst_charges = self.thirst_charges

  def update(self):
    self.thirst(self.bg.generals[(self.side+1)%2])
    self.next_action -= self.thirst_charges
    super(Bloodrotter, self).update()

class Ox(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Ox", color=libtcod.dark_red):
    super(Ox, self).__init__(battleground, side, x, y, name, color)
    self.rand = random.Random()
    self.max_hp = 300
    self.helix_index = 2

  def get_attacked(self, enemy, power=None, attack_effect=None, attack_type=None):
    if not attack_type:
      attack_type = enemy.attack_type
    if attack_type == "physical" and self.rand.randint(1,6) == 6:
      self.use_skill(-1, 0, 0)      
    super(Ox, self).get_attacked(enemy, power, attack_effect, attack_type)
   
  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, apply_status, 20, [Taunted(None, self, 3, 20)], "Berserker's Call",
                      "Taunts nearby units and gains bonus armor",
                      Circle(self.bg, is_enemy, self, None, True, 5)))
    self.skills.append(Skill(self, apply_status, 30, [PoisonHunger(None, self, 1, 6, 20)], "Battle Hunger",
                      "Enemy gets slowed and takes damage until it kills a unit",
                      SingleTarget(self.bg, is_enemy, self, is_inrange_close)))
    self.skills.append(Skill(self, place_entity, 5, [Slash(self.bg, side=self.side)], "Counter Helix",
                      "When attacked, performs a helix counter attack", SingleTarget(self.bg)))
    self.skills.append(Skill(self, decapitate, 75, [0.33], "Culling Blade",
                      "Decapitates enemies with low health", SingleTarget(self.bg, is_enemy, self, is_adjacent)))

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
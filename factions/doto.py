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
    self.max_hp = 250
    self.power = 11
    self.thirst_charges = 0
    self.prev_thirst_charges = 0

  def initialize_skills(self):
    self.skills = []
    bloodrage_duration = 50
    self.skills.append(Skill(self, apply_statuses, 90,
                       [[Empower(None, self, bloodrage_duration, "Bloodrage empower", 1),
                         FreezeCooldowns(None, self, bloodrage_duration, "Bloodrage silence"),
                         Poison(None, self, 1, 1, bloodrage_duration/2, "Bloodrage poison")]],
                       "Bloodrage", "Gives higher power to a unit, but takes damage and silence",
                      SingleTarget(self.bg, is_unit, self, is_inrange_close)))
    self.skills.append(Skill(self, null, 1, [], "Blood Bath", "Gain health for every unit killed"))
    self.skills.append(Skill(self, null, 1, [], "Thirst",
                       "Gets damage and speed based on enemy's missing health"))
    self.skills.append(Skill(self, nuke_statuses, 140, [40, TempEffect(self.bg, char='*', color=self.color),
                       "magical", [Bleeding(owner=self, power=30, duration=40, name="Rupture")]],
                       "Rupture", "Deals initial damage plus extra damage if the unit moves",
                       SingleTarget(self.bg, is_enemy, self, is_inrange_close)))

  def register_kill(self, killed):
    super(Bloodrotter, self).register_kill(killed)
    # Blood Bath
    self.get_healed(int(killed.max_hp * 0.25))

  def thirst(self, enemy):
    self.thirst_charges = (enemy.max_hp-enemy.hp)/int(enemy.max_hp*0.33)
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
    self.max_hp = 400
    self.helix_index = 2

  def get_attacked(self, enemy, power=None, attack_effect=None, attack_type=None):
    if not attack_type:
      attack_type = enemy.attack_type
    if attack_type == "physical" and self.rand.randint(1,6) == 6:
      self.use_skill(-1, 0, 0)      
    super(Ox, self).get_attacked(enemy, power, attack_effect, attack_type)
   
  def initialize_skills(self):
    self.skills = []
    taunt_duration = 80
    self.skills.append(Skill(self, [apply_status, apply_status], 35, [[Taunted(None, self, taunt_duration)], 
                       [Shield(name="Berserker's Call", armor=1, duration=taunt_duration), True]], "Berserker's Call",
                      "Taunts nearby units and gains bonus armor", Circle(self.bg, is_enemy, self, None, True, 5), True))
    self.skills.append(Skill(self, apply_status, 100, [PoisonHunger(None, self, 4, 6, 20)], "Battle Hunger",
                      "Enemy gets slowed and takes damage until it kills a unit",
                      SingleTarget(self.bg, is_enemy, self, is_inrange_close)))
    self.skills.append(Skill(self, place_entity, 2, [Slash(self.bg, side=self.side, power=10)], "Counter Helix",
                      "When attacked, performs a helix counter attack", SingleTarget(self.bg)))
    self.skills.append(Skill(self, decapitate, 80, [0.33], "Culling Blade",
                      "Decapitates enemies with low health", SingleTarget(self.bg, is_enemy, self, is_adjacent)))

  def start_battle(self):
    super(Ox, self).start_battle()
    self.rand.seed(hash(self.name))

  def use_skill(self, i, x, y):
    if i == self.helix_index:
      # Counter helix can't be used like that
      return False
    else:
      last = self.last_skill_used
      if i == -1:
        i = self.helix_index # Forced counter helix
      skill_used = super(Ox, self).use_skill(i, x, y)
      if skill_used and i == self.helix_index:
        self.last_skill_used = last
      return skill_used

class Pock(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Pock", color=libtcod.sky):
    super(Pock, self).__init__(battleground, side, x, y, name, color)
    self.max_hp = 200
    self.armor["physical"] = 1
    self.orb = Orb(self.bg, self.side, char='o', color=self.color)
    self.orb_index = 0

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, place_entity, 60, [self.orb], "Illusory Orb",
                       "Launches a magic orb that damages and might be teleported into",
                       SingleTarget(self.bg, general=self, reach_function=is_inrange_long, selfcentered=True)))
    self.skills.append(Skill(self, nuke_statuses, 70, [15, TempEffect(self.bg, char='`', color=self.color),
                       "magical", [FreezeCooldowns(None, self, 20, "Waning Rift silence")]],
                       "Waning Rift", "Deals damage and silences enemy units nearby",
                       Circle(self.bg, is_enemy, self, selfcentered=True, radius=2)))

  def use_skill(self, i, x, y):
    skill_used = super(Pock, self).use_skill(i, x, y)
    if skill_used and i == self.orb_index:
      self.orb = self.bg.tiles[(self.x, self.y)].effects[-1]
      self.orb.path = Line(self.bg, origin=(self.x, self.y)).get_tiles(x, y)[:20]
    return skill_used

class Rubock(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Rubock", color=libtcod.green):
    super(Rubock, self).__init__(battleground, side, x, y, name, color)
    self.copied_skill = 2
    self.armor["physical"] = 1

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, apply_status, 120, [Lifted(None, self, 15,
                      land_area=Circle(self.bg, is_enemy, self, radius=4),land_status=Stunned(None, self, 15))],
                      "Telekinesis", "Lifts an enemy  into the air that stuns around on landing",
                      SingleTarget(self.bg, is_enemy, self, is_inrange_close)))
    self.skills.append(Skill(self, apply_status, 40, [Jumping(None, self, 1, "Fade Bolt", 10, -1, 
                      Circle(self.bg, is_enemy, self, radius=2), Empower(duration = 20, name="Fade Bolt debuff",
                       power_ratio=-0.25))], "Fade Bolt", "Travels between units damaging and weakening them",
                      SingleTarget(self.bg, is_enemy, self, is_inrange_close)))
    self.skills.append(Skill(self, null, 1, [], "Null Field", "Grants magic resistance to all allies"))
    self.skills.append(Skill(self, copy_spell, 140, [], "Spell Steal", "Copies the last spell used by the enemy",
                      SingleTarget(self.bg, is_enemy_general, self, is_inrange_long)))
    self.skills.append(Skill(self, null, 1, [], "Spell Stolen", "Copy of the last spell used by the enemy"))

  def start_battle(self):
    super(Rubock, self).start_battle()
    Aura(self, self, name="Null Field aura", area=Circle(self.bg, is_ally, self, radius=6),
        status=Shield(name="Null Field", armor=2, armor_type="magical"))


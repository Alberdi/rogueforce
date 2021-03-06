from area import *
from formation import *
from minion import *
from sieve import *
from skill import *
from status import *
import effect
import tactic

import libtcodpy as libtcod

import math

class General(Minion):
  def __init__(self, battleground, side, x=-1, y=-1, name="General", color=libtcod.orange):
    super(General, self).__init__(battleground, side, x, y, name, name[0], color)
    self.max_hp = 300
    self.cost = 250
    self.death_quote = "..."
    self.flag = None
    self.formation = Rows(self)
    self.minion = Minion(self.bg, self.side, char='b' if side else 'd')
    self.skills = []
    self.starting_minions = 101
    self.tactics = [tactic.stop, tactic.forward, tactic.backward, tactic.go_sides, tactic.go_center, tactic.attack_general, tactic.defend_general]
    self.tactic_quotes = ["Stop/Fire", "Forward", "Backward", "Go sides", "Go center", "Attack", "Defend"]
    self.selected_tactic = self.tactics[0]
    self.previous_tactic = self.tactics[0]
    self.swap_cd = 0
    self.swap_max_cd = 200
    self.swap_sickness = 10
    self.last_skill_used = -1
    self.armor["physical"] = 2
    self.power = 10

  def ai_action(self, turn):
    return None

  def can_be_pushed(self, dx, dy):
    return False

  def change_battleground(self, bg, x, y):
    super(General, self).change_battleground(bg, x, y)
    self.minion.change_battleground(bg, -1, -1)

  def command_tactic(self, i):
    self.selected_tactic = self.tactics[i]
    for m in self.bg.minions:
      if m.side == self.side:
        m.tactic = self.tactics[i]

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, heal, 50, [100], "Don't die!", "1", SingleTarget(self.bg, is_ally_minion, self)))
    self.skills.append(Skill(self, heal, 50, [20], "Heal you all men!",  "2", AllBattleground(self.bg, is_minion, self)))
    self.skills.append(Skill(self, place_entity, 50, [Mine(self.bg)], "Can't touch this", "3", SingleTarget(self.bg, is_empty)))
    self.skills.append(Skill(self, sonic_waves, 50, [10, 3], "Sonic Waves", "4"))
    self.skills.append(Skill(self, water_pusher, 50, [], "Hidro Pump", "5", SingleTarget(self.bg)))

  def place_flag(self, x, y):
    if self.flag:
      if (self.flag.x, self.flag.y) == (x,y):
        return
      self.flag.dissapear()
    if self.bg.is_inside(x, y):
      self.flag = effect.Blinking(self.bg, self.side, x, y, 'q', self.original_color)
    else:
      self.flag = None

  def recommand_tactic(self):
    self.command_tactic(self.tactics.index(self.selected_tactic))

  def recount_minions_alive(self):
    self.minions_alive = len(filter(lambda x: x.alive and x.side == self.side, self.bg.minions))

  def start_battle(self):
    self.initialize_skills()
    self.command_tactic(0)
    self.swap_cd = 200
    #self.formation.place_minions()

  def start_scenario(self):
    self.deployed = False
    self.hp = self.max_hp
    self.minions_alive = self.starting_minions
    self.requisition = 0

  def swap(self, i):
    r = self.bg.reserves[self.side]
    if self.swap_cd >= self.swap_max_cd and len(r) > i:
      self.bg.generals[self.side] = r[i]
      r[i].swap_cd = 0
      r[i].next_action = r[i].swap_sickness
      self.bg.tiles[(self.x, self.y)].entity = r[i]
      (r[i].x, r[i].y) = (self.x, self.y)
      if self.flag:
        r[i].place_flag(self.flag.x, self.flag.y)
        self.flag.dissapear()
        self.flag = None
      self.bg.reserves[self.side][i] = self
      return True
    return False

  def update(self):
    if not self.alive:
      return
    for s in self.skills:
      s.update()
    for s in self.statuses:
      s.update()
    self.swap_cd = min(self.swap_cd+1, self.swap_max_cd)
    if self.next_action <= 0:
      self.reset_action()
      if self.flag and self.bg.is_inside(self.flag.x, self.flag.y):
        dx = self.flag.x - self.x
        dy = self.flag.y - self.y
        if not self.move(math.copysign(1, dx) if dx else 0, math.copysign(1,dy) if dy else 0) \
            or (self.x, self.y) == (self.flag.x, self.flag.y):
          self.place_flag(-1, -1)
      else:
        if not self.try_attack():
          self.next_action = -1
    else:
      self.next_action -= 1
      
  def update_color(self):
    self.color = self.original_color

  def use_skill(self, i, x, y):
    skill = self.skills[i]
    if skill.is_ready():
      if skill.use(x, y):
        for s in self.skills:
          s.change_cd(-5)
        #skill.change_max_cd(skill.max_cd)
        skill.reset_cd()
        self.last_skill_used = i
        return True
    return False

class Conway(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Conway", color=libtcod.green):
    super(Conway, self).__init__(battleground, side, x, y, name, color)
    self.death_quote = "This is more like a game of... death"
    self.tactics = [tactic.stop, tactic.null]
    self.tactic_quotes = ["Stop", "Live life"]
    self.selected_tactic = self.tactics[0]

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, minion_glider, 50, [False], "Glide from the top!", "", SingleTarget(self.bg, is_empty)))
    self.skills.append(Skill(self, minion_glider, 50, [True], "Glide from the bottom!", "", SingleTarget(self.bg, is_empty)))
    self.skills.append(Skill(self, minion_lwss, 50, [], "Lightweight strike force!", "", SingleTarget(self.bg, is_empty)))
    self.skills.append(Skill(self, apply_status, 50, [Poison(None, 5, 19, 4)],
                             "Poison on your veins!", "", SingleTarget(self.bg, is_enemy, self)))

  def live_life(self, tile):
    neighbours = 0
    for i in [-1, 0, 1]:
      for j in [-1, 0, 1]:
        (x, y) = (tile.x+i, tile.y+j)
        if (i, j) == (0, 0) or not self.bg.is_inside(x, y): continue
        if self.bg.tiles[(x, y)].entity is not None and self.bg.tiles[(x, y)].entity.is_ally(self): neighbours += 1
    # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
    if tile.entity is None and neighbours == 3 and tile.passable: self.next_gen_births.append(tile)
    # Any live cell...
    elif tile.entity is not None and tile.entity.is_ally(self) and tile.entity != self:
      # ...with more than three live neighbours dies, as if by overcrowding.
      if neighbours > 3: self.next_gen_deaths.append(tile)
      # ...with fewer than two live neighbours dies, as if caused by under-population.
      elif neighbours < 2: self.next_gen_deaths.append(tile)
      # ...with two or three live neighbours lives on to the next generation.
      # No need to do any action.

  def update(self):
    if not self.alive: return
    if self.selected_tactic == tactic.null: # Live life
      if self.next_action <= 0:
        self.reset_action()
        self.next_gen_births = []
        self.next_gen_deaths = []
        for t in self.bg.tiles.values():
          self.live_life(t)
        for tile in self.next_gen_births:
          minion_placed = self.minion.clone(tile.x, tile.y) 
          if minion_placed is not None:
            self.bg.minions.append(minion_placed)
        for tile in self.next_gen_deaths:
          tile.entity.die()
        self.recount_minions_alive()
      else:
        self.next_action -= 1
    super(Conway, self).update()

class Emperor(General):
  def __init__(self, battleground, side, x=-1, y=-1, name="Emperor", color=libtcod.sepia):
    super(Emperor, self).__init__(battleground, side, x, y, name, color)
    self.max_hp = 60
    #self.start_quote = "May this night carry my will and these old stars forever remember this night."
    self.death_quote = "Nightspirit... embrace my soul..."
    self.human_form = True
    self.minion = RangedMinion(self.bg, self.side, name="wizard")
    self.minion.attack_effects = [')', '(']
    self.starting_minions = 0
    self.transform_index = 3

  def die(self):
    if self.human_form:
      self.use_skill(self.transform_index, 0, 0)
    else:
      self.transform()
      super(Emperor, self).die()

  def initialize_skills(self):
    self.skills = []
    self.skills.append(Skill(self, restock_minions, 25, [21], "Once destroyed, their souls are being summoned", ""))
    self.skills.append(Skill(self, apply_status, 50, [FreezeCooldowns(None, 15)], "I curse you of all men", "",
                             AllBattleground(self.bg, is_enemy_general, self)))
    self.skills.append(Skill(self, water_pusher, 50, [], "Towards the Pantheon", "", SingleTarget(self.bg)))
    self.skills.append(Skill(self, null, 200, [], "This shouldn't be showed", ""))
    # We don't need that last quote because it will be changed and pulled in transform()

  def start_battle(self):
    super(Emperor, self).start_battle()
    self.minons_alive = 0

  def transform(self):
    if not self.human_form:
      self.char = 'E'
      self.name = "Emperor"
      return
    self.human_form = False
    self.hp = self.max_hp
    self.char = 'N'
    self.name = "Nightspirit"
    self.original_color = libtcod.light_grey
    self.color = self.original_color
    self.skills = []
    self.skills.append(Skill(self, sonic_waves, 50, [10, 3], "Thus spake the Nightspirit", ""))
    self.skills.append(Skill(self, darkness, 50, [20], "Nightside eclipse", "", AllBattleground(self.bg)))
    self.skills.append(Skill(self, consume, 50, [1, 1], "My wizards are many, but their essence is mine", "",
                             AllBattleground(self.bg, is_ally_minion, self)))
    self.skills.append(Skill(self, sonic_waves, 250, [50, 50],
                             "O'Nightspirit... I am one with thee, I am the eternal power, I am the Emperor!", ""))
    # Last quote is shared with the human form skill
    return True

  def use_skill(self, i, x, y):
    skill_used = super(Emperor, self).use_skill(i, x, y)
    if skill_used and self.human_form and i == self.transform_index: self.transform()
    return skill_used

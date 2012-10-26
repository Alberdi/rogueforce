from area import *
from formation import *
from minion import *
from sieve import *
from skill import *
from status import *

import libtcodpy as libtcod
import tactic

class General(Minion):
  def __init__(self, battleground, x, y, side, name = "General", color=libtcod.orange):
    super(General, self).__init__(battleground, x, y, side, name, color)
    self.max_hp = 100
    self.death_quote = "..."
    self.formation = Rows(self)
    self.minion = Minion(self.bg, -1, -1, self.side, "minion")
    self.starting_minions = 101
    self.skills = []
    self.skills.append(Skill(self, heal, 50, [100], "Don't die!", SingleTarget(self, is_ally_minion)))
    self.skills.append(Skill(self, heal, 50, [20], "Heal you all men!", AllBattleground(self, is_minion)))
    self.skills.append(Skill(self, place_entity, 50, [Mine(self.bg)], "Can't touch this", SingleTarget(self, is_empty)))
    self.skills.append(Skill(self, sonic_waves, 50, [10, 3], "Sonic Waves"))
    self.skills.append(Skill(self, water_pusher, 50, [], "Hidro Pump", SingleTarget(self)))
    self.tactics = [tactic.forward, tactic.stop, tactic.backward, tactic.go_sides, tactic.go_center, tactic.attack_general, tactic.defend_general]
    self.tactic_quotes = ["Forward", "Stop/Fire", "Backward", "Go sides", "Go center", "Attack", "Defend"]
    self.selected_tactic = self.tactics[0]

  def can_be_pushed(self, dx, dy):
    return False

  def command_tactic(self, i):
    self.selected_tactic = self.tactics[i]
    for m in self.bg.minions:
      if m.side == self.side:
        m.tactic = self.tactics[i]

  def start_battle(self):
    self.hp = self.max_hp
    self.minions_alive = self.starting_minions
    self.command_tactic(0)

  def update(self):
    if not self.alive: return
    for s in self.skills: s.update()
    for s in self.statuses: s.update()

  def update_color(self):
    pass

  def use_skill(self, i, x, y):
    skill = self.skills[i]
    if skill.cd >= skill.max_cd:
      if skill.use(x, y):
        for s in self.skills:
          s.change_cd(-5)
        skill.change_max_cd(skill.max_cd)
        skill.reset_cd()
        return True
    return False

class Conway(General):
  def __init__(self, battleground, x, y, side, name = "Conway", color=libtcod.green):
    super(Conway, self).__init__(battleground, x, y, side, name, color)
    self.death_quote = "This is more like a game of... death"
    self.skills = []
    self.skills.append(Skill(self, minion_glider, 50, [False], "Glide from the top!", SingleTarget(self, is_empty)))
    self.skills.append(Skill(self, minion_glider, 50, [True], "Glide from the bottom!", SingleTarget(self, is_empty)))
    self.skills.append(Skill(self, minion_lwss, 50, [], "Lightweight strike force!", SingleTarget(self, is_empty)))
    self.skills.append(Skill(self, apply_status, 50, [Poison(None, 5, 19, 4)],
                             "Poison on your veins!", SingleTarget(self, is_enemy)))
    self.tactics = [tactic.null, tactic.stop]
    self.tactic_quotes = ["Live life", "Stop"]
    self.selected_tactic = self.tactics[0]

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
          self.bg.minions.append(self.minion.clone(tile.x, tile.y))
        for tile in self.next_gen_deaths:
          tile.entity.die()
      else:
        self.next_action -= 1
    super(Conway, self).update()

class Emperor(General):
  def __init__(self, battleground, x, y, side, name = "Emperor", color=libtcod.sepia):
    super(Emperor, self).__init__(battleground, x, y, side, name, color)
    self.max_hp = 60
    #self.start_quote = "May this night carry my will and these old stars forever remember this night."
    self.death_quote = "Nightspirit... embrace my soul..."
    self.human_form = True
    self.minion = Ranged_Minion(self.bg, -1, -1, self.side, "wizard")
    self.minion.attack_effects = [')', '(']
    self.starting_minions = 0
    curse = Freeze_Cooldowns(None, 15)
    self.skills = []
    self.skills.append(Skill(self, restock_minions, 25, [21], "Once destroyed, their souls are being summoned"))
    self.skills.append(Skill(self, apply_status, 50, [Freeze_Cooldowns(None, 15)], "I curse you of all men",
                             AllBattleground(self, is_enemy_general)))
    self.skills.append(Skill(self, water_pusher, 50, [], "Towards the Pantheon", SingleTarget(self)))
    self.skills.append(Skill(self, null, 200, [], "This shouldn't be showed"))
    # We don't need that last quote because it will be changed and pulled in transform()
    self.transform_index = 3

  def die(self):
    if self.human_form:
      self.cd[self.transform_index] = self.max_cd[self.transform_index]
      self.use_skill(self.transform_index, 0, 0)
    else:
      self.char = 'E'
      self.name = "Emperor"
      super(Emperor, self).die()

  def transform(self):
    if not self.human_form: return False
    self.human_form = False
    self.hp = self.max_hp
    self.char = 'N'
    self.name = "Nightspirit"
    self.original_color = libtcod.light_grey
    self.color = self.original_color
    self.skills = []
    self.skills.append(Skill(self, sonic_waves, 50, [10, 3], "Thus spake the Nightspirit"))
    self.skills.append(Skill(self, darkness, 50, [20], "Nightside eclipse", AllBattleground(self)))
    self.skills.append(Skill(self, consume, 50, [1, 1], "My wizards are many, but their essence is mine",
                             AllBattleground(self, is_ally_minion)))
    self.skills.append(Skill(self, sonic_waves, 250, [50, 50],
                             "O'Nightspirit... I am one with thee, I am the eternal power, I am the Emperor!"))
    # Last quote is shared with the human form skill
    return True

  def use_skill(self, i, x, y):
    skill_used = super(Emperor, self).use_skill(i, x, y)
    if skill_used and self.human_form and i == self.transform_index: self.transform()
    return skill_used

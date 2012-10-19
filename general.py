from minion import Minion
from formation import *

import libtcodpy as libtcod
import skill
import tactic

import inspect

class General(Minion):
  def __init__(self, battleground, x, y, side, name, color=libtcod.white):
    super(General, self).__init__(battleground, x, y, side, name, color)
    self.max_hp = 100
    self.hp = 100
    self.max_cd = []
    self.cd = []
    self.formation = Files(self)
    self.minion = Minion(self.bg, 0, 0, self.side, "minion")
    self.starting_minions = 138
    self.bg.tiles[(0,0)].entity = None
    self.skills = [(skill.heal_target_minion, 100), (skill.heal_all_minions, 20), (skill.mine, 50), (skill.sonic_waves, 10, 3), (skill.water_pusher, 50)]
    self.skill_quotes =["Don't die!", "Heal you all men!", "Mine", "Sonic Waves", "Hidro Pump"]
    self.tactics = [tactic.forward, tactic.stop, tactic.backward, tactic.go_sides, tactic.go_center, tactic.attack_general, tactic.defend_general]
    self.tactic_quotes = ["Forward", "Fire", "Backward", "Go sides", "Go center", "Attack", "Defend"]
    self.selected_tactic = self.tactics[0]
    for i in range(0, len(self.skills)):
      self.max_cd.append(50)
      self.cd.append(0)

  def can_be_pushed(self, dx, dy):
    return False

  def command_tactic(self, i):
    self.selected_tactic = self.tactics[i]
    for m in self.bg.minions:
      if m.side == self.side:
        m.tactic = self.tactics[i]

  def update(self):
    if not self.alive: return
    for i in range(0, len(self.skills)):
      if self.cd[i] < self.max_cd[i]: self.cd[i] += 1

  def update_color(self):
    pass

  def use_skill(self, i, x, y):
    if self.cd[i] >= self.max_cd[i]:
      params = [self]
      if inspect.getargspec(self.skills[i][0])[0][1:3] == ['x', 'y']:
        if not self.bg.is_inside(x, y): return
        params.extend([x, y])
      params.extend(self.skills[i][1:])
      if self.skills[i][0](*params): # Used properly
        for j in range(0, len(self.skills)):
          if j != i: self.cd[j] -= 5
          else:
            self.max_cd[i] *= 2
            self.cd[i] = 0
        return True
    return False

class Conway(General):
  def __init__(self, battleground, x, y, side, name, color=libtcod.white):
    super(Conway, self).__init__(battleground, x, y, side, name, color)
    self.skills = [(skill.minion_glider, False), (skill.minion_glider, True), (skill.minion_lwss, )]
    self.skill_quotes = ["Glide from the top!", "Glide from the bottom!", "Lightweight strike force!"]
    self.tactics = [tactic.null, tactic.stop]
    self.tactic_quotes = ["Live life", "Stop"]
    self.selected_tactic = self.tactics[0]
    self.command_tactic(0)

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

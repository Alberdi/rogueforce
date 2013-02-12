from battle import BattleWindow
from battleground import Battleground
from entity import *
from general import *
from faction import *
from window import *

import libtcodpy as libtcod

import re

KEYMAP_GENERALS = "QWERTYUIOP"
MOVEGEN_PATTERN = re.compile("move_gen(\d) \((-?\d+),(-?\d+)\)")

class Scenario(Window):
  def __init__(self, battleground, side, factions, host = None, port = None, window_id = 0):
    super(Scenario, self).__init__(battleground, side, host, port, window_id)
    self.factions = factions
    self.requisition = [999, 300]
    self.max_requisition = 999
    self.keymap_generals = KEYMAP_GENERALS[0:len(factions[side].generals)]
    self.selected_general = None
    for f in factions:
      for g in f.generals:
        g.start_scenario()
 
    #TODO: remove, just for testing purposes
    self.i = 0
    self.deploy_general(factions[1].generals[2])
    self.i += 1
    self.deploy_general(factions[1].generals[1])
    self.i += 1
    self.deploy_general(factions[1].generals[0])

  def apply_requisition(self, general):
    if general.deployed: return
    if general.requisition + self.requisition[general.side] >= general.cost:
      if self.deploy_general(general):
        self.requisition[general.side] -= general.cost - general.requisition
        general.requisition = general.cost
      else: #If can't be deployed, we give all but one requisition points
        self.requisition[general.side] -= general.cost - general.requisition - 1
        general.requisition = general.cost - 1
    else:
      general.requisition += self.requisition[general.side]
      self.requisition[general.side] = 0

  def check_input(self, key, x, y):
    n = self.keymap_generals.find(chr(key.c).upper()) # Number of the general pressed
    if n != -1:
      g = self.factions[self.side].generals[n]
      if g.deployed:
        self.selected_general = g
        if not self.bg.is_inside(x, y):
          return
        return "move_gen{0} ({1},{2})\n".format(n, x, y) 
      else:
        self.selected_general = None
        return "apply_req{0}\n".format(n)
    return None

  def deploy_general(self, general):
    if general.teleport(1 if general.side == 0 else 56+self.i, 21):
      general.target = (4,21) if general.side == 0 else (52,21)
      general.home = general.target
      general.deployed = True
      general.alive = True
      self.bg.generals.append(general)
      self.message(general.name + " has been deployed on the " + ("left" if general.side == 0 else "right") 
                                + " side.", general.color)
      return True
    return False

  def get_next_tile(self, general):
    for t in [(general.x+i, general.y+j) for i in range(-1,2) for j in range(-1,2)]:
      if self.bg.tiles[t].entity == self.bg.tiles[general.target].entity:
        return t
    starting_tiles = general.get_passable_neighbours()
    checked = [(general.x, general.y)]
    for starting in starting_tiles:
      tiles = [starting]
      while tiles:
        (x, y) = tiles.pop()
        checked.append((x, y))
        for t in [(x+i, y+j) for i in range(-1,2) for j in range(-1,2)]:
          if self.bg.tiles[t].entity == self.bg.tiles[general.target].entity:
            return starting
          if self.bg.tiles[t].passable and t not in checked:
            tiles.append(t)

  def increment_requisition(self):
    for f in self.bg.fortresses:
      if f.side != NEUTRAL_SIDE:
        self.requisition[f.side] += f.requisition_production
    for i in [0,1]:
      if self.requisition[i] > self.max_requisition:
        self.requisition[i] = self.max_requisition

  def process_messages(self, turn):
    for i in [0,1]:
      if turn in self.messages[i]:
        if self.messages[i][turn].startswith("apply_req"):
          self.apply_requisition(self.factions[i].generals[int(self.messages[i][turn][9])])
        else:
          match = MOVEGEN_PATTERN.match(self.messages[i][turn])
          if match:
            g = self.factions[i].generals[int(match.group(1))]
            (x, y) = (int(match.group(2)), int(match.group(3)))
            if not self.bg.is_inside(x, y):
              return
            target = self.bg.tiles[(x, y)].entity
            home = self.bg.tiles[(g.x, g.y)].entity
            if (target in self.bg.fortresses and home in self.bg.fortresses and g in home.guests):
              for (f, tile) in home.connected_fortresses:
                if f == target:
                  # Send general g out from fortress home to fortress target thorugh tile
                  (g.x, g.y) = tile
                  g.home = (home.x, home.y)
                  g.target = (target.x, target.y)
                  home.unhost(g)
                  return

  def render_side_panel(self, i, bar_length, bar_offset_x):
    libtcod.console_set_default_foreground(self.con_panels[i], libtcod.white)
    libtcod.console_print(self.con_panels[i], bar_offset_x-1, 0, " Requisition")
    libtcod.console_set_default_foreground(self.con_panels[i], libtcod.black)
    self.render_bar(self.con_panels[i], bar_offset_x, 1, bar_length, self.requisition[i], self.max_requisition, libtcod.dark_blue, libtcod.sky, libtcod.black)
    line = 4
    for j in range(0, len(self.factions[i].generals)):
      g = self.factions[i].generals[j]
      libtcod.console_set_default_foreground(self.con_panels[i], g.color if g == self.selected_general else libtcod.white)
      libtcod.console_print(self.con_panels[i], bar_offset_x-1, line, " " + g.name)
      libtcod.console_set_default_foreground(self.con_panels[i], libtcod.black)
      libtcod.console_put_char_ex(self.con_panels[i], bar_offset_x-1, line+1, self.keymap_generals[j], g.color, libtcod.black)
      if not g.deployed:
        self.render_bar(self.con_panels[i], bar_offset_x, line+1, bar_length, g.requisition, g.cost, libtcod.dark_blue, libtcod.sky, libtcod.black)
      else: 
        self.render_bar(self.con_panels[i], bar_offset_x, line+1, bar_length, g.hp, g.max_hp, libtcod.red, libtcod.yellow, libtcod.black)
      line += 3

  def start_battle(self, generals):
    if generals[0].side != 0: # Left side must be the first
      (generals[0], generals[1]) = (generals[1], generals[0])
    return self.start_battle_thread(generals)
    #thread.start_new_thread(self.start_battle_thread, (generals,))

  def start_battle_thread(self, generals):
    battleground = Battleground(BG_WIDTH, BG_HEIGHT)
    battleground.generals = generals
    scenario_pos = []
    for g in generals:
      scenario_pos.append((g.x, g.y))
      g.change_battleground(battleground, 3 if g.side == 0 else 56, g.y)
    battle = BattleWindow(battleground, 0)
    winner = battle.loop()
    for i in [0,1]:
      generals[i].change_battleground(self.bg, *(scenario_pos[i]))
      if not generals[i].alive:
        generals[i].die()
        generals[i].start_scenario()
        self.message(generals[(i+1)%2].name + " defeated " + generals[i].name + " on a battle.", generals[(i+1)%2].color)
   
  def update_all(self):
    self.increment_requisition()
    for g in self.bg.generals:
      if not g.deployed:
        continue
      enemy = g.enemy_reachable(diagonals=True)
      if enemy is not None and enemy.side != NEUTRAL_SIDE:
        if enemy in self.bg.fortresses:
          if enemy.guests:
            e = enemy.guests[-1]
            self.start_battle([g, e])
            if not e.alive:
              enemy.unhost(e)
        else:
          self.start_battle([g, enemy])
      else:
        t = self.get_next_tile(g)
        if t:
          entity = self.bg.tiles[t].entity
          if entity in self.bg.fortresses:
            entity.host(g)
          elif g.can_move(t[0]-g.x, t[1]-g.y):
            g.move(t[0]-g.x, t[1]-g.y)
          else:
            g.target = g.home


if __name__=="__main__":
  battleground = Battleground(BG_WIDTH, BG_HEIGHT, "map.txt")
  factions = []
  factions.append(Saviours(battleground, 0))
  factions.append(Oracles(battleground, 1))
  scenario = Scenario(battleground, 0, factions) 
  scenario.loop()

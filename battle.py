from area import SingleTarget
from battleground import Battleground
from general import *
from window import *

import libtcodpy as libtcod

import copy
import re

KEYMAP_SKILLS = "QWERTYUIOP"
KEYMAP_TACTICS = "ZXCVBNM"

FLAG_PATTERN = re.compile("flag \((-?\d+),(-?\d+)\)")
SKILL_PATTERN = re.compile("skill(\d) \((-?\d+),(-?\d+)\)")

class BattleWindow(Window):
  def __init__(self, battleground, side, host = None, port = None, window_id = 1):
    for i in [0,1]:
      battleground.generals[i].start_battle()

    self.keymap_skills = KEYMAP_SKILLS[0:len(battleground.generals[side].skills)]
    self.keymap_tactics = KEYMAP_TACTICS[0:len(battleground.generals[side].tactics)]
    super(BattleWindow, self).__init__(battleground, side, host, port, window_id)

  def ai_action(self, turn):
    ai_side = (self.side+1)%2
    return self.bg.generals[ai_side].ai_action(turn)

  def check_input(self, key, mouse, x, y):
    if mouse.rbutton_pressed:
      self.bg.generals[self.side].place_flag(x, y)
      return "flag ({0},{1})\n".format(x, y)
    n = self.keymap_skills.find(chr(key.c).upper()) # Number of the skill pressed
    if n != -1: 
      if chr(key.c).istitle(): # With uppercase we show the area
        self.hover_function = self.bg.generals[self.side].skills[n].get_area_tiles
      else: # Use the skill
        self.hover_function = None
        return "skill{0} ({1},{2})\n".format(n, x, y)
    if chr(key.c) == ' ':
      if self.bg.generals[self.side].tactics.index(self.bg.generals[self.side].selected_tactic) == 0:
        n = self.bg.generals[self.side].tactics.index(self.bg.generals[self.side].previous_tactic)
      else:
        self.bg.generals[self.side].previous_tactic = self.bg.generals[self.side].selected_tactic
        n = 0
    else:
      if self.bg.generals[self.side].tactics.index(self.bg.generals[self.side].selected_tactic) != 0:
        self.bg.generals[self.side].previous_tactic = self.bg.generals[self.side].selected_tactic
      n = self.keymap_tactics.find(chr(key.c).upper()) # Number of the tactic pressed
    if n != -1:
      last_Tactic = n
      return "tactic{0}\n".format(n)
    return None

  def check_winner(self):
    #TODO: detect draws
    for i in [0,1]:
      if not self.bg.generals[i].alive:
        self.message(self.bg.generals[i].name + ": " + self.bg.generals[i].death_quote, self.bg.generals[i].original_color)
        self.message(self.bg.generals[i].name + " is dead!", self.bg.generals[i].original_color)
        self.game_over = True
        return self.bg.generals[(i+1)%2]
    return None

  def clean_all(self):
    for e in copy.copy(self.bg.effects):
      if not e.alive:
        self.bg.effects.remove(e)
    for m in copy.copy(self.bg.minions):
      if not m.alive:
        self.bg.minions.remove(m)

  def process_messages(self, turn):
    for i in [0,1]:
      if turn in self.messages[i]:
        if self.messages[i][turn].startswith("tactic"):
          self.bg.generals[i].command_tactic(int(self.messages[i][turn][6]))
        else:
          match = FLAG_PATTERN.match(self.messages[i][turn])
          if match:
            self.bg.generals[i].place_flag(int(match.group(1)), int(match.group(2)))
          else:
            match = SKILL_PATTERN.match(self.messages[i][turn])
            if match:
              if self.bg.generals[i].use_skill(*map(int, match.groups())):
                self.message(self.bg.generals[i].name + ": " + self.bg.generals[i].skills[int(match.group(1))].quote,
                             self.bg.generals[i].color)

  def render_msgs(self):
    y = 0
    for (line, color) in self.game_msgs:
      libtcod.console_set_default_foreground(self.con_msgs, color)
      libtcod.console_print(self.con_msgs, 0, y, line)
      y += 1

  def render_info(self, x, y):
    libtcod.console_print(self.con_info, 0, 0, " " * INFO_WIDTH)
    nskills = len(self.bg.generals[1].skills)
    i=-1
    if -13 < x < -1:
      i = 0
    elif BG_WIDTH + + 1 < x < BG_WIDTH + + 13:
      i = 1
    
    nskills = len(self.bg.generals[i].skills)
    if (5 + nskills * 2) > y > 3 and i is not -1:
      skill = self.bg.generals[i].skills[(y-5)/2]
      libtcod.console_set_default_foreground(self.con_info, libtcod.white)
      libtcod.console_print(self.con_info, 0, 0, skill.description)
    else:
      super(BattleWindow, self).render_info(x, y)

  def render_side_panel(self, i, bar_length, bar_offset_x):
    libtcod.console_set_default_foreground(self.con_panels[i], libtcod.black)
    self.render_bar(self.con_panels[i], bar_offset_x, 1, bar_length, self.bg.generals[i].hp, self.bg.generals[i].max_hp,
      libtcod.red, libtcod.yellow, libtcod.black)
    line = 3
    for s in range(0, len(self.bg.generals[i].skills)):
      libtcod.console_put_char_ex(self.con_panels[i], bar_offset_x-1, line, KEYMAP_SKILLS[s], libtcod.white, libtcod.black)
      self.render_bar(self.con_panels[i], bar_offset_x, line, bar_length, self.bg.generals[i].skills[s].cd, self.bg.generals[i].skills[s].max_cd,
        libtcod.dark_blue, libtcod.sky, libtcod.black)
      line += 2
    libtcod.console_set_default_foreground(self.con_panels[i], libtcod.white)
    libtcod.console_print(self.con_panels[i], 3, line+1,
                          str(self.bg.generals[i].minions_alive) + " " + self.bg.generals[i].minion.name + "s  ")
    self.render_tactics(i)

  def render_tactics(self, i):
    bar_offset_x = 3
    line = 7 + len(self.bg.generals[i].skills)*2
    for s in range(0, len(self.bg.generals[i].tactics)):
      libtcod.console_set_default_foreground(self.con_panels[i],
        libtcod.red if self.bg.generals[i].tactics[s] == self.bg.generals[i].selected_tactic else libtcod.white)
      libtcod.console_print(self.con_panels[i], bar_offset_x, line, KEYMAP_TACTICS[s] + ": " + self.bg.generals[i].tactic_quotes[s])
      line += 2

from factions import doto
if __name__=="__main__":
  bg = Battleground(BG_WIDTH, BG_HEIGHT)
  bg.generals = [doto.Bloodrotter(bg, 0, 3, 21), doto.Ox(bg, 1, 56, 21)]
  bg.generals[0].start_scenario()
  bg.generals[1].start_scenario()
  if len(sys.argv) == 4: 
    battle = BattleWindow(bg, int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
  elif len(sys.argv) == 2:
    battle = BattleWindow(bg, int(sys.argv[1]))
  else:
    battle = BattleWindow(bg, 0)
  battle.loop()

from area import SingleTarget
from battleground import Battleground
from general import *
from window import *

import libtcodpy as libtcod

import copy
import re

KEYMAP_SKILLS = "QWERTYUIOP"
KEYMAP_TACTICS = "ZXCVBNM"

SKILL_PATTERN = re.compile("skill(\d) \((-?\d+),(-?\d+)\)")

class BattleWindow(Window):
  def __init__(self, battleground, side, host = None, port = None, window_id = 1):
    for i in [0,1]:
      battleground.generals[i].formation.place_minions()
      battleground.generals[i].command_tactic(0)
      battleground.generals[i].start_battle()

    self.keymap_skills = KEYMAP_SKILLS[0:len(battleground.generals[side].skills)]
    self.keymap_tactics = KEYMAP_TACTICS[0:len(battleground.generals[side].tactics)]
    super(BattleWindow, self).__init__(battleground, side, host, port, window_id)

  def check_game_over(self):
    for i in [0,1]:
      if not self.bg.generals[i].alive:
        self.message(self.bg.generals[i].name + ": " + self.bg.generals[i].death_quote, self.bg.generals[i].original_color)
        self.message(self.bg.generals[i].name + " is dead!", self.bg.generals[i].original_color)
        self.game_over = True

  def check_input(self, key, x, y):
    n = self.keymap_skills.find(chr(key.c).upper()) # Number of the skill pressed
    if n != -1: 
      if chr(key.c).istitle(): # With uppercase we show the area
        hover_function = self.bg.generals[self.side].skills[n].get_area_tiles
      else: # Use the skill
        hover_function = None
        return "skill{0} ({1},{2})\n".format(n, x, y)
    n = self.keymap_tactics.find(chr(key.c).upper()) # Number of the tactic pressed
    if n != -1: 
      return "tactic{0}\n".format(n)
    return None

  def clean_all(self):
    for e in copy.copy(self.bg.effects):
      if not e.alive:
        self.bg.effects.remove(e)
    for m in copy.copy(self.bg.minions):
      if not m.alive:
        self.bg.minions.remove(m)

  def process_messages(self, turn):
    t = turn - TURN_LAG
    for i in [0,1]:
      if t in self.messages[i]:
        match = SKILL_PATTERN.match(self.messages[i][t])
        if match is not None:
          if self.bg.generals[i].use_skill(*map(int, match.groups())):
            self.message(self.bg.generals[i].name + ": " + self.bg.generals[i].skills[int(match.group(1))].quote, self.bg.generals[i].color)
        elif self.messages[i][t].startswith("tactic"):
          self.bg.generals[i].command_tactic(int(self.messages[i][t][6]))

  def render_bar(self, con, x, y, w, value, max_value, bar_bg_color, bar_fg_color, text_color):
    ratio = int(w*(float(value)/max_value))
    libtcod.console_set_default_background(con, bar_fg_color)
    libtcod.console_rect(con, x, y, ratio, 1, False, libtcod.BKGND_SET)
    libtcod.console_set_default_background(con, bar_bg_color)
    libtcod.console_rect(con, x+ratio, y, w-ratio, 1, False, libtcod.BKGND_SET)
    libtcod.console_set_default_background(con, text_color)
    libtcod.console_print_rect(con, x+1, y, w, 1, "%03d / %03d" % (value, max_value))

  def render_msgs(self):
    y = 0
    for (line, color) in self.game_msgs:
      libtcod.console_set_default_foreground(self.con_msgs, color)
      libtcod.console_print(self.con_msgs, 0, y, line)
      y += 1

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

if __name__=="__main__":
  bg = Battleground(BG_WIDTH, BG_HEIGHT)
  bg.generals = [Emperor(bg, 3, 21, 0), General(bg, 56, 21, 1)]
  if len(sys.argv) == 4: 
    battle = BattleWindow(bg, int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
  else:
    battle = BattleWindow(bg, int(sys.argv[1]))
  battle.loop()

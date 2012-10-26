from area import SingleTarget
from battleground import Battleground
from general import *

import libtcodpy as libtcod

import copy
import random
import re
import socket
import sys
import textwrap
import time

BG_WIDTH = 60
BG_HEIGHT = 43
PANEL_WIDTH = 16
PANEL_HEIGHT = BG_HEIGHT
INFO_WIDTH = BG_WIDTH
INFO_HEIGHT = 1
MSG_WIDTH = BG_WIDTH - 2
MSG_HEIGHT = 6
SCREEN_WIDTH = BG_WIDTH + PANEL_WIDTH*2
SCREEN_HEIGHT = BG_HEIGHT + INFO_HEIGHT + MSG_HEIGHT + 1

BG_OFFSET_X = PANEL_WIDTH
BG_OFFSET_Y = MSG_HEIGHT + 1
PANEL_OFFSET_X = 0
PANEL_OFFSET_Y = BG_OFFSET_Y + 3
MSG_OFFSET_X = BG_OFFSET_X
MSG_OFFSET_Y = 1
INFO_OFFSET_X = PANEL_WIDTH + 1
INFO_OFFSET_Y = BG_OFFSET_Y + BG_HEIGHT

KEYMAP_SKILLS = "QWERTYUIOP"
KEYMAP_TACTICS = "ZXCVBNM"

SKILL_PATTERN = re.compile("skill(\d) \((-?\d+),(-?\d+)\)")

TURN_LAG = 1

class Game(object):
  def __init__(self, battleground, side, host = None, port = None):
    if host is not None:
      self.network = Network(host, port)
    else:
      self.network = None
    self.bg = battleground
    self.side = side
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Rogue Force')

    self.messages = [{}, {}]

    self.con_root = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    self.con_bg = libtcod.console_new(BG_WIDTH, BG_HEIGHT)
    self.con_info = libtcod.console_new(INFO_WIDTH, INFO_HEIGHT)
    self.con_msgs = libtcod.console_new(MSG_WIDTH, MSG_HEIGHT)
    self.con_panels = [libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT), libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT)]

    for i in [0,1]:
      self.bg.generals[i].formation.place_minions()
      self.bg.generals[i].command_tactic(0)

    self.keymap_skills = KEYMAP_SKILLS[0:len(self.bg.generals[self.side].skills)]
    self.keymap_tactics = KEYMAP_TACTICS[0:len(self.bg.generals[self.side].tactics)]
    self.game_msgs = []
    self.game_over = False
    self.area_hover_color = libtcod.green
    self.area_hover_color_invalid = libtcod.red
    self.default_hover_color = libtcod.blue
    self.default_hover_function = SingleTarget(self.bg.generals[self.side]).get_all_tiles

    self.bg.generals[0].start_battle()
    self.bg.generals[1].start_battle()
    self.render_all(0,0)

  def check_game_over(self):
    for i in [0,1]:
      if not self.bg.generals[i].alive:
        self.message(self.bg.generals[i].name + ": " + self.bg.generals[i].death_quote, self.bg.generals[i].original_color)
        self.message(self.bg.generals[i].name + " is dead!", self.bg.generals[i].original_color)
        self.game_over = True

  def clean_all(self):
    for e in copy.copy(self.bg.effects):
      if not e.alive:
        self.bg.effects.remove(e)
    for m in copy.copy(self.bg.minions):
      if not m.alive:
        self.bg.minions.remove(m)

  def do_hover(self, hover_function, x, y):
    if hover_function is not None:
      tiles = hover_function(x,y)
      if tiles is None:
        self.bg.hover_tiles(self.default_hover_function(x,y), self.area_hover_color)
      elif tiles:
        self.bg.hover_tiles(tiles, self.area_hover_color)
      else:
        self.bg.hover_tiles(self.default_hover_function(x, y), self.area_hover_color_invalid)
    else:
      self.bg.hover_tiles(self.default_hover_function(x, y), self.default_hover_color)

  def message(self, new_msg, color=libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
    for line in new_msg_lines:
      #if the buffer is full, remove the first line to make room for the new one
      if len(self.game_msgs) == MSG_HEIGHT:
        del self.game_msgs[0]
        libtcod.console_clear(self.con_msgs)
      #add the new line as a tuple, with the text and the color
      self.game_msgs.append((line, color))

  def loop(self):
    turn = 0
    turn_time = 0.1
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    hover_function = None
    while not self.game_over:
      start = time.time()
      if self.network is not None and turn > 0:
        received = self.network.recv()
        split = received.split("#")
        if len(split) == 2:
          self.messages[not self.side][int(split[0])] = split[1]

      while time.time() - start < turn_time:
        libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
        (x, y) = (mouse.cx-BG_OFFSET_X, mouse.cy-BG_OFFSET_Y)
        if key.vk == libtcod.KEY_ESCAPE: exit()
        n = self.keymap_skills.find(chr(key.c).upper()) # Number of the skill pressed
        if n != -1: 
          if chr(key.c).istitle(): # With uppercase we show the area
            hover_function = self.bg.generals[self.side].skills[n].get_area_tiles
          else: # Use the skill
            self.messages[self.side][turn] = "skill{0} ({1},{2})\n".format(n, x, y)
            #messages[self.side] += "skill{0} ({1},{2})\n".format(n, x, y)
            hover_function = None
        n = self.keymap_tactics.find(chr(key.c).upper()) # Number of the tactic pressed
        if n != -1: 
          self.messages[self.side][turn] = "tactic{0}\n".format(n)

      if self.network != None:
        if turn in self.messages[self.side]:
          self.network.send(str(turn) + "#"  + self.messages[self.side][turn])
        else:
          self.network.send("D")

      self.process_messages(turn)
      self.update_all()
      self.check_game_over()
      if (turn % 100) == 0: self.clean_all()
      self.do_hover(hover_function, x, y)
      turn +=1
      self.render_all(x, y)

    while True: # Game is over
      libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
      if key.vk == libtcod.KEY_ESCAPE: exit()

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

  def render_all(self, x, y):
    self.bg.draw(self.con_bg)
    self.render_info(x, y)
    self.render_msgs()
    self.render_panels()
    libtcod.console_blit(self.con_bg, 0, 0, BG_WIDTH, BG_HEIGHT, self.con_root, BG_OFFSET_X, BG_OFFSET_Y)
    for i in [0,1]:
      libtcod.console_blit(self.con_panels[i], 0, 0, PANEL_WIDTH, PANEL_HEIGHT, self.con_root, (PANEL_WIDTH+BG_WIDTH)*i, PANEL_OFFSET_Y)
    libtcod.console_blit(self.con_info, 0, 0, MSG_WIDTH, MSG_HEIGHT, self.con_root, INFO_OFFSET_X, INFO_OFFSET_Y)
    libtcod.console_blit(self.con_msgs, 0, 0, MSG_WIDTH, MSG_HEIGHT, self.con_root, MSG_OFFSET_X, MSG_OFFSET_Y)
    libtcod.console_blit(self.con_root, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    libtcod.console_flush()
 
  def render_bar(self, con, x, y, w, value, max_value, bar_bg_color, bar_fg_color, text_color):
    ratio = int(w*(float(value)/max_value))
    libtcod.console_set_default_background(con, bar_fg_color)
    libtcod.console_rect(con, x, y, ratio, 1, False, libtcod.BKGND_SET)
    libtcod.console_set_default_background(con, bar_bg_color)
    libtcod.console_rect(con, x+ratio, y, w-ratio, 1, False, libtcod.BKGND_SET)
    libtcod.console_set_default_background(con, text_color)
    libtcod.console_print_rect(con, x+1, y, w, 1, "%03d / %03d" % (value, max_value))

  def render_info(self, x, y):
    libtcod.console_print(self.con_info, 0, 0, " " * INFO_WIDTH)
    if self.bg.is_inside(x, y):
      libtcod.console_set_default_foreground(self.con_info, libtcod.white)
      libtcod.console_print(self.con_info, INFO_WIDTH-7, 0, "%02d/%02d" % (x, y))
      entity = self.bg.tiles[(x, y)].entity
      if entity is not None:
        if entity in self.bg.minions or entity in self.bg.generals:
          libtcod.console_set_default_foreground(self.con_info, self.bg.generals[entity.side].original_color)
          libtcod.console_print(self.con_info, 0, 0, entity.name.capitalize() + ": HP %02d/%02d, PW %d" %
            (entity.hp, entity.max_hp, entity.power))

  def render_msgs(self):
    y = 0
    for (line, color) in self.game_msgs:
      libtcod.console_set_default_foreground(self.con_msgs, color)
      libtcod.console_print(self.con_msgs, 0, y, line)
      y += 1

  def render_panels(self):
    bar_length = 11
    bar_offset_x = 4
    for i in [0,1]:
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

  def update_all(self):
    for g in self.bg.generals:
      g.update()
    for e in self.bg.effects:
      e.update()
    for m in self.bg.minions:
      m.update()

class Network(object):
  def __init__(self, host, port):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.connect((host, port))

  def recv(self):
    return self.s.recv(1024)

  def send(self, data):
    self.s.send(data)


if __name__=="__main__":
  bg = Battleground(BG_WIDTH, BG_HEIGHT)
  bg.generals = [Emperor(bg, 3, 21, 0), General(bg, 56, 21, 1)]
  if len(sys.argv) == 4: 
    game = Game(bg, int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
  else:
    game = Game(bg, int(sys.argv[1]))
  game.loop()

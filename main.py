from battleground import Battleground
from general import General
from minion import *

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
MSG_WIDTH = BG_WIDTH - 2
MSG_HEIGHT = 6
SCREEN_WIDTH = BG_WIDTH + PANEL_WIDTH*2
SCREEN_HEIGHT = BG_HEIGHT + MSG_HEIGHT + 2

BG_OFFSET_X = PANEL_WIDTH
BG_OFFSET_Y = 0
MSG_OFFSET_X = PANEL_WIDTH + 1
MSG_OFFSET_Y = BG_HEIGHT + 1

LIMIT_FPS = 20

KEYMAP_SKILLS = "QWERTYUIOP"
KEYMAP_TACTICS = "ZXCVBNM"

SKILL_PATTERN = re.compile("skill(\d) \((-?\d+),(-?\d+)\)")

class Gui(object):
  def __init__(self, side, host = None, port = None):
    if host is not None:
      self.network = Network(host, port)
    else:
      self.network = None
    self.side = side
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Rogue Force')
    libtcod.sys_set_fps(LIMIT_FPS)

    self.con_root = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    self.con_bg = libtcod.console_new(BG_WIDTH, BG_HEIGHT)
    self.con_msgs = libtcod.console_new(MSG_WIDTH, MSG_HEIGHT)
    self.con_panels = [libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT), libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT)]

    self.bg = Battleground(BG_WIDTH, BG_HEIGHT)
    for x in range(10,5,-1):
      for y in range(10,31):
        self.bg.minions.append(Ranged_Minion(self.bg, x, y, 0, "human"))
    for x in range(49,54):
      for y in range(10,31):
        self.bg.minions.append(Minion(self.bg, x, y, 1, "monkey"))

    self.bg.generals = [General(self.bg, 3, 20, 0, "Gemekaa", libtcod.green), General(self.bg, 56, 20, 1, "Fapencio", libtcod.orange)]
    self.keymap_skills = KEYMAP_SKILLS[0:len(self.bg.generals[self.side].skills)]
    self.keymap_tactics = KEYMAP_TACTICS[0:len(self.bg.generals[self.side].tactics)]
    self.game_msgs = []
    self.render_all()

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

  def clean_all(self):
    for e in copy.copy(self.bg.effects):
      if not e.alive:
        self.bg.effects.remove(e)
    for m in copy.copy(self.bg.minions):
      if not m.alive:
        self.bg.minions.remove(m)

  def loop(self):
    turn = 0
    turn_time = 0.1
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    while True:
      messages = ["", ""]
      start = time.time()
      while time.time() - start < turn_time:
        libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
        (x, y) = (mouse.cx-BG_OFFSET_X, mouse.cy-BG_OFFSET_Y)
        if self.bg.is_inside(x,y): self.bg.tile_hovered(x, y)
        if key.vk == libtcod.KEY_ESCAPE: exit()
        n = self.keymap_skills.find(chr(key.c).upper()) # Number of the skill pressed
        if n != -1: 
          messages[self.side] += "skill{0} ({1},{2})\n".format(n, x, y)
        n = self.keymap_tactics.find(chr(key.c).upper()) # Number of the tactic pressed
        if n != -1: 
          messages[self.side] += "tactic{0}\n".format(n)
      messages[self.side] += "DONE\n"

      if self.network != None:
        self.network.send(messages[self.side])
        messages[(self.side+1)%2] = self.network.recv()
      else:
        messages[(self.side+1)%2] = "DONE\n"
      turn +=1
      self.process_messages(messages)
      self.update_all()
      if (turn % 100) == 0: self.clean_all()
      self.render_all()

  def process_messages(self, messages):
    for i in [0,1]:
      for m in messages[i].split("\n"):
        match = SKILL_PATTERN.match(m)
        if match is not None:
          if self.bg.generals[i].use_skill(*map(int, match.groups())):
            self.message(self.bg.generals[i].name + ": " + self.bg.generals[i].skill_quotes[int(match.group(1))], self.bg.generals[i].color)
        elif m.startswith("tactic"):
          self.bg.generals[i].command_tactic(int(m[6]))

  def render_all(self):
    self.bg.draw(self.con_bg)
    self.render_msgs()
    self.render_panels()
    libtcod.console_blit(self.con_bg, 0, 0, BG_WIDTH, BG_HEIGHT, self.con_root, BG_OFFSET_X, BG_OFFSET_Y)
    for i in [0,1]:
      libtcod.console_blit(self.con_panels[i], 0, 0, PANEL_WIDTH, PANEL_HEIGHT, self.con_root, (PANEL_WIDTH+BG_WIDTH)*i, 0)
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
        self.render_bar(self.con_panels[i], bar_offset_x, line, bar_length, self.bg.generals[i].cd[s], self.bg.generals[i].max_cd[s],
          libtcod.dark_blue, libtcod.sky, libtcod.black)
        line += 2
      self.render_tactics(i)

  def render_tactics(self, i):
    bar_offset_x = 3
    line = 9 + len(self.bg.generals[i].skills)
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
  if len(sys.argv) == 4: 
    gui = Gui(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
  else:
    gui = Gui(int(sys.argv[1]))
  gui.loop()

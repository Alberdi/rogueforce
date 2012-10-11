from battleground import Battleground
from general import General
from minion import Minion

import libtcodpy as libtcod
import random
import socket
import sys
import time

BG_WIDTH = 60
BG_HEIGHT = 43
PANEL_WIDTH = 16
PANEL_HEIGHT = BG_HEIGHT
SCREEN_WIDTH = BG_WIDTH + PANEL_WIDTH*2
SCREEN_HEIGHT = BG_HEIGHT

BG_OFFSET_X = PANEL_WIDTH
BG_OFFSET_Y = 0

LIMIT_FPS = 20

KEYMAP_SKILLS = "QWERTYUIOP"
KEYMAP_TACTICS = "ZXCVBNM"

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
    self.con_panels = [libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT), libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT)]

    self.bg = Battleground(BG_WIDTH, BG_HEIGHT)
    for x in range(10,5,-1):
      for y in range(10,31):
        self.bg.minions.append(Minion(self.bg, x, y, 0, "human"))
    for x in range(49,54):
      for y in range(10,31):
        self.bg.minions.append(Minion(self.bg, x, y, 1, "monkey"))

    self.bg.generals = [General(self.bg, 3, 20, 0, "Gemekaa"), General(self.bg, 56, 20, 1, "Fapencio")]
    self.keymap_skills = KEYMAP_SKILLS[0:len(self.bg.generals[self.side].skills)]
    self.keymap_tactics = KEYMAP_TACTICS[0:len(self.bg.generals[self.side].tactics)]
    self.render_all()

  def loop(self):
    turn = 0
    turn_time = 0.1
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    while True:
      messages = ["", ""]
      start = time.time()
      while time.time() - start < turn_time:
        if BG_OFFSET_X <= mouse.cx < BG_WIDTH + BG_OFFSET_X and BG_OFFSET_Y <= mouse.cy < BG_HEIGHT + BG_OFFSET_Y:
          self.bg.tile_hovered(mouse.cx-BG_OFFSET_X, mouse.cy-BG_OFFSET_Y)
        libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
        if key.vk == libtcod.KEY_ESCAPE:
          exit()
        n = self.keymap_skills.find(chr(key.c).upper()) # Number of the skill pressed
        if n != -1: 
          messages[self.side] += "skill" + str(n) + "\n"
        n = self.keymap_tactics.find(chr(key.c).upper()) # Number of the tactic pressed
        if n != -1: 
          messages[self.side] += "tactic" + str(n) + "\n"
      messages[self.side] += "DONE\n"

      if self.network != None:
        self.network.send(messages[self.side])
        messages[(self.side+1)%2] = self.network.recv()
      else:
        messages[(self.side+1)%2] = "DONE\n"

      turn +=1
      self.process_messages(messages)
      self.update_all()
      self.render_all()

  def process_messages(self, messages):
    for i in [0,1]:
      for m in messages[i].split("\n"):
        if m.startswith("skill"):
          self.bg.generals[i].use_skill(int(m[5]))
        elif m.startswith("tactic"):
          self.bg.generals[i].command_tactic(int(m[6]))

  def render_all(self):
    self.bg.draw(self.con_bg)
    self.render_panels()
    libtcod.console_blit(self.con_bg, 0, 0, BG_WIDTH, BG_HEIGHT, self.con_root, BG_OFFSET_X, BG_OFFSET_Y)
    for i in [0,1]:
      libtcod.console_blit(self.con_panels[i], 0, 0, PANEL_WIDTH, PANEL_HEIGHT, self.con_root, (PANEL_WIDTH+BG_WIDTH)*i, 0)
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

  def update_all(self):
    for m in self.bg.minions:
      m.update()
    for g in self.bg.generals:
      g.update()

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

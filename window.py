from area import SingleTarget
from battleground import Battleground

import libtcodpy as libtcod

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

TURN_LAG = 1

class Window(object):
  def __init__(self, battleground, side, host = None, port = None, window_id = 0):
    if host is not None:
      self.network = Network(host, port)
    else:
      self.network = None
    self.bg = battleground
    self.side = side
    self.window_id = window_id

    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Rogue Force')

    self.messages = [{}, {}]

    self.con_root = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    self.con_bg = libtcod.console_new(BG_WIDTH, BG_HEIGHT)
    self.con_info = libtcod.console_new(INFO_WIDTH, INFO_HEIGHT)
    self.con_msgs = libtcod.console_new(MSG_WIDTH, MSG_HEIGHT)
    self.con_panels = [libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT), libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT)]

    self.game_msgs = []
    self.game_over = False
    self.area_hover_color = libtcod.green
    self.area_hover_color_invalid = libtcod.red
    self.default_hover_color = libtcod.blue
    self.default_hover_function = SingleTarget(self.bg).get_all_tiles

    #self.render_all(0,0)

  def check_input(self, key, x, y):
    return None

  def check_winner(self):
    return None

  def clean_all(self):
    return False

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
        if key.vk == libtcod.KEY_ESCAPE:
          return None
        s = self.check_input(key, x, y)
        if s is not None:
          self.messages[self.side][turn] = s

      if self.network != None:
        if turn in self.messages[self.side]:
          self.network.send(str(turn) + "#"  + self.messages[self.side][turn])
        else:
          self.network.send("D")

      self.process_messages(turn - TURN_LAG)
      self.update_all()
      winner = self.check_winner()
      if (turn % 100) == 0: self.clean_all()
      self.do_hover(hover_function, x, y)
      turn +=1
      self.render_all(x, y)

    return winner

  def process_messages(self, turn):
    return False

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
      self.render_side_panel(i, bar_length, bar_offset_x)

  def render_side_panel(self, i, bar_length, bar_offset_x):
    pass

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


from battleground import Battleground
from general import General
from minion import Minion

import libtcodpy as libtcod
import random

BG_WIDTH = 60
BG_HEIGHT = 43
PANEL_WIDTH = 16
PANEL_HEIGHT = BG_HEIGHT
SCREEN_WIDTH = BG_WIDTH + PANEL_WIDTH*2
SCREEN_HEIGHT = BG_HEIGHT

BG_OFFSET_X = PANEL_WIDTH
BG_OFFSET_Y = 0

LIMIT_FPS = 20

class Gui(object):
  def __init__(self):
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Rogue Force')
    libtcod.sys_set_fps(LIMIT_FPS)

    self.con_root = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    self.con_bg = libtcod.console_new(BG_WIDTH, BG_HEIGHT)
    self.con_panels = [libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT), libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT)]

    self.bg = Battleground(BG_WIDTH, BG_HEIGHT)
    self.entities = []
    for x in range(10,5,-1):
      for y in range(10,31):
        self.entities.append(Minion(self.bg, x, y, 1, "human"))
    for x in range(49,54):
      for y in range(10,31):
        self.entities.append(Minion(self.bg, x, y, -1, "monkey"))

    self.generals = [General(self.bg, 3, 20, 1, "Gemekaa"), General(self.bg, 56, 20, -1, "Fapencio")]

  def loop(self):
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    while not libtcod.console_is_window_closed():
      libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
      if BG_OFFSET_X <= mouse.cx < BG_WIDTH + BG_OFFSET_X and BG_OFFSET_Y <= mouse.cy < BG_HEIGHT + BG_OFFSET_Y:
        self.bg.tile_hovered(mouse.cx-BG_OFFSET_X, mouse.cy-BG_OFFSET_Y)
    
      if key.c == ord('q'):
        self.generals[0].skill1()
      elif key.vk == libtcod.KEY_ESCAPE:
        exit()

      for e in self.entities:
        e.update()
      for g in self.generals:
        g.update()

      self.bg.draw(self.con_bg)

      self.render_left_panel()
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

  def render_left_panel(self):
    bar_length = 11
    bar_offset_x = 4
    for i in [0,1]:
      libtcod.console_set_default_foreground(self.con_panels[i], libtcod.black)
      self.render_bar(self.con_panels[i], bar_offset_x, 1, bar_length, self.generals[i].hp, self.generals[i].max_hp,
        libtcod.red, libtcod.yellow, libtcod.black)
      self.render_bar(self.con_panels[i], bar_offset_x, 3, bar_length, self.generals[i].cd1, self.generals[i].max_cd1,
        libtcod.dark_blue, libtcod.sky, libtcod.black)
 
if __name__=="__main__":
  gui = Gui()
  gui.loop()

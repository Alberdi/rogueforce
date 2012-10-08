from battleground import Battleground
from general import General
from minion import Minion

import libtcodpy as libtcod
import random

SCREEN_WIDTH = 92
SCREEN_HEIGHT = 50

BG_WIDTH = 60
BG_HEIGHT = 43

PANEL_WIDTH = 16
PANEL_HEIGHT = BG_HEIGHT

LIMIT_FPS = 20


libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Rogue Force')
libtcod.sys_set_fps(LIMIT_FPS)

con_root = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
con_bg = libtcod.console_new(BG_WIDTH, BG_HEIGHT)
con_left_panel = libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT)

key = libtcod.Key()
mouse = libtcod.Mouse()

bg = Battleground(BG_WIDTH, BG_HEIGHT)
l = []
for x in range(10,5,-1):
  for y in range(10,31):
    l.append(Minion(bg, x, y, 1, "human"))
for x in range(49,54):
  for y in range(10,31):
    l.append(Minion(bg, x, y, -1, "monkey"))

general_left = General(bg, 3, 20, 1, "Gemekaa")
general_right = General(bg, 56, 20, -1, "Fapencio")
l.append(general_left)
l.append(general_right)

while not libtcod.console_is_window_closed():
  libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
  if PANEL_WIDTH <= mouse.cx < BG_WIDTH + PANEL_WIDTH and 0 <= mouse.cy < BG_HEIGHT:
    bg.tile_hovered(mouse.cx-PANEL_WIDTH, mouse.cy)
    
  if key.c == ord('q'):
    general_left.skill1()
  elif key.vk == libtcod.KEY_ESCAPE:
    exit()

  for m in l:
    m.update()
  bg.draw(con_bg)

  libtcod.console_blit(con_bg, 0, 0, BG_WIDTH, BG_HEIGHT, con_root, PANEL_WIDTH, 0)
  libtcod.console_blit(con_left_panel, 0, 0, PANEL_WIDTH, PANEL_HEIGHT, con_root, 0, 0)
  libtcod.console_blit(con_root, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
  libtcod.console_flush()
   

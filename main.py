from battleground import Battleground
from minion import Minion
import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Rogue Force', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

bg = Battleground(60, 40)
l = []
for x in range(10,15):
  for y in range(10,30):
    l.append(Minion(bg, x, y, 0, "human"))

while not libtcod.console_is_window_closed():
  for m in l:
    m.update()
  bg.draw(con)
  for m in l:
    m.draw(con)

  libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
  libtcod.console_flush()
    

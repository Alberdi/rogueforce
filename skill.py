from effect import *
from entity import *

def heal_all_minions(general, amount):
  for m in general.bg.minions:
    m.get_healed(amount)
  return True

def heal_target_minion(general, x, y, amount):
  if not general.bg.is_inside(x, y): return False
  minion = general.bg.tiles[x, y].entity
  if minion is not None and minion.side == general.side and minion != general and minion.hp != minion.max_hp:
    minion.get_healed(amount)
    return True
  return False

def mine(general, x, y, power):
  if not general.bg.is_inside(x, y) or general.bg.tiles[(x, y)].entity is not None: return False
  Mine(general.bg, x, y, power)
  return True

def sonic_waves(general, power, waves):
  for i in range(0, waves):
    x = general.x+1-(i+1)/2 if general.side == 0 else general.x-1+(i+1)/2
    y = general.y+(((i+1)/2)*(-1 if i%2 == 0 else 1))
    if general.bg.is_inside(x,y):
      general.bg.effects.append(Wave(general.bg, x, y, general.side, power))
  return waves > 0

from effect import *
from entity import *

import area
import status

class Skill(object):
  def __init__(self, general, function, max_cd, parameters=[], quote="", description="", area=None):
    self.general = general
    self.function = function
    self.original_max_cd = max_cd
    self.max_cd = max_cd
    self.cd = 0
    self.parameters = parameters
    self.area = area
    self.quote = quote
    self.description = description

  def apply_function(self, tiles):
    did_anything = False
    for t in tiles:
      did_anything += self.function(self.general, t, *self.parameters)
    return did_anything

  def change_cd(self, delta):
    self.cd += delta
    self.cd = 0 if self.cd < 0 else self.max_cd if self.cd > self.max_cd else self.cd

  def change_max_cd(self, delta):
    self.max_cd += delta

  def get_area_tiles(self, x, y):
    if self.area is None: return None
    return self.area.get_tiles(x, y)

  def reset_cd(self):
    self.cd = 0

  def update(self):
    if self.cd < self.max_cd: self.cd += 1

  def use(self, x, y):
    if self.area is None:
      return self.function(self.general, *self.parameters)
    return self.apply_function(self.area.get_tiles(x, y))


def add_path(general, tile, entity):
  entity.path.append(tile)
  return True

def apply_status(general, tile, status):
  status.clone(tile.entity)
  return True

def consume(general, tile, hp_gain=1, delta_cd=1):
  tile.entity.die()
  general.get_healed(hp_gain)
  for s in general.skills:
    s.change_cd(delta_cd)
  return True

def create_minions(general, l):
  did_anything = False
  for (x, y) in l:
    minion_placed = general.minion.clone(x, y)
    if minion_placed is not None:
      general.bg.minions.append(minion_placed)
      general.minions_alive += 1
      did_anything = True
  return did_anything

def darkness(general, tile, duration):
  if tile.passable:
    d = Darkness(general.bg, tile.x, tile.y, duration)
    general.bg.effects.append(d)
  return tile.passable

def heal(general, tile, amount):
  if tile.entity.hp == tile.entity.max_hp: return False
  tile.entity.get_healed(amount)
  return True

def minion_glider(general, tile, go_bottom = True):
  (x, y) = (tile.x, tile.y)
  if not general.bg.is_inside(x-1, y-1) or not general.bg.is_inside(x+1, y+1): return False
  j = 1 if go_bottom else -1
  i = 1 if general.side == 0 else -1
  return create_minions(general, [(x-i, y-j), (x, y-j), (x, y), (x+i, y), (x-i, y+j)])

def minion_lwss(general, tile):
  (x, y) = (tile.x, tile.y)
  if not general.bg.is_inside(x-2, y-2) or not general.bg.is_inside(x+2, y+2): return False
  j = 1 if general.side == 0 else -1
  return create_minions(general,\
    [(x-1*j, y-1), (x, y-1), (x+1*j, y-1), (x+2*j, y-1), (x-2*j, y), (x+2*j, y), (x+2*j, y+1), (x-2*j, y+2), (x+1*j, y+2)])

def null(general):
  return True

def place_entity(general, tile, entity):
  clone = entity.clone(tile.x, tile.y)
  return clone is not None

def recall_entity(general, tile):
  for m in general.bg.minions:
    if m.is_ally(general):
      for s in m.statuses:
        if s.name == "Vanished" and m.teleport(tile.x, tile.y):
          s.end()
          m.teleport(tile.x, tile.y)
          return True
  return False

def restock_minions(general, number):
  #TODO: this can be a lot cleaner
  tmp = general.minions_alive
  general.minions_alive = number
  general.formation.place_minions()
  general.minions_alive = tmp
  general.command_tactic([i for i,x in enumerate(general.tactics) if x == general.selected_tactic][0])
  general.recount_minions_alive()
  return True

def sonic_waves(general, power, waves):
  for i in range(0, waves):
    x = general.x+1-(i+1)/2 if general.side == 0 else general.x-1+(i+1)/2
    y = general.y+(((i+1)/2)*(-1 if i%2 == 0 else 1))
    if general.bg.is_inside(x,y):
      general.bg.effects.append(Wave(general.bg, general.side, x, y, power))
  return waves > 0

def water_pusher(general, tile):
  did_anything = False
  for i in [-1, 0, 1]:
    for j in [-1, 0, 1]:
      if not general.bg.is_inside(tile.x + i, tile.y + j): continue
      entity = general.bg.tiles[(tile.x + i, tile.y + j)].entity
      if entity is not None and (i, j) != (0, 0) and entity.can_be_pushed(i, j):
        entity.get_pushed(i, j)
        did_anything = True
  return did_anything


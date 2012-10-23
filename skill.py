from effect import *
from entity import *

class Skill(object):
  def __init__(self, general, function, max_cd, parameters=[], quote="", area=None):
    self.general = general
    self.function = function
    self.max_cd = max_cd
    self.cd = 0
    self.parameters = parameters
    self.area = area
    self.quote = quote

  def apply_function(self, tiles):
    did_anything = False
    for t in tiles:
      did_anything += self.function(self.general, t, *self.parameters)
    return did_anything

  def change_cd(self, delta):
    self.cd += delta
    self.cd = 0 if self.cd < 0 else self.max_cd if self.cd > self.max_cd else self.cd

  def reset_cd(self):
    self.cd = 0

  def update(self):
    if self.cd < self.max_cd: self.cd += 1

  def use(self, x, y):
    if self.area is None:
      return self.function(self.general, *self.parameters)
    return self.apply_function(self.area.get_tiles(x, y))
    #return self.function(general, self.area.get_tiles(x, y), *parameters)

def apply_status(general, tile, status):
  status.clone(tile.entity)
  return True

def consume(general, tile, hp_gain=1, delta_cd=1):
  tile.entity.die()
  general.get_healed(hp_gain)
  for s in general.skills:
    s.change_cd(delta_cd)
  return True

def darkness(general, tile, duration):
  if tile.passable:
    d = Darkness(general.bg, tile.x, tile.y, duration)
    general.bg.effects.append(d)
  return tile.passable

def heal(general, tile, amount):
  if tile.entity.hp == tile.entity.max_hp: return False
  tile.entity.get_healed(amount)
  return True

def place_entity(general, tile, entity):
  clone = entity.clone(tile.x, tile.y)
  return clone is not None

def sonic_waves(general, power, waves):
  for i in range(0, waves):
    x = general.x+1-(i+1)/2 if general.side == 0 else general.x-1+(i+1)/2
    y = general.y+(((i+1)/2)*(-1 if i%2 == 0 else 1))
    if general.bg.is_inside(x,y):
      general.bg.effects.append(Wave(general.bg, x, y, general.side, power))
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

#### Old functions ####

def apply_status_target(general, x, y, status):
  entity = general.bg.tiles[(x, y)].entity
  if entity is None: return False
  status.clone(entity)
  return True


def create_minion(general, x, y):
  if general.bg.tiles[(x, y)].entity is not None or not general.bg.tiles[(x, y)].passable: return False
  general.bg.minions.append(general.minion.clone(x, y))
  return True

def create_minions(general, l):
  did_anything = False
  for (x, y) in l:
    did_anything += create_minion(general, x, y)
  return did_anything > 0

def heal_all_minions(general, amount):
  for m in general.bg.minions:
    m.get_healed(amount)
  return True

def heal_target_minion(general, x, y, amount):
  minion = general.bg.tiles[x, y].entity
  if minion is not None and minion.side == general.side and minion != general and minion.hp != minion.max_hp:
    minion.get_healed(amount)
    return True
  return False

def minion_glider(general, x, y, go_bottom = True):
  if not general.bg.is_inside(x-1, y-1) or not general.bg.is_inside(x+1, y+1): return False
  j = 1 if go_bottom else -1
  i = 1 if general.side == 0 else -1
  return create_minions(general, [(x-i, y-j), (x, y-j), (x, y), (x+i, y), (x-i, y+j)])

def minion_lwss(general, x, y):
  if not general.bg.is_inside(x-2, y-2) or not general.bg.is_inside(x+2, y+2): return False
  j = 1 if general.side == 0 else -1
  return create_minions(general,\
    [(x-1*j, y-1), (x, y-1), (x+1*j, y-1), (x+2*j, y-1), (x-2*j, y), (x+2*j, y), (x+2*j, y+1), (x-2*j, y+2), (x+1*j, y+2)])

def null(general):
  return True

def restock_minions(general, number):
  tmp = general.starting_minions
  general.starting_minions = number
  general.formation.place_minions()
  general.starting_minions = tmp
  general.command_tactic([i for i,x in enumerate(general.tactics) if x == general.selected_tactic][0])
  return True


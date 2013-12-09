import area

class Sieve(object):
  def __init__(self, general, function):
    self.general = general
    self.function = function

  def apply(self, tile):
    return self.function(self.general, tile)


def is_ally_general(general, tile):
  if tile.entity is None: return False
  return tile.entity == general

def is_ally_minion(general, tile):
  if tile.entity is None: return False
  return tile.entity in general.bg.minions and tile.entity.is_ally(general)
  
def is_empty(general, tile):
  return tile.entity is None

def is_enemy(general, tile):
  return tile.entity is not None and not tile.entity.is_ally(general)

def is_enemy_general(general, tile):
  return tile.entity == general.bg.generals[(general.side+1)%2]

def is_inrange(general, tile, radius):
  a = area.Circle(general.bg, radius=radius)
  return tile in a.get_tiles(general.x, general.y)

def is_inrange_close(general, tile):
  return is_inrange(general, tile, 8)

def is_inrange_long(general, tile):
  return is_inrange(general, tile, 30)

def is_minion(general, tile):
  return tile.entity is not None and tile.entity in general.bg.minions


class Sieve(object):
  def __init__(self, general, function):
    self.general = general
    self.function = function

  def apply(self, tile):
    return self.function(self.general, tile)

def is_ally_minion(general, tile):
  if tile.entity is None: return False
  return tile.entity in general.bg.minions and tile.entity.is_ally(general)
  
  

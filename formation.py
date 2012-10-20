class Formation(object):
  def __init__(self, general):
    self.general = general

  def place_minions(self): pass

  def mirror(self, x, y):
    return (self.general.bg.width - x - 1, self.general.bg.height - y - 1) if self.general.side else (x, y)

class Rows(Formation):
  def __init__(self, general, rows=21):
    super(Rows, self).__init__(general)
    self.rows = rows

  def place_minions(self):
    n = self.general.starting_minions
    for x in range(5, 15):
      offset_y = 0
      r = self.rows
      while r > 0:
        if n <= 0: return
        (pos_x, pos_y) = self.mirror(x, self.general.y + offset_y)
        if self.general.bg.tiles[(pos_x, pos_y)].entity is None:
          self.general.bg.minions.append(self.general.minion.clone(pos_x, pos_y))
          n -= 1
        offset_y = abs(offset_y)+1 if r%2 or not self.rows%2 else -offset_y
        r -= 1


class Formation(object):
  def __init__(self, general):
    self.general = general

  def place_minions(self): pass

  def mirror(self, x, y):
    return (self.general.bg.width - x - 1, self.general.bg.height - y - 1) if self.general.side else (x, y)

class Flying_Wedge(Formation):
  def __init__(self, general, increment=1):
    super(Flying_Wedge, self).__init__(general)
    self.increment = increment

  def place_minions(self):
    n = self.general.starting_minions
    for i in range(14, 3, -1):
      offset_y = 0
      for x in range(i, 3, -1):
        for j in range(0, self.increment + 1):
          if n <= 0: return
          minion_placed = self.general.minion.clone(*self.mirror(x, self.general.y + offset_y))
          if minion_placed is not None:
            self.general.bg.minions.append(minion_placed)
            n -= 1
          offset_y = abs(offset_y)+1 if j%2 else -offset_y

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
        minion_placed = self.general.minion.clone(*self.mirror(x, self.general.y + offset_y))
        if minion_placed is not None:
          self.general.bg.minions.append(minion_placed)
          n -= 1
        offset_y = abs(offset_y)+1 if r%2 or not self.rows%2 else -offset_y
        r -= 1


class Formation(object):
  def __init__(self, general):
    self.general = general

  def place_minions(self): pass

  def mirror(self, x, y):
    return (self.general.bg.width - x - 1, self.general.bg.height - y - 1) if self.general.side else (x, y)

class Files(Formation):
  def place_minions(self):
    n = self.general.starting_minions
    if n <= 0: return
    for x in range(13, 6, -1):
      for y in range(10, 33):
        self.general.bg.minions.append(self.general.minion.clone(*self.mirror(x, y)))
        n -= 1
        if n <= 0: return


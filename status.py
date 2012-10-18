class Status(object):
  def __init__(self, minion, duration = 9999):
    self.duration = duration
    self.minion = minion
    if minion != None: # Not a prototype
      self.minion.statuses.append(self)
  
  def clone(self, minion):
    return self.__class__(minion, self.duration)

  def end(self):
    self.duration = -1
    self.minion.statuses.remove(self)

  def tick(self): pass

  def update(self):
    if self.duration > 0:
      self.duration -= 1
      self.tick()
      if self.duration <= 0: self.end()

class Poison(Status):
  # tbt = time between ticks
  def __init__(self, minion, power, tbt = 0, ticks = 9999):
    #  Duration is not exact, it lasts a few more updates, but that shouldn't be a problem.
    super(Poison, self).__init__(minion, ticks*(tbt+1))
    self.tbt = tbt
    self.ticks = ticks
    self.power = power
    self.timer = 0

  def clone(self, minion):
    return self.__class__(minion, self.power, self.tbt, self.ticks)

  def tick(self):
    self.timer -= 1
    if self.timer < 0:
      self.minion.get_attacked(self)
      self.timer = self.tbt
      self.ticks -= 1
      if self.ticks == 0: self.duration = -1 # end


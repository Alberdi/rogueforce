class Status(object):
  def __init__(self, entity, duration = 9999):
    self.duration = duration
    self.entity = entity
    if entity != None: # Not a prototype
      self.entity.statuses.append(self)
  
  def clone(self, entity):
    return self.__class__(entity, self.duration)

  def end(self):
    self.duration = -1
    self.entity.statuses.remove(self)

  def tick(self): pass

  def update(self):
    if self.duration > 0:
      self.duration -= 1
      self.tick()
      if self.duration <= 0: self.end()

class Freeze_Cooldowns(Status):
  def __init__(self, entity, duration = 9999):
    super(Freeze_Cooldowns, self).__init__(entity, duration)

  def tick(self):
    for s in self.entity.skills:
      s.change_cd(-1)

class Poison(Status):
  # tbt = time between ticks
  def __init__(self, entity, power, tbt = 0, ticks = 9999):
    #  Duration is not exact, it lasts a few more updates, but that shouldn't be a problem.
    super(Poison, self).__init__(entity, ticks*(tbt+1))
    self.tbt = tbt
    self.ticks = ticks
    self.power = power
    self.timer = 0

  def clone(self, entity):
    return self.__class__(entity, self.power, self.tbt, self.ticks)

  def tick(self):
    self.timer -= 1
    if self.timer < 0:
      self.entity.get_attacked(self)
      self.timer = self.tbt
      self.ticks -= 1
      if self.ticks == 0: self.duration = -1 # end


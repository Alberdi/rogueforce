from entity import Entity

class Minion(Entity):

  def __init__(self, battleground, x, y, side, name):
    super(Minion, self).__init__(battleground, x, y, name[0])
    self.name = name
    self.side = side
    self.next_move = 20

  def update(self):
    if self.next_move <= 0:
      self.move(self.side, 0)
      self.next_move = 20
    else: self.next_move -= 1

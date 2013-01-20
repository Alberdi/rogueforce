from factions import oracles

class Faction(object):
  def __init__(self, battleground, side, generals, name="Faction"):
    self.bg = battleground
    self.side = side
    self.generals = generals

class Oracles(Faction):
  def __init__(self, battleground, side):
    generals = []
    generals.append(oracles.Gemekaa(battleground, side))
    super(Oracles, self).__init__(battleground, side, generals)

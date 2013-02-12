from factions import oracles
from factions import saviours
import general

class Faction(object):
  def __init__(self, battleground, side, generals, name="Faction"):
    self.bg = battleground
    self.side = side
    self.generals = generals

class Oracles(Faction):
  def __init__(self, battleground, side):
    generals = []
    generals.append(oracles.Gemekaa(battleground, side))
    generals.append(general.General(battleground, side))
    generals.append(general.Emperor(battleground, side))
    super(Oracles, self).__init__(battleground, side, generals, "Oracles")

class Saviours(Faction):
  def __init__(self, battleground, side):
    generals = []
    generals.append(saviours.Ares(battleground, side))
    generals.append(general.General(battleground, side))
    generals.append(general.Emperor(battleground, side))
    super(Saviours, self).__init__(battleground, side, generals, "Saviours")
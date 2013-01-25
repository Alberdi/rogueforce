from factions import oracles
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
    generals.append(oracles.Hunzuu(battleground, side))
    generals.append(general.General(battleground, side))
    generals.append(general.Emperor(battleground, side))
    super(Oracles, self).__init__(battleground, side, generals)

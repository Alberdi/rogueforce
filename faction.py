from factions import doto
from factions import mechanics
from factions import oracles
from factions import saviours
from factions import wizerds
import general

class Faction(object):
  def __init__(self, battleground, side, generals, name="Faction"):
    self.bg = battleground
    self.side = side
    self.generals = generals

class Doto(Faction):
  def __init__(self, battleground, side):
    generals = [doto.Ox(battleground, side),
                doto.Bloodrotter(battlegound, side)]
    super(Doto, self).__init__(battleground, side, generals, "Doto")

class Mechanics(Faction):
  def __init__(self, battleground, side):
    generals = [mechanics.Flappy(battleground, side)]
    super(Mechanics, self).__init__(battleground, side, generals, "Mechanics")

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

class Wizerds(Faction):
  def __init__(self, battleground, side):
    generals = [wizerds.Flappy(battleground, side)]
    super(Wizerds, self).__init__(battleground, side, generals, "Wizerds")

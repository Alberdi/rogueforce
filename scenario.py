from battle import BattleWindow
from battleground import Battleground
from general import *
from window import *

import os
import thread

class Scenario(Window):
  def __init__(self, battleground, side, host = None, port = None, window_id = 0):
    super(Scenario, self).__init__(battleground, side, host, port, window_id)

  def start_battle(self, generals):
    return self.start_battle_thread(generals)
    #thread.start_new_thread(self.start_battle_thread, ())
    #Very dirty non-portable non-even-workaround for the line above
    #thread.start_new_thread(os.system, ("python battle.py 0",))

  def start_battle_thread(self, generals):
    battleground = Battleground(BG_WIDTH, BG_HEIGHT)
    battleground.generals = generals
    scenario_pos = []
    for g in generals:
      scenario_pos.append((g.x, g.y))
      g.change_battleground(battleground, 52 if g.side == 0 else 56, g.y)
    battle = BattleWindow(battleground, 0)
    winner = battle.loop()
    for i in [0,1]:
      generals[i].change_battleground(self.bg, *(scenario_pos[i]))
      if not generals[i].alive:
        generals[i].die()
   
  def update_all(self):
    for i in [0,1]:
      if not self.bg.generals[i].alive: continue
      dx = 1 if self.bg.generals[i].side == 0 else -1
      if self.bg.generals[i].x + dx == self.bg.generals[(i+1)%2].x:
        winner = self.start_battle([self.bg.generals[0], self.bg.generals[1]])
      self.bg.generals[i].move(1 if self.bg.generals[i].side == 0 else -1, 0)
    #super(Scenario, self).update_all()


if __name__=="__main__":
  battleground = Battleground(BG_WIDTH, BG_HEIGHT)
  battleground.generals = [General(battleground, 3, 21, 0), General(battleground, 56, 21, 1)] 
  side = 0
  scenario = Scenario(battleground, side) 
  scenario.loop()

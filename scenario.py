from battle import BattleWindow
from battleground import Battleground
from general import *
from window import *

class Scenario(Window):
  def __init__(self, battleground, side, host = None, port = None, window_id = 0):
    super(Scenario, self).__init__(battleground, side, host, port, window_id)
    for g in self.bg.generals:
      g.start_scenario()

  def start_battle(self, generals):
    return self.start_battle_thread(generals)
    #thread.start_new_thread(self.start_battle_thread, (generals,))

  def start_battle_thread(self, generals):
    battleground = Battleground(BG_WIDTH, BG_HEIGHT)
    battleground.generals = generals
    scenario_pos = []
    for g in generals:
      scenario_pos.append((g.x, g.y))
      g.change_battleground(battleground, 40 if g.side == 0 else 56, g.y)
    battle = BattleWindow(battleground, 0)
    winner = battle.loop()
    for i in [0,1]:
      generals[i].change_battleground(self.bg, *(scenario_pos[i]))
      if not generals[i].alive:
        generals[i].die()
   
  def update_all(self):
    for g in self.bg.generals:
      if not g.alive: continue
      enemy = g.enemy_reachable()
      if enemy is not None:
        self.start_battle([g, enemy])
      else:
        g.move(1 if g.side == 0 else -1, 0)


if __name__=="__main__":
  battleground = Battleground(BG_WIDTH, BG_HEIGHT)
  battleground.generals = [General(battleground, 3, 21, 0), General(battleground, 43, 21, 0), General(battleground, 56, 21, 1)] 
  side = 0
  scenario = Scenario(battleground, side) 
  scenario.loop()

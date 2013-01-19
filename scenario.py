from battle import BattleWindow
from battleground import Battleground
from general import *
from window import *

KEYMAP_GENERALS = "QWERTYUIOP"

class Scenario(Window):
  def __init__(self, battleground, side, reserve, host = None, port = None, window_id = 0):
    super(Scenario, self).__init__(battleground, side, host, port, window_id)
    self.reserve = reserve
    self.requisition = [450, 300]
    self.max_requisition = 999
    self.keymap_generals = KEYMAP_GENERALS
    for g in reserve[0]:
      g.start_scenario()
    for g in reserve[1]:
      g.start_scenario()

  def apply_requisition(self, general):
    if general.deployed: return
    if general.requisition + self.requisition[general.side] >= general.cost:
      if self.deploy_general(general):
        self.requisition[general.side] -= general.cost - general.requisition
        general.requisition = general.cost
      else: #If can't be deployed, we give all but one requisition points
        self.requisition[general.side] -= general.cost - general.requisition - 1
        general.requisition = general.cost - 1
    else:
      general.requisition += self.requisition[general.side]
      self.requisition[general.side] = 0
      

  def check_input(self, key, x, y):
    n = self.keymap_generals.find(chr(key.c).upper()) # Number of the general pressed
    if n != -1:
      return "apply_req{0}\n".format(n)
    return None

  def deploy_general(self, general):
    if general.teleport(3, 21):
      general.deployed = True
      self.bg.generals.append(general)
      return True
    return False

  def increment_requisition(self, i):
    self.requisition[i] += 1
    if self.requisition[i] > self.max_requisition:
      self.requisition[i] = self.max_requisition

  def process_messages(self, turn):
    for i in [0,1]:
      if turn in self.messages[i]:
        if self.messages[i][turn].startswith("apply_req"):
          self.apply_requisition(self.reserve[i][int(self.messages[i][turn][9])])

  def render_side_panel(self, i, bar_length, bar_offset_x):
    libtcod.console_set_default_foreground(self.con_panels[i], libtcod.white)
    libtcod.console_print(self.con_panels[i], bar_offset_x-1, 0, " Requisition")
    libtcod.console_set_default_foreground(self.con_panels[i], libtcod.black)
    self.render_bar(self.con_panels[i], bar_offset_x, 1, bar_length, self.requisition[i], self.max_requisition, libtcod.dark_blue, libtcod.sky, libtcod.black)
    line = 4
    j = 0
    for g in self.reserve[i]:
      libtcod.console_set_default_foreground(self.con_panels[i], libtcod.white)
      libtcod.console_print(self.con_panels[i], bar_offset_x-1, line, " " + g.name)
      libtcod.console_set_default_foreground(self.con_panels[i], libtcod.black)
      libtcod.console_put_char_ex(self.con_panels[i], bar_offset_x-1, line+1, self.keymap_generals[j], g.color, libtcod.black)
      self.render_bar(self.con_panels[i], bar_offset_x, line+1, bar_length, g.requisition, g.cost, libtcod.dark_blue, libtcod.sky, libtcod.black)
      j += 1
      line += 3

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
    for i in [0,1]:
      self.increment_requisition(i)
    for g in self.bg.generals:
      if not g.alive: continue
      enemy = g.enemy_reachable()
      if enemy is not None:
        self.start_battle([g, enemy])
      else:
        g.move(1 if g.side == 0 else -1, 0)


if __name__=="__main__":
  battleground = Battleground(BG_WIDTH, BG_HEIGHT)
  reserve = []
  reserve.append([General(battleground, 0), Emperor(battleground, 0)])
  reserve.append([General(battleground, 1)])
  side = 0
  scenario = Scenario(battleground, side, reserve) 
  scenario.loop()

from minion import Minion
import libtcodpy as libtcod

class General(Minion):

  def __init__(self, battleground, x, y, side, name):
    super(General, self).__init__(battleground, x, y, side, name)
    self.max_hp = 100
    self.hp = 100
    self.max_cd1 = 100
    self.cd1 = 100

  def update(self):
    if not self.alive: return
    self.cd1 -= 1 
    if self.next_action <= 0:
      self.next_action = 20
      enemy = self.enemy_reachable()
      if enemy != None:
        enemy.get_attacked(self)

  def skill1(self):
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
    if self.cd1 <= 0:
      self.cd1 = self.max_cd1
      minion = self.bg.tiles[(mouse.cx-16, mouse.cy)].entity
      if minion.side == self.side:
        minion.get_healed(100)

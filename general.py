from minion import Minion
import libtcodpy as libtcod

class General(Minion):

  def __init__(self, battleground, x, y, side, name):
    super(General, self).__init__(battleground, x, y, side, name)
    self.max_hp = 100
    self.hp = 100
    self.max_cd1 = 50
    self.cd1 = 0
    self.max_cd2 = 50
    self.cd2 = 0

  def update(self):
    if not self.alive: return
    if self.cd1 < self.max_cd1: self.cd1 += 1 
    if self.cd2 < self.max_cd2: self.cd2 += 1 
    if self.next_action <= 0:
      self.next_action = 20
      enemy = self.enemy_reachable()
      if enemy != None:
        enemy.get_attacked(self)

  def skill1(self):
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
    if self.cd1 >= self.max_cd1:
      minion = self.bg.tiles[(mouse.cx-16, mouse.cy)].entity
      if minion is not None and minion.side == self.side and minion != self:
        self.cd1 = 0
        minion.get_healed(100)
  
  def skill2(self, minions):
    if self.cd2 >= self.max_cd2:
      self.cd2 = 0
      for m in minions:
        m.get_healed(100)

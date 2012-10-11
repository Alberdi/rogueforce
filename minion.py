from entity import Entity
import libtcodpy as libtcod

class Minion(Entity):
  def __init__(self, battleground, x, y, side, name):
    super(Minion, self).__init__(battleground, x, y, side, name[0])
    self.name = name
    self.max_hp = 20
    self.hp = 20
    self.power = 5
    self.alive = True
    self.tactic = "forward"

  def enemy_reachable(self):
    # Order: forward, backward, up, down
    enemy = self.bg.tiles[(self.x + (1 if self.side == 0 else -1), self.y)].entity
    if enemy is None or self.is_ally(enemy): enemy = self.bg.tiles[(self.x + (-1 if self.side == 0 else 1), self.y)].entity
    if enemy is None or self.is_ally(enemy): enemy = self.bg.tiles[(self.x, self.y-1)].entity
    if enemy is None or self.is_ally(enemy): enemy = self.bg.tiles[(self.x, self.y+1)].entity
    if enemy != None and enemy.side != self.side: return enemy
    else: return None
 
  def follow_tactic(self):
    if self.tactic == "forward":
      self.move(1 if self.side == 0 else -1, 0)
    elif self.tactic == "stop":
      self.next_action = 1
    elif self.tactic == "go_sides":
      self.move(0, 1 if self.y >= self.bg.height/2 else -1)
    elif self.tactic == "go_center":
      self.move(0, -1 if self.y >= self.bg.height/2 else 1)

  def get_attacked(self, enemy):
    self.hp -= enemy.power
    if self.hp > 0:
      self.update_color()
    else:
      self.bg.tiles[(self.x, self.y)].entity = None
      # We can't delete self from the list because we are iterating it
      #self.bg.minions.remove(self)
      self.x = -1
      self.alive = False

  def get_healed(self, amount):
    self.hp += amount
    if self.hp > self.max_hp: self.hp = self.max_hp
    self.update_color()

  def update(self):
    if not self.alive: return
    if self.next_action <= 0:
      self.reset_action()
      enemy = self.enemy_reachable()
      if enemy != None:
        enemy.get_attacked(self)
      else:
        self.follow_tactic()
    else: self.next_action -= 1

  def update_color(self):
    # We change the color to indicate that the minion is wounded
    # More red -> closer to death
    c = int(255*(float(self.hp)/self.max_hp))
    self.color = libtcod.Color(255, c, c)
    

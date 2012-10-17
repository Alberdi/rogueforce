from math import copysign

def attack_general(minion):
  minion.move(copysign(1, minion.bg.generals[(minion.side+1)%2].x - minion.x),
              copysign(1, minion.bg.generals[(minion.side+1)%2].y - minion.y))

def backward(minion):
  minion.move(-1 if minion.side == 0 else 1, 0)

def defend_general(minion):
  minion.move(copysign(1, minion.bg.generals[minion.side].x - minion.x),
              copysign(1, minion.bg.generals[minion.side].y - minion.y))

def disperse(minion):
  r = 5
  d = {(1,1):0, (-1,1):0, (-1,-1):0, (1,-1):0}
  for i in range(-r, r+1):
    for j in range(-r, r+1):
      (x, y) = (minion.x+i, minion.y+j)
      if not minion.bg.is_inside(x, y): continue
      entity = minion.bg.tiles[(x, y)].entity
      if entity is not None and entity != minion:
        d[(copysign(1, i), copysign(1, j))] += 1
  minion.move(*min(d, key=d.get))

def forward(minion):
  minion.move(1 if minion.side == 0 else -1, 0)

def go_bottom(minion):
  minion.move(0, 1)

def go_center(minion):
  minion.move(0, -1 if minion.y >= minion.bg.height/2 else 1)

def go_sides(minion):
  minion.move(0, 1 if minion.y >= minion.bg.height/2 else -1)

def go_top(minion):
  minion.move(0, -1)

def null(minion):
  pass
  
def stop(minion):
  minion.next_action = 1

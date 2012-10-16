def backward(minion):
  minion.move(-1 if minion.side == 0 else 1, 0)

def forward(minion):
  minion.move(1 if minion.side == 0 else -1, 0)

def go_center(minion):
  minion.move(0, -1 if minion.y >= minion.bg.height/2 else 1)

def go_sides(minion):
  minion.move(0, 1 if minion.y >= minion.bg.height/2 else -1)

def stop(minion):
  minion.next_action = 1

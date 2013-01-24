from battleground import Battleground
import general
import main
import minion

from easygui import *
import libtcodpy as libtcod

if __name__=="__main__":
  bg = Battleground(main.BG_WIDTH, main.BG_HEIGHT)
  generals = ["General", "Conway", "Emperor"]
  minions = ["Minion", "Ranged_Minion"] 
  title = "Rogue Force launcher"

  g = []
  for i in [0,1]:
    g.append(choicebox("Choose general " + str(i), title, generals))
    g[i] = getattr(general, g[i])(bg, 56 if i else 3, 21, i)

  bg.generals = g

  s = int(choicebox("Select your side", title, [0,1]))
  n = enterbox("Enter server:port address", title).split(":")

  if n is None or n[0] == "":
    game = main.Game(bg, s)
  else:
    game = main.Game(bg, s, n[0], int(n[1]))
  game.loop()

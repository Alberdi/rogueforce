import battleground
import faction

def autodoc_faction(faction):
  print get_header()
  for g in faction.generals:
    autodoc_general(g)
  print get_footer()

def autodoc_general(general):
  general.start_battle()
  print "<ul>"
  print get_pair("Name", str(general.name))
  print get_pair("HP", str(general.max_hp))
  print get_pair("Cost", str(general.cost))
  print get_pair("Minions", general.minion.name + "s")
  print get_pair("Starting minions", str(general.starting_minions))
  print "</ul>"
  for s in general.skills:
    autodoc_skill(s)

def autodoc_skill(skill):
  print skill

def get_footer():
  return "</body></html>"

def get_header():
  return "<html><head></head><body>"

def get_pair(key, value):
  return "<dt>" + key + "</dt>" + " <dd>" + value + "</dd>"

if __name__=='__main__':
  bg = battleground.Battleground(0, 0)
  autodoc_faction(faction.Oracles(bg, 0))


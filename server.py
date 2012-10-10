import socket
import sys
import thread

MSG_EXIT = "EXIT"

class Server(object):
  def __init__(self, port1, port2):
    self.s = []
    self.c = []
    self.a = []
    for i in [0,1]:
      self.s.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
      self.s[i].bind(('', port1 if i == 0 else port2))
      self.s[i].listen(0)
      # We accept them in order, shouldn't be like that
      client, address = self.s[i].accept()
      self.c.append(client)
      self.a.append(address)

  def close(self):
    self.s[0].close()
    self.s[1].close()

  def launch(self):
    thread.start_new_thread(self.listen, (0,))
    self.listen(1)

  def listen(self, i):
    while 1:
      data = self.c[i].recv(1024)
      if data:
        if data.rstrip() == MSG_EXIT:
          self.close()
          return
        else:
          self.c[(i+1)%2].send(data)

p = int(sys.argv[1])
server = Server(p, p+1)
server.launch()


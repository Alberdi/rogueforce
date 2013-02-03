Rogue Force
===========
Rogue Force is a reimagining of the Sega Saturn *Dragon Force* game set in space featuring roguelike graphics. The game is still in very early development with the focus put on the one on one battles, with a very crude version of the overworld view and other details for now. Not even the name is final.

What does it look like?
-----------------------
If the term *roguelike* didn't click in you, here is some hardcore action featuring a wizard minion attacking a mighty general:

    G...(...w

To be honest, that is more concept art than anything. Here is a real screenshot, if you prefer:

![Rogue Force](http://i.imgur.com/E9kDO.png)

How's the gameplay?
-------------------------
Currently? A bit clumsy. All the input is given through the keyboard, with the mouse position being used for some skills. The graphical interface doesn't help new players that much at the moment, so the best way to know what is what is by trial and error.

Does it feature network play?
-----------------------------
Yeah, you can play against your friends. You only need to run your own copy of the server included and connect to it following some obscure and poorly documented protocol. It'll run flawlessly! (At least if the both of you have good PCs that are really near to the server.) Even then, the hardest part, by far, is finding someone to play against.

How can I run it?
-----------------
You'll need to download all the files in this repository and add the required library files to the root folder from the [libtcod webpage](http://doryen.eptalys.net/libtcod/download/), version 1.5.1. For Linux systems this is simply the `libtcod.so` file.

After that, run `scenario.py` from the command line for the full experience or `battle.py` for a quick fight. The only one that supports network play at the moment is `battle.py`, you can try it with:

    python battle.py [0|1] {address port}

The first argument is the side on which you are playing (0 is left). The game features a dumb AI that does nothing, so you can try the game against it; just leave empty the last pair of parameters. If you want to play a networked game someone has to run the server included, `server.py`, as follows:

    python server.py port

It will launch a TCP server based on sockets on the port included and the next one (port+1). Then each player needs to connect to it in the proper order, first the one going in the port specified and then the other one. Here is an example of the workflow to play a single game of 60 seconds.

    marce:~$ python server.py 8888
    marce:~$ python battle.py 8888
     sito:~$ python battle.py 8889

To customize your experience, such as choosing different generals for each side, you'll to edit the last lines of `battle.py`; and remember to do it on both sides of the network if you want to play the same game. Maybe it's a bit cumbersome, but the `scenario.py` will support network soon.

Rogue Force will have ready to play packages for each major system in the future, but they're not provided yet.

Can I help?
-----------
Probably. I'll appreciate most kinds of help, from code to game ideas for new generals or gameplay. If you want to get involved somehow, write to Marcelino Alberdi (marcelino.alberdi@gmail.com) explaining what would you like to do.

License?
--------
Coming soon.

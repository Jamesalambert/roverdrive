This is a fork of Tolgaatam's ColabTurtle.

The goal is to run this code locally rather than on Google Colab. I've made a lot of changes, principally:

1) The turtle is now animated
2) Background images can be set
3) The turtle can be given a label via t.robot_name = 

Installation
============

Open a new jupyter notebook and add a symlink to Turtle.py in the same folder as the notebook '.ipynb' file




Typical usage (This will probably change)
=============

import Turtle as t

t.loadMissions()
t.missions.start_mission(1)

t.robot_name = "Curiosity"

for i in range(4):
    t.forward(100)
    t.right(90)
    
t.go()








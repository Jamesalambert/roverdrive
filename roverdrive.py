from IPython.display import display, HTML 
import time
import math
import random
import csv

#Modified by James Lambert June 2019
# handy packaging howto
#       https://packaging.python.org/tutorials/packaging-projects/
# if installing from pip then use
# from roverdrive import roverdrive as r


# Created at: 23rd October 2018
#         by: Tolga Atam

# Module for drawing classic Turtle figures on Google Colab notebooks.
# It uses html capabilites of IPython library to draw svg shapes inline.
# Looks of the figures are inspired from Blockly Games / Turtle (blockly-games.appspot.com/turtle)

DEFAULT_WINDOW_SIZE = (800, 500)
DEFAULT_SPEED = 7
DEFAULT_TURTLE_VISIBILITY = True
DEFAULT_PEN_COLOR = 'yellow'
DEFAULT_TURTLE_DEGREE = 270
DEFAULT_BACKGROUND_COLOR = 'black'
DEFAULT_IS_PEN_DOWN = True
DEFAULT_PEN_WIDTH = 5
DEFAULT_ROBOT_NAME = ""
SPEED_TO_SEC_MAP = {1: 1.5, 2: 0.9, 3: 0.7, 4: 0.5, 5: 0.3, 6: 0.18, 7: 0.12, 8: 0.06, 9: 0.04, 10: 0.02}
VALID_COLORS = ('white', 'yellow', 'orange', 'red', 'green', 'blue', 'purple', 'grey', 'black')
MISSION_FOLDER = "roverdrive/backgrounds/training/"

DEFAULT_SVG_ANIMATION_STRING = """
<animateMotion  xlink:href="#turtle" 
                dur="{duration}" 
                begin="0s" 
                rotate="auto" 
                fill="freeze"> 
    <mpath          xlink:href="#route" />
</animateMotion>

<animate    xlink:href="#route" 
            attributeName="stroke-dashoffset" 
            begin="0s" 
            to="0" 
            dur="{duration}" 
            fill="freeze"/>
"""
#fill can be freeze or remove

#the regular solid colour background template
SVG_TEMPLATE = """
      <svg width="{window_width}" height="{window_height}" viewBox="0 0 800 500" style="">
        <rect width="100%" height="100%" fill="{background_color}"/>
        {lines}
        {turtle}
        {animation}
      </svg>
    """

#The Template used if a background image is set
SVG_BG_TEMPLATE_old = """
<svg width="{window_width}" height="{window_height}" viewBox="0 0 800 500">
    <defs>
        <pattern    id="background" 
                    patternUnits="userSpaceOnUse" 
                    width="100%" 
                    height="100%">
                    
            <image      href="{filename}" 
                        x="0" 
                        y="0" 
                        width="100%" 
                        height="100%" />
        </pattern>
    </defs>
    <rect   width="100%" 
            height="100%" 
            fill="url(#background)"/>
    {lines}
    {turtle}
    {animation}
</svg>
"""

SVG_BG_TEMPLATE = """
<svg width="{window_width}" height="{window_height}" viewBox="0 0 800 500">
    <image      href="{filename}" 
                x="0" 
                y="0" 
                width="100%" 
                height="100%" />
    {lines}
    {turtle}
    {animation}
</svg>
"""




#Drawn pointing to the right
TURTLE_SVG_TEMPLATE = """
<g id="turtle" visibility={visibility}>
    <circle stroke="{turtle_color}" 
            stroke-width="3" 
            fill="transparent" 
            r="12" 
            cx="0" 
            cy="0"/>
    <polygon    points="19,0 16,3 16,-3" 
                fill="{turtle_color}"
                stroke="{turtle_color}"
                stroke-width="2"/>
    <text   x="0" 
            y="-22" 
            fill={turtle_color}>
            {label}
    </text>
</g>
"""



# helper function that maps [1,10] speed values to ms delays
def _speedToSec(speed):
    return SPEED_TO_SEC_MAP[speed]


is_turtle_visible = DEFAULT_TURTLE_VISIBILITY
pen_color = DEFAULT_PEN_COLOR
window_size = DEFAULT_WINDOW_SIZE
turtle_pos = (DEFAULT_WINDOW_SIZE[0] // 2, DEFAULT_WINDOW_SIZE[1] // 2)
turtle_degree = DEFAULT_TURTLE_DEGREE
turtle_travel = 0
background_color = DEFAULT_BACKGROUND_COLOR
is_pen_down = DEFAULT_IS_PEN_DOWN
pen_width = DEFAULT_PEN_WIDTH
drawing_window = None
missions = None
speed = DEFAULT_SPEED
robot_name = DEFAULT_ROBOT_NAME

# construct the display for turtle
def initializeTurtle(initial_speed=DEFAULT_SPEED, initial_window_size=DEFAULT_WINDOW_SIZE):
    global window_size
    global drawing_window
    global is_turtle_visible
    global pen_color
    global background_color
    global is_pen_down
    global svg_animation_string
    global svg_path
    global pen_width
    global missions
    global turtle_travel
    global speed
    global robot_name

    if initial_speed not in range(1, 11):
        raise ValueError('initial_speed should be an integer in interval [1,10]')
    if not (isinstance(initial_window_size, tuple) and len(initial_window_size) == 2 and isinstance(
            initial_window_size[0], int) and isinstance(initial_window_size[1], int)):
        raise ValueError('window_size should be a tuple of 2 integers')

    window_size = initial_window_size

    is_pen_down = DEFAULT_IS_PEN_DOWN
    is_turtle_visible = DEFAULT_TURTLE_VISIBILITY
    pen_color = DEFAULT_PEN_COLOR
    turtle_travel = 0
    speed = DEFAULT_SPEED
    robot_name = DEFAULT_ROBOT_NAME
    background_color = DEFAULT_BACKGROUND_COLOR
        
    #Creatw the start of a new svg path with 'move to x,y' M x,y command.
    svg_path = "M {x0},{y0} ".format(   x0 = missions.start_position()[0], 
                                        y0 = missions.start_position()[1])
    
    #ugly fix! The forward command ensures the turtle is always pointing in the new direction of travel.
    forward(1)
    turtle_travel -= 1
    
    svg_animation_string = DEFAULT_SVG_ANIMATION_STRING
    pen_width = DEFAULT_PEN_WIDTH

    drawing_window = display(HTML(_genereateSvgDrawing()), display_id=True)
    #go()
    

def go():
    _updateDrawing()

# helper function for generating svg string of the turtle

def _generate_svg_animation_string():
    
    #determine the duration of the animation
    pixels_per_second = 40 * speed
    
    if speed == 0:
        t = 4
    elif (turtle_travel / pixels_per_second) > 120:
        t = 120
    else:
        t = turtle_travel / pixels_per_second
    
    #print(speed,t)
    return svg_animation_string.format(duration = "{:.2f}s".format(t))

def _generateTurtleSvgDrawing():
    if is_turtle_visible:
        vis = '"visible"'
    else:
        vis = '"hidden"'

    out = TURTLE_SVG_TEMPLATE.format(   turtle_color    =pen_color, 
                                        turtle_x        =turtle_pos[0], 
                                        turtle_y        =turtle_pos[1],
                                        visibility      =vis, 
                                        degrees         =missions.start_degree, 
                                        label           =robot_name)
    
    #print(out)
    
    return out

def _generate_svg_path_string():
        
    p = "d = '" + svg_path + "'"
    
    path_string = """<path  id="route" 
                            stroke='{pen_color}' 
                            stroke-width='{pen_width}' 
                            stroke-dasharray='{length}' 
                            stroke-dashoffset='{length}' 
                            stroke-linecap='round' 
                            fill='transparent' {path} />""".format( pen_color=pen_color, 
                                                                    pen_width=pen_width, 
                                                                    length=turtle_travel, 
                                                                    path=p)

    return path_string

# helper function for generating the whole svg string
def _genereateSvgDrawing():
        
    name = missions.bg_file()
   
    if(name is None):
        out = SVG_TEMPLATE.format(      window_width    =window_size[0], 
                                        window_height   =window_size[1],
                                        background_color=background_color, 
                                        lines           =_generate_svg_path_string(),
                                        turtle          =_generateTurtleSvgDrawing(), 
                                        animation       =_generate_svg_animation_string())
    else:
        out = SVG_BG_TEMPLATE.format(   window_width    =window_size[0], 
                                        window_height   =window_size[1],
                                        filename        =name, 
                                        lines           =_generate_svg_path_string(),
                                        turtle          =_generateTurtleSvgDrawing(), 
                                        animation       =_generate_svg_animation_string())    
    #print(out)                       
    return out


# helper functions for updating the screen using the latest positions/angles/lines etc.
def _updateDrawing():
    if drawing_window == None:
        raise AttributeError("Display has not been initialized yet. Call initializeTurtle() before using.")
    #time.sleep(2)
    #print("update",drawing_window)
    drawing_window.update(HTML(_genereateSvgDrawing()))

#imagine the robot reports what it's found at its current position. [0] makes sure it returns a string not a 1 element list.
def sample():
    return random.choices(["water","dust","ice"],[0.1,0.7,0.2])[0]

# helper function for managing any kind of move to a given 'new_pos' and draw lines if pen is down
def _moveToNewPosition(new_pos):
    global turtle_pos
    global svg_path
    
    svg_path += "L {x2:.2f},{y2:.2f} ".format(  x2 = new_pos[0], 
                                                y2 = new_pos[1])
        
    turtle_pos = new_pos
    #_updateDrawing()



# makes the turtle move forward by 'units' units
def forward(units):
    global turtle_travel
    
    if not isinstance(units, int):
        raise ValueError('units should be an integer')

    alpha = math.radians(turtle_degree)
    ending_point = (turtle_pos[0] + units * math.cos(alpha), turtle_pos[1] + units * math.sin(alpha))

    turtle_travel += abs(units)

    _moveToNewPosition(ending_point)


# makes the turtle move backward by 'units' units
def backward(units):
    if not isinstance(units, int):
        raise ValueError('units should be an integer')
    forward(-1 * units)


# makes the turtle move right by 'degrees' degrees (NOT radians)
def right(degrees):
    global turtle_degree

    if not (isinstance(degrees, int) or isinstance(degrees, float)):
        raise ValueError('degrees should be a number')

    turtle_degree = (turtle_degree + degrees) % 360
    
    forward(1)                          #an ugly fix to make sure the turtle animates to the correct angle at the end of a line!
    
    #_updatedrawing()


# makes the turtle move right by 'degrees' degrees (NOT radians)
def left(degrees):
    if not (isinstance(degrees, int) or isinstance(degrees, float)):
        raise ValueError('degrees should be a number')
    right(-1 * degrees)

# This is currently unused and broken!
# raises the pen such that following turtle moves will not cause any drawings
def _penup():
    global is_pen_down

    is_pen_down = False
    # TODO: decide if we should put the timout after lifting the pen
    # _updateDrawing()


# lowers the pen such that following turtle moves will now cause drawings
def _pendown():
    global is_pen_down

    is_pen_down = True
    # TODO: decide if we should put the timout after releasing the pen
    # _updateDrawing()

def get_degree():
    return "rover is at {:.2f} degrees.".format((turtle_degree - 270.0) % 360.0)

def get_travel():
    return turtle_travel

def set_name(s=""):
    global robot_name
    
    if len(str(s)) > 15:
        raise ValueError('The name should be 15 characters or fewer')
    
    robot_name = s
    

# update the speed of the moves, [1,10]
def set_speed(s):

    global speed
    if s not in range(0, 11):
        raise ValueError('speed should be an integer in the interval [0,10]')
     
    speed = s
    # TODO: decide if we should put the timout after changing the speed
    # _updateDrawing()


# move the turtle to a designated 'x' x-coordinate, y-coordinate stays the same
def setx(x):
    if not isinstance(x, int):
        raise ValueError('new x position should be an integer')
    if not x >= 0:
        raise ValueError('new x position should be nonnegative')
    _moveToNewPosition((x, turtle_pos[1]))


# move the turtle to a designated 'y' y-coordinate, x-coordinate stays the same
def sety(y):
    if not isinstance(y, int):
        raise ValueError('new y position should be an integer')
    if not y >= 0:
        raise ValueError('new y position should be nonnegative')
    _moveToNewPosition((turtle_pos[0], y))


# move the turtle to a designated 'x'-'y' coordinate
def goto(x, y):
    if not isinstance(x, int):
        raise ValueError('new x position should be an integer')
    if not x >= 0:
        raise ValueError('new x position should be nonnegative')
    if not isinstance(y, int):
        raise ValueError('new y position should be an integer')
    if not y >= 0:
        raise ValueError('new y position should be nonnegative')
    _moveToNewPosition((x, y))


# switch turtle visibility to ON
def showturtle():
    global is_turtle_visible

    is_turtle_visible = True
    _updateDrawing()


# switch turtle visibility to ON
def hideturtle():
    global is_turtle_visible

    is_turtle_visible = False
    _updateDrawing()


# change the background color of the drawing area; valid colors are defined at VALID_COLORS
def bgcolor(color):
    global background_color

    if not color in VALID_COLORS:
        raise ValueError('color value should be one of the following: ' + str(VALID_COLORS))
    background_color = color
    _updateDrawing()


# change the color of the pen; valid colors are defined at VALID_COLORS
def color(color):
    global pen_color

    if not color in VALID_COLORS:
        raise ValueError('color value should be one of the following: ' + str(VALID_COLORS))
    pen_color = color
    _updateDrawing()


# change the width of the lines drawn by the turtle, in pixels
def width(width):
    global pen_width

    if not isinstance(width, int):
        raise ValueError('new width position should be an integer')
    if not width > 0:
        raise ValueError('new width position should be positive')

    pen_width = width
    # TODO: decide if we should put the timout after changing the speed
    # _updateDrawing()
    

def loadMissions(folder = MISSION_FOLDER):
    global missions

    try:
        path = folder + "missions.tsv"
    
        inFile = open(path,'r')

        data = csv.reader(inFile, delimiter='\t')

        start_pos = {int(row[0]): (int(row[1]),int(row[2]),int(row[3])) for row in data}
        
        inFile.close()
   
    except FileNotFoundError:
        start_pos = {}
        print("Couldn't find missions file.")
    finally:
        #create Mission object to store mission data and build bg file names.
        missions = Missions(folder, start_pos)
    

#class to hold all the mission data
class Missions(object):
    
    def __init__(self, folder = MISSION_FOLDER, data = {}):
        self.folder = folder
        self.start_pos = {k : (v[0],v[1]) for k,v in data.items()}
        self.start_deg = {k : v[2] for k,v in data.items()}
        self.current_mission = 0
    
    def start(self,n=0):
        
        global turtle_pos
        global turtle_degree
        
        if n not in self.start_pos.keys(): 
            self.current_mission = 0
        else:
            self.current_mission = n
        
        #Move the turtle to the starting position        
        turtle_pos = self.start_position()
        turtle_degree = self.start_degree()
        
        #set up all other default values
        initializeTurtle()
        
    
    def bg_file(self):
        if self.current_mission not in self.start_pos.keys(): 
            return None
        else:
            out = self.folder + "{:0>3}.jpeg".format(self.current_mission)
            return out
    
    def start_position(self):
        if self.current_mission not in self.start_pos.keys(): 
            return (DEFAULT_WINDOW_SIZE[0] // 2, DEFAULT_WINDOW_SIZE[1] // 2)
        else:
            return self.start_pos[self.current_mission]
        
    def start_degree(self):
        if self.current_mission not in self.start_pos.keys(): 
            return 270
        else:
            return self.start_deg[self.current_mission]

        
        

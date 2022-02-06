import pygame

##Setup Initial Pygame Window##
#The number of pixels horizontally in the game window, helps define the size of the tile
SCREEN_WIDTH = 1000
#The number of pixels vertically in the game window
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tentacave')

##Config file storing numerous variables shared across multiple files

##Define game variables##

FPS = 60 #Frames per second the game runs at

#Setup game timer and time related variables
global clock #a global clock varable
clock = pygame.time.Clock() 

global num_ticks #global number of ticks that have transpired since last update
num_ticks = 0

SCROLL_THRESH = 200 #Threshold of pixels from the right or left of the screen before scrolling begins
ROWS = 16 #How many rows of tiles vertically. Also defines how the size of the tiles altogether
COLS = 150 #Max number of collumns in a level
TILE_TYPES = 21 #How many different types of tiles are utilized within the game
ACCELERATION = 2 #A numerical value that defines how fast the player character accelerates. Recommended value < 5

#The amount of water resistance against the players movements. Higher values increases the deacceleration of
#the player when no movement key is held in the direction of movement.
WATRES = 0.5
tile_size = SCREEN_HEIGHT//ROWS #The size of each individual tile on the screen.
max_velocity = 15 #The max speed the player character is able to achieve before speed is limited

#The game_state, current possible values include:
# 3: the intial starting state, initializes game at the start menu
# 2:  the game state signifying the completion of a level
# 0:  the game state when the game is running. Loads world and allows player movement
# -1: indicates the player is dead and triggers game over screen
# Game state 1 is currently reserves for a pause menu, not currently implemented
game_state = 3

global screen_scroll# Initializes the initial screen scroll at 0. Value corresponds to number of pixels to scroll to the right
screen_scroll = 0   # or left during runtime

global bg_scroll    # Functions much the same as screen scroll however is the value tracked for the background to create
bg_scroll = 0       #an interesting visual effect
playerspawn = [500, 500] #A list correspond to the x and y coordinates of the player on initial spawn

#The value corresponding to the initial level to spawn on, increments as levels are cleared, begins at 1
level = 1
numlevels = 2 #The total number of levels available to play
#3 levels are currently technically available but the third level is for testing only

vec = pygame.math.Vector2 #Setsup a vector variable to track non planar movement


import pygame
from config import TILE_TYPES


#loads all tile images and append the images to a parsable list.
#Mostly for use in level editor, though somewhat utilized
#for basic tiles in game
tile_img_list = []
for x in range(TILE_TYPES):
    img =pygame.image.load(f'img/tiles/{x}.png')
    tile_img_list.append(img)

#Load and scale images pertaining to the background
farbg_img = pygame.image.load('img/Background/far.png')
farbg_img = pygame.transform.scale(farbg_img, (1067, 800))
closebg_img = pygame.image.load('img/Background/foregound-merged.png')
closebg_img = pygame.transform.scale(closebg_img, (2133, 800))
midbg_img = pygame.image.load('img/Background/sand.png')
midbg_img = pygame.transform.scale(midbg_img, (1067, 800))

#Load and scale images related to the menus
restart_img = pygame.image.load('img/buttons/restart.png') 
restart_img =pygame.transform.scale(restart_img, (146, 60))
play_img = pygame.image.load('img/buttons/play.png')
play_img =pygame.transform.scale(play_img, (146, 60))
exit_img = pygame.image.load('img/buttons/exit.png')
exit_img =pygame.transform.scale(exit_img, (146, 60))
start_img = pygame.image.load('img/Splash_Text/start.png')
start_img = pygame.transform.scale(start_img, (600, 108))
complete_img = pygame.image.load('img/Splash_Text/complete.png')
complete_img = pygame.transform.scale(complete_img, (750, 108))
final_img = pygame.image.load('img/Splash_Text/finished.png')
final_img = pygame.transform.scale(final_img, (750, 108))

##Load images related to the player##
#and append to a list for use animating later
idle_player_images = [] #ImageSet used for player in the menu
moving_player_images = [] #ImageSet used for in game player
dead_player_images = [] #ImageSet used for dead player
for num in range(1, 11):
    img = pygame.image.load(f'img/Octo_Sprites/U ({num}).png')
    img = pygame.transform.scale(img, (66,58))
    moving_player_images.append(img)
    img = pygame.image.load(f'img/Octo_Sprites/Dead ({num}).png')
    img = pygame.transform.scale(img, (66,58))
    dead_player_images.append(img)
    img = pygame.image.load(f'img/Octo_Sprites/Idle{num}.png')
    idle_player_images.append(img)

##Load Images related to Enemies##
#Urchin
urchin_image = pygame.image.load('img/tiles/Enemies/urchin.png')
urchin_image = pygame.transform.scale(urchin_image, (50, 50))

#Mines
mine_image = pygame.image.load('img/tiles/Enemies/mine.png')

#Feesh
feesh_images = []
for num in range(1, 5):
    img = pygame.image.load(f'img/tiles/Enemies/Feesh/{num}.png')
    img = pygame.transform.scale(img, (78, 60))
    feesh_images.append(img)

#Beeg_Feesh
beeg_feesh_images = []
for num in range(1, 5):
    img = pygame.image.load(f'img/tiles/Enemies/Beeg_Feesh/{num}.png')
    img = pygame.transform.scale(img, (160, 150))
    beeg_feesh_images.append(img)

##Collectible Images##
#Chest
chest_img = tile_img_list[19]
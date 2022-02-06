##Ocotcave##
#This is the main file for the Octocave game and contains the majority of the game logic.
#This project depends on pygame, which comes preinstalled with recent versions of python.
#This project was mostly developed in order to better understand the caoabilities of the 
#pygame module and is by no means a AAA game. Many further optimizations may be implemented down
#the line and all game content is subject to change.
#This project is brought to you by Ryan Thomsen
import pygame
from pygame.sprite import Sprite
from spritesheet import SpriteSheet
import csv
import button
import enemies
import world
from collectibles import Chest
from image_loader import *
import config
from config import screen, game_state, ROWS, COLS

#Initialize imported pygame modules
pygame.init()

#Initialize music modules
pygame.mixer.init()

#Load Background Music
pygame.mixer.music.load('img/Sounds/watery_cave.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play()

#Class defining the player object
class Player():
    def __init__(self, x, y):
        #Calls the reset class upon initialization of the player character
        self.reset(x, y)

    #A class controlling the player movement that operates using booleans 
    #to determine the players direction. Operates on acceleration rather than
    #a flat speed to simulate building momentum under water
    #Also includes a constant deceleration supposed to simulate water resistance
    def move(self, moving_left, moving_right, moving_up, moving_down):
        #reset movement variables
        self.acc =config.vec(0,0)
        #assign movement variables depending on direction moving
        #calculates velocity in x and y directions
        #also calculates rotational information for player sprites
        if moving_left:
            self.rotate = 90
            self.flip_x = True
            self.acc.x = -config.ACCELERATION #neg accelerations in x direction moves player left
        if moving_right:
            self.rotate = 90
            self.flip_x = False
            self.acc.x = config.ACCELERATION #pos accelerations in x direction moves player right
        if moving_up:
            self.rotate = 0
            self.flip_x = False
            self.acc.y = -config.ACCELERATION #neg accelerations in x direction moves player up
        if moving_down:
            self.rotate = 0
            self.flip_x = True
            self.acc.y = config.ACCELERATION #pos accelerations in y direction moves player up
        #factors in water resistance
        #gradually slows down player in all directions
        if self.vel.x >0:
            self.vel.x -= config.WATRES
        if self.vel.x <0:
            self.vel.x += config.WATRES
        if self.vel.y <0:
            self.vel.y += config.WATRES
        if self.vel.y >0:
            self.vel.y -= config.WATRES

        #Adjust player velocity according to acceleration 
        #player velocity is computed as a vector
        self.vel+=self.acc

        #checks to make sure max velocity is not exceeded
        if (self.vel.y > config.max_velocity):
            self.vel.y = config.max_velocity
        if (self.vel.y < -config.max_velocity):
            self.vel.y = -config.max_velocity
        if (self.vel.x > config.max_velocity):
            self.vel.x = config.max_velocity
        if (self.vel.x < -config.max_velocity):
            self.vel.x = -config.max_velocity

        #Adjusts position based on velocity
        self.pos+=self.vel+(self.acc)/2
        #Converts positions to integers as pygame rectangles cannot handle floats
        self.pos.x = round(self.pos.x)
        self.pos.y = round(self.pos.y)

        #create projected rectangle at new coordinates
        temp_rect = pygame.Rect(0, 0, self.width, self.height)
        temp_rect.center = self.pos
        #check for collisions against projected rectangle
        #checks for collisions against tiles, enemies, and collectibles
        #and updates game state accordingly
        game_state = self.collide(temp_rect)

        #check for and computes necesarry screen scroll
        self.scroll(temp_rect)

        #Once all checks and adjustments have occured oficially updates
        #player position
        self.rect.center=self.pos
        self.hitbox.center=self.pos
        #Returns updated game state after player movement
        return game_state

    #Player method to compute both if scrolling needs to occur and how far
    def scroll(self,temp_rect):
        #reset scroll from previous calls
        config.screen_scroll = 0
        #Check to see if current position is off screen and resets if has occured
        if temp_rect.left < 0:
            temp_rect.left=0
            self.pos.x = temp_rect.centerx
        elif temp_rect.right > config.SCREEN_WIDTH:
            temp_rect.right = config.SCREEN_WIDTH
            self.pos.x = temp_rect.centerx
        if temp_rect.top < 0:
            temp_rect.top=0
            self.pos.y = temp_rect.centery
        elif temp_rect.bottom > config.SCREEN_HEIGHT:
            temp_rect.bottom = config.SCREEN_HEIGHT
            self.pos.y = temp_rect.centery
        #check for if scroll threshold has been crossed and computes screen scroll distance
        #according to current player velocity
        if temp_rect.left < config.SCROLL_THRESH and config.bg_scroll > config.tile_size:
            config.screen_scroll = -self.vel.x
            temp_rect.left=config.SCROLL_THRESH
            self.pos.x = temp_rect.centerx
        elif temp_rect.right > config.SCREEN_WIDTH - config.SCROLL_THRESH and config.bg_scroll < (world1.level_length * config.tile_size) - config.SCREEN_WIDTH - config.tile_size:
            config.screen_scroll = -self.vel.x
            temp_rect.right=config.SCREEN_WIDTH - config.SCROLL_THRESH
            self.pos.x = temp_rect.centerx
    #Method providing collision detection for the player
    def collide(self, temp_rect):
        game_state = 0
        for tile in world1.obstacle_list:
            #checks for collision in the x direction
            if tile[2].colliderect(temp_rect.x, self.hitbox.y, self.width, self.height):
                #check if on right side of block by checking current velocity direction
                #sets position to be just left of the right side of colliding tile
                if self.vel.x < 0:
                    temp_rect.left = tile[2].right + 1
                    self.pos.x = temp_rect.centerx
                    self.vel.x = 0
                #check if on left side of block by checking current velocity direction
                #sets position to be just right of the left side of colliding tile
                elif self.vel.x > 0:
                    temp_rect.right = tile[2].left - 1
                    self.pos.x = temp_rect.centerx
                    self.vel.x = 0
            #checks for collision in y direction\
            if tile[2].colliderect(self.hitbox.x, temp_rect.y, self.width, self.height):
                #check if below the block by checking current velocity direction
                #sets position to be just below the bottom of colliding tile
                if self.vel.y < 0:
                    temp_rect.top = tile[2].bottom + 1
                    self.pos.y = temp_rect.centery
                    self.vel.y = 0
                #check if above the block by checking current velocity direction
                #sets position to be just above the top of colliding tile
                if self.vel.y > 0:
                    temp_rect.bottom = tile[2].top -1
                    self.pos.y = temp_rect.centery
                    self.vel.y = 0
            #check for enemy collision
            #and sets game state to the death state if collision occurs
            for mine in world1.mine_group:
                if mine.hitbox.colliderect(temp_rect):
                    game_state = -1
            for feesh in world1.feesh_group:
                if feesh.hitbox.colliderect(temp_rect):
                    game_state = -1
            for urchin in world1.urchin_group:
                if urchin.hitbox.colliderect(temp_rect):
                    game_state = -1   
            for beegfeesh in world1.beegfeesh_group:
                if beegfeesh.hitbox.colliderect(temp_rect):
                    game_state = -1
                #Check for crossing line of sight of a beeg feesh and if
                #los is crossed triggers beeg feesh
                elif beegfeesh.triggerbox.colliderect(temp_rect):
                    beegfeesh.trigger()
            #Check for collision with chest and sets game state
            #to level complete if collision occurs
            if pygame.sprite.spritecollide(self, world1.chest_group, False):
                    game_state = 2
        return game_state
    #Draw method for the player class
    def draw(self):
        #draws the correct facing spriteaccording to prior determined values
        screen.blit(pygame.transform.rotate(pygame.transform.flip(moving_player_images[self.index], self.flip_y, self.flip_x), -self.rotate),self.rect)
    #Update method for the player that animates sprite and changes sprite according to game state
    def update(self, game_state):
        global dt
        #checks game_state to make sure player is alive
        if game_state==0:
            self.draw()
        #sets playersprite to dead sprite if game state is -1
        elif game_state == -1:
            screen.blit(dead_player_images[self.index], self.rect)
            if (self.rect.y > 50):
                self.rect.y-=5

        #option to draw hitbox
        #pygame.draw.rect(screen, (255,255,255), self.hitbox, 2)

        #add number of ticks transpired
        self.elapsed += config.num_ticks
        #Limits update frequency
        if self.elapsed >= 100:
            self.index+=1
            if self.index == 10:
                self.index = 0
            self.elapsed = 0
    #Reset method for the player character for when level is reset
    #resets all player variables and its location
    def reset(self,x,y):
        self.index = 0
        self.elapsed = 0
        self.flip_x = False
        self.flip_y = False
        self.rotate = 0
        self.pos = config.vec(x,y)
        self.vel = config.vec(0,0)
        self.acc =config.vec(0,0)
        #player sprite loading
        self.image = moving_player_images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = 45
        self.height = 45
        self.hitbox = pygame.Rect(x+11, y+5, self.width, self.height)


#variables pertaining to main game loop
run= True
frames = 0 #index helping track number of ticks
ani_index = 0 #index for animating menu

#variables relating to player movement initialization
moving_left = False
moving_right = False
moving_up = False
moving_down = False

#creaty empy tile list
world_data = []
config.level -= 1 #Decrement config.level so that it begins at 0 for pythons readability rather than 1 as humans use
for row in range(config.ROWS):
        r = [-1]*config.COLS
        world_data.append(r)
#load in level data from csv files and create world
with open(f'level{config.level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile,delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world1 = world.World(world_data) #creates world list according to level data
playerspawn = world1.process_data(world_data) #set player spawn from world data
player = Player(playerspawn[0], playerspawn[1]) #spawns an instance of the player
#create buttons
restart_button = button.Button(config.SCREEN_WIDTH//2 - 246, config.SCREEN_HEIGHT//2+100, restart_img, 1)
play_button = button.Button(config.SCREEN_WIDTH//2 - 246, config.SCREEN_HEIGHT//2+100, play_img, 1)
exit_button = button.Button(config.SCREEN_WIDTH//2 + 100, config.SCREEN_HEIGHT//2+100, exit_img, 1)

#beginning of main game loop
while run:
    #Update the number of ticks that have transpired
    config.num_ticks = config.clock.tick(config.FPS)
    #draws the background
    world.World.draw_bg()
    #Draws world if in the play game state
    #Needs to be called before player update function
    #else draws world over player
    if game_state ==0:
        #draw world
        world1.draw()
    #draws and updates player sprite according to game state
    player.update(game_state)
    #checks for closing the game and keypresses
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if game_state == 0:
            #get keypresses, set movement bools accordingly
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a):
                    moving_left = True
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d):
                    moving_right = True
                if (event.key == pygame.K_UP or event.key == pygame.K_w):
                    moving_up = True
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s):
                    moving_down = True
        #captures when keys are released
            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a):
                    moving_left = False
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_d):
                    moving_right = False
                if (event.key == pygame.K_UP or event.key == pygame.K_w):
                    moving_up = False
                if (event.key == pygame.K_DOWN or event.key == pygame.K_s):
                    moving_down = False
    #Game State 0 is when the player is alive and no menus are active
    if(game_state==0):
        #moves player, record game state, and screen_scroll
        game_state = player.move(moving_left, moving_right, moving_up, moving_down)
        #Sets bg scroll according to screen scroll
        config.bg_scroll -= config.screen_scroll
        #Load world for enemies
        enemies.Enemy.load_world(world1)
        #update sprite groups
        world1.mine_group.update()
        world1.feesh_group.update()
        world1.urchin_group.update()
        world1.chest_group.update()
        world1.beegfeesh_group.update()
        #draw sprite groups
        world1.mine_group.draw(screen)
        world1.feesh_group.draw(screen)
        world1.urchin_group.draw(screen)
        world1.beegfeesh_group.draw(screen)
        world1.chest_group.draw(screen)
    #Game State 2 is the completion screen for a level
    elif game_state ==2:
        #checker to see if we have exceeded the total number of created levels
        #If so renders game complete screen
        if config.level >= config.numlevels-1:
            screen.blit(idle_player_images[ani_index//2], (config.SCREEN_WIDTH//2-175,config.SCREEN_HEIGHT//3-150))
            screen.blit(final_img, (config.SCREEN_WIDTH//2-360,config.SCREEN_HEIGHT//3-100))
            ani_index+=1
            if ani_index >=20:
                ani_index = 0
            #Resets world and level to first level if play button is clicked
            if(play_button.draw(screen)):
                config.level = 0
                world_data = world1.reset_level()
                #load in level and create world
                with open(f'level{config.level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile,delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world1 = world.World(world_data)
                playerspawn = world1.process_data(world_data)
                player.reset(playerspawn[0],playerspawn[1])
                game_state = 0
            #quits the game if exit is clicked
            if(exit_button.draw(screen)):
                run=False
         #Check to make sure we are not exceeding the number of created levels
         #Resets worldd, increments level, and renders next level if we have another level to load
        if config.level< config.numlevels-1:
            screen.blit(complete_img, (config.SCREEN_WIDTH//2-375,config.SCREEN_HEIGHT//3-100))
            if(play_button.draw(screen)):
                config.bg_scroll = 0
                config.level+=1
                world_data = world1.reset_level()
                #load in level and create world
                with open(f'level{config.level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile,delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world1 = world.World(world_data)
                playerspawn = world1.process_data(world_data)
                player.reset(playerspawn[0],playerspawn[1])
                game_state = 0
        #Quits if exit button is clicked
        if(exit_button.draw(config.screen)):
            run=False
    #Game State 3 is when the Start Menu is active
    elif game_state ==3:
        screen.blit(idle_player_images[ani_index//2], (config.SCREEN_WIDTH//2-175,config.SCREEN_HEIGHT//3-150))
        screen.blit(start_img, (config.SCREEN_WIDTH//2-300,config.SCREEN_HEIGHT//3-100))
        #add number of ticks transpired
        frames += config.num_ticks
        #Limits update frequency
        if frames >= 100:
            ani_index+=1
            #Resets after all frames are completed
            if ani_index >=20:
                ani_index = 0
                frames = 0
        if(play_button.draw(screen)):
            game_state=0
        if(exit_button.draw(screen)):
            run=False
    #Game State -1 is when the player is dead, the Retry screen.
    #Stops screem scroll in case player dies mid scroll
    elif game_state == -1:
        config.screen_scroll = 0
        #Resets world and game variables when restart button is clocked
        if restart_button.draw(screen):
            config.bg_scroll = 0
            world_data = world1.reset_level()
            #load in level and create world
            with open(f'level{config.level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile,delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)
            world1 = world.World(world_data)
            playerspawn = world1.process_data(world_data)
            player.reset(playerspawn[0],playerspawn[1])
            game_state = 0
        #Quits when exit button is clocked
        if exit_button.draw(screen):
            run = False
    #Updates full display for player viewing
    pygame.display.update()
#Closes initialized pygame modules
pygame.quit()
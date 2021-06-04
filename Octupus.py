from os import urandom
import pygame
import pygame.math
from pygame import draw
from pygame.locals import *
from pygame.sprite import Sprite
from spritesheet import SpriteSheet
import csv
from random import seed
from random import randint

pygame.init()

clock = pygame.time.Clock()
fps = 60 
screen_width = 1000
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Octupus Game')

#define game variables
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_TYPES = 19
ACCELERATION = 2
WATRES = 0.5
tile_size = screen_height//ROWS
max_velocity = 15
dt = 0
game_state = 3
screen_scroll = 0
bg_scroll = 0
playerspawn = [500, 500]
level = 1
numlevels = 2
vec = pygame.math.Vector2
#load tiles
img_list = []
for x in range(TILE_TYPES):
    img =pygame.image.load(f'img/Tile/{x}.png')
    img_list.append(img)


#load images
farbg_img = pygame.image.load('img/Background/far.png')
farbg_img = pygame.transform.scale(farbg_img, (1067, 800))
closebg_img = pygame.image.load('img/Background/foregound-merged.png')
closebg_img = pygame.transform.scale(closebg_img, (2133, 800))
midbg_img = pygame.image.load('img/Background/sand.png')
midbg_img = pygame.transform.scale(midbg_img, (1067, 800))
restart_img = pygame.image.load('img/red/restart.png') 
play_img = pygame.image.load('img/red/play.png')
exit_img = pygame.image.load('img/red/exit.png')
start_img = pygame.image.load('img/start.png')
start_img = pygame.transform.scale(start_img, (600, 108))
complete_img = pygame.image.load('img/complete.png')
complete_img = pygame.transform.scale(complete_img, (750, 108))

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.image =pygame.transform.scale(self.image, (146, 60))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    
    def draw(self):
        action = False
        #get_mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        #draw button
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)


    def move(self, moving_left, moving_right, moving_up, moving_down):
        #reset movement variables
        screen_scroll = 0
        self.acc =vec(0,0)
        #assign movement variables depending on direction moving
        #calculates velocity in x and y directions
        if moving_left:
            self.rotate = 90
            self.flip_x = True
            self.acc.x = -ACCELERATION
        if moving_right:
            self.rotate = 90
            self.flip_x = False
            self.acc.x = ACCELERATION
        if moving_up:
            self.rotate = 0
            self.flip_x = False
            self.acc.y = -ACCELERATION
        if moving_down:
            self.rotate = 0
            self.flip_x = True
            self.acc.y = ACCELERATION
        #factors in water resistance
        if self.vel.x >0:
            self.vel.x -= WATRES
        if self.vel.x <0:
            self.vel.x += WATRES
        if self.vel.y <0:
            self.vel.y += WATRES
        if self.vel.y >0:
            self.vel.y -= WATRES

        self.vel+=self.acc

        if (self.vel.y > max_velocity):
            self.vel.y = max_velocity
        if (self.vel.y < -max_velocity):
            self.vel.y = -max_velocity
        if (self.vel.x > max_velocity):
            self.vel.x = max_velocity
        if (self.vel.x < -max_velocity):
            self.vel.x = -max_velocity

        self.pos+=self.vel+(self.acc)/2
        self.pos.x = round(self.pos.x)
        self.pos.y = round(self.pos.y)

        #create rectangle at position
        temp_rect = pygame.Rect(0, 0, self.width, self.height)
        temp_rect.center = self.pos
        #check for collision
        game_state = self.collide(temp_rect)

        #check for screen scroll
        screen_scroll = self.scroll(temp_rect)

        self.rect.center=self.pos
        self.hitbox.center=self.pos

        #update scroll based on player position

        return game_state, screen_scroll

    def scroll(self,temp_rect):
        #check if going off the edges of the screen
        screen_scroll=0
        if temp_rect.left < 0:
            temp_rect.left=0
            self.pos.x = temp_rect.centerx
        elif temp_rect.right > screen_width:
            temp_rect.right = screen_width
            self.pos.x = temp_rect.centerx
        if temp_rect.top < 0:
            temp_rect.top=0
            self.pos.y = temp_rect.centery
        elif temp_rect.bottom > screen_height:
            temp_rect.bottom = screen_height
            self.pos.y = temp_rect.centery
        #check for if sceen should scroll
        if temp_rect.left < SCROLL_THRESH and bg_scroll > tile_size:
            screen_scroll = -self.vel.x
            temp_rect.left=SCROLL_THRESH
            self.pos.x = temp_rect.centerx
        elif temp_rect.right > screen_width - SCROLL_THRESH and bg_scroll < (world.level_length * tile_size) - screen_width-tile_size:
            screen_scroll = -self.vel.x
            temp_rect.right=screen_width - SCROLL_THRESH
            self.pos.x = temp_rect.centerx
        return screen_scroll

    def collide(self, temp_rect):
        #check for collision
        game_state = 0
        for tile in world.obstacle_list:
            #x direction
            if tile[2].colliderect(temp_rect.x, self.hitbox.y, self.width, self.height):
                #check if on right side of block
                if self.vel.x < 0:
                    temp_rect.left = tile[2].right + 1
                    self.pos.x = temp_rect.centerx
                    self.vel.x = 0
                #check if on left side of block
                elif self.vel.x > 0:
                    temp_rect.right = tile[2].left - 1
                    self.pos.x = temp_rect.centerx
                    self.vel.x = 0
            #y direction
            if tile[2].colliderect(self.hitbox.x, temp_rect.y, self.width, self.height):
                #check if below the block
                if self.vel.y < 0:
                    temp_rect.top = tile[2].bottom + 1
                    self.pos.y = temp_rect.centery
                    self.vel.y = 0
                #check if above the block
                if self.vel.y > 0:
                    temp_rect.bottom = tile[2].top -1
                    self.pos.y = temp_rect.centery
                    self.vel.y = 0
            #check for enemy collision
            for mine in mine_group:
                if mine.hitbox.colliderect(temp_rect):
                    game_state = -1
            for feesh in feesh_group:
                if feesh.hitbox.colliderect(temp_rect):
                    game_state = -1
            for urchin in urchin_group:
                if urchin.hitbox.colliderect(temp_rect):
                    game_state = -1        
            if pygame.sprite.spritecollide(self, chest_group, False):
                    game_state = 4
        return game_state

    def draw(self):
        #draws the correct facing sprite
        screen.blit(pygame.transform.rotate(pygame.transform.flip(self.images_U[self.index], self.flip_y, self.flip_x), -self.rotate),self.rect)

    def update(self, game_state):
        global dt
        #checks game_state
        if game_state==0:
            self.draw()
        #kills player if game state is -1
        elif game_state == -1:
            screen.blit(self.images_Dead[self.index], self.rect)
            if (self.rect.y > 50):
                self.rect.y-=5

        #option to draw hitbox
        #pygame.draw.rect(screen, (255,255,255), self.hitbox, 2)

        #add number of ticks transpired
        self.elapsed += dt
        #Limits update frequency
        if self.elapsed >= 100:
            self.index+=1
            if self.index == 10:
                self.index = 0
            self.elapsed = 0


    def reset(self,x,y):
        self.images_U = []
        self.images_Dead = []
        self.index = 0
        self.elapsed = 0
        self.flip_x = False
        self.flip_y = False
        self.rotate = 0
        self.pos = vec(x,y)
        self.vel = vec(0,0)
        self.acc =vec(0,0)
        #player sprite loading
        for num in range(1, 11):
            self.img = pygame.image.load(f'Assets/Octo_Sprites/U ({num}).png')
            self.img = pygame.transform.scale(self.img, (66,58))
            self.images_U.append(self.img)
            self.img = pygame.image.load(f'Assets/Octo_Sprites/Dead ({num}).png')
            self.img = pygame.transform.scale(self.img, (66,58))
            self.images_Dead.append(self.img)
        
        self.image = self.images_U[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = 45
        self.height = 45
        self.hitbox = pygame.Rect(x+11, y+5, self.width, self.height)


def reset_level():
    mine_group.empty()
    chest_group.empty()
    feesh_group.empty()
    urchin_group.empty()
    data = []
    for row in range(ROWS):
            r = [-1]*COLS
            data.append(r)

    return data

    
class World():
    def __init__(self, data):
        self.obstacle_list = []
        self.decoration_list = []

    def process_data(self, data):
        self.level_length =len(data[0])
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile>=0 and tile <= 12:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size

                    if tile >= 0 and tile<=8:
                        hitbox = pygame.Rect(x*tile_size, y*tile_size, tile_size, tile_size)
                        if tile >=0 and tile <= 4:
                            tile_data = (img, img_rect, hitbox)
                        elif tile>=5 and tile<=6:
                            img_rect.x-= 10
                            tile_data = (img, img_rect, hitbox)
                        elif tile>=7 and tile<=8:
                            img_rect.y-= 10
                            tile_data = (img, img_rect, hitbox)
                    elif(tile >=9 and tile <=12):
                        hitbox = pygame.Rect(x*tile_size, y*tile_size, 32, 32)
                        if tile == 9:
                            img_rect.x+= 1
                            img_rect.y+= 1
                            hitbox.x += 20
                            hitbox.y+= 20
                        if tile == 10:
                            img_rect.x-= 1
                            img_rect.y+= 1
                            hitbox.y+= 20
                        if tile == 11:
                            img_rect.x+= 1
                            img_rect.y-= 1
                            hitbox.x += 20
                        if tile == 12:
                            img_rect.x-= 1
                            img_rect.y-= 1
                        tile_data = (img, img_rect, hitbox)
                    self.obstacle_list.append(tile_data)
                elif tile == 13:
                    #Randomizer for height
                    random_int = randint(-50, 50)
                    mine = Mine(x*tile_size, y*tile_size +random_int, random_int, 100)
                    mine_group.add(mine)
                elif tile == 14:
                    feesh = Feesh(x*tile_size, y*tile_size)
                    feesh_group.add(feesh)
                elif tile == 15:
                    urchin = Urchin(x*tile_size, y*tile_size)
                    urchin_group.add(urchin)
                elif tile == 16:
                    urchin = Urchin(x*tile_size, y*tile_size)
                    urchin_group.add(urchin)       
                elif tile == 17:
                    chest = Chest(x*tile_size, y*tile_size)
                    chest_group.add(chest)
                elif tile == 18:
                    playerspawn = (x*tile_size, y*tile_size)
        return playerspawn
    def draw (self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            tile[2][0] += screen_scroll
            screen.blit(tile[0],tile[1])
            #pygame.draw.rect(screen, (255,0,255), tile[2], 2)
        for tile in self.decoration_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0],tile[1])

class Chest(pygame.sprite.Sprite):
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/tile/chest/chest1.png')
        self.image =pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.touched = False
    def update(self):
        #scroll
        self.rect.x+=screen_scroll
        

class Urchin(pygame.sprite.Sprite):
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        #self.index = 0
        #self.count = 1
        #if (direction == 1 or direction == 2):
        #    for num in range (1, 5):
        #        self.img = pygame.image.load(f'img/tile/Enemies/urchin{num}.png')
        #        self.img = pygame.transform.scale(self.img, (54, 50))
        #        self.hitbox = pygame.Rect(x+2, y+2, 48, 48)
        #        if direction == 2:
        #            self.hitbox.y-=5
        #            self.img = pygame.transform.flip(self.img, True, True)
        #        self.images.append(self.img)
        #self.image = self.images[self.index]
        self.image = pygame.image.load('img/tile/Enemies/urchin.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.hitbox = pygame.Rect(x+10, y+10, 30, 30)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        #self.image = self.images[self.index]
        #if(self.count%10 == 0):
            #dosomething
        #    self.index+=1
        #if(self.count ==30):
        #    self.count = 0
        #    self.index = 0
        #self.count+=1
        #scroll
        self.hitbox.x+=screen_scroll
        self.rect.x+=screen_scroll             

class Mine(pygame.sprite.Sprite):
    def __init__(self,x, y, bob, bob_max):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/tile/Enemies/mine.png')
        self.hitbox = pygame.Rect(x+6, y+8, 30, 30)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.bob_direction = 1
        self.bob_counter = bob
        self.bob_max = bob_max
    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        if self.bob_counter%5:
            self.rect.y += (self.bob_direction)
            self.hitbox.y += (self.bob_direction)
        self.bob_counter += 1
        if abs(self.bob_counter) > self.bob_max:
            self.bob_direction *= -1
            self.bob_counter *=-1
        #scroll
        self.hitbox.x+=screen_scroll
        self.rect.x+=screen_scroll

class Feesh(pygame.sprite.Sprite):
    def __init__(self,x, y):
            pygame.sprite.Sprite.__init__(self)
            feesh = SpriteSheet('img/tile/Enemies/feesh.png')
            self.images = []
            self.index = 0
            self.elapsed = 0
            self.hitbox = pygame.Rect(x+1, y+12, 75, 46)
            margin = 2
            for num in range(1, 5):
                feesh_rect = ((margin*num)+(26*(num-1)), margin, 26, 20)
                self.img = feesh.image_at(feesh_rect, -1)
                self.img = pygame.transform.scale(self.img, (78, 60))
                self.images.append(self.img)
            self.rect = self.img.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_direction = 3
            self.move_counter = 0
    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        self.rect.x += self.move_direction
        self.hitbox.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *=-1
        if self.move_direction > 0:
            self.image = self.images[self.index]
        elif self.move_direction < 0:
            self.image = pygame.transform.flip(self.images[self.index], True, False)
        #add number of ticks transpired
        self.elapsed += dt
        #Limits update frequency
        if self.elapsed >= 100:
            self.index+=1
            if self.index == 4:
                self.index = 0
            self.elapsed = 0
        #scroll
        self.hitbox.x+=screen_scroll
        self.rect.x+=screen_scroll

def draw_bg():
    screen.fill((0,0,255))
    width = farbg_img.get_width()
    for x in range(6):
        screen.blit(farbg_img, ((x*width)-bg_scroll*0.5,0))
        if x%2==0:
            screen.blit(midbg_img, ((x*width*2)-bg_scroll*0.6,0))
        screen.blit(closebg_img, ((x*width)-bg_scroll*0.8,0))

#creaty empy tile list
world_data = []
for row in range(ROWS):
        r = [-1]*COLS
        world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile,delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

mine_group = pygame.sprite.Group()
feesh_group = pygame.sprite.Group()
urchin_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
world = World(world_data)
playerspawn = world.process_data(world_data)
player = Player(playerspawn[0], playerspawn[1])
#create buttons
restart_button = Button(screen_width//2 - 246, screen_height//2+100, restart_img)
play_button = Button(screen_width//2 - 246, screen_height//2+100, play_img)
exit_button = Button(screen_width//2 + 100, screen_height//2+100, exit_img)

#main
run= True
moving_left = False
moving_right = False
moving_up = False
moving_down = False

while run:

    dt = clock.tick(fps)
    #draws the background
    draw_bg()
    if game_state ==0:
        #draw world
        world.draw()
    #draws and updates player according to game state
    player.update(game_state)
    #checks for closing the game and keypresses
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if game_state == 0:
            #get keypresses
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a):
                    moving_left = True
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d):
                    moving_right = True
                if (event.key == pygame.K_UP or event.key == pygame.K_w):
                    moving_up = True
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s):
                    moving_down = True
            
        if event.type == pygame.KEYUP:
            if (event.key == pygame.K_LEFT or event.key == pygame.K_a):
                moving_left = False
            if (event.key == pygame.K_RIGHT or event.key == pygame.K_d):
                moving_right = False
            if (event.key == pygame.K_UP or event.key == pygame.K_w):
                moving_up = False
            if (event.key == pygame.K_DOWN or event.key == pygame.K_s):
                moving_down = False
    if(game_state==0):
        #move player record game state and screen_scroll
        game_state, screen_scroll = player.move(moving_left, moving_right, moving_up, moving_down)
        bg_scroll -= screen_scroll
        #update groups
        mine_group.update()
        feesh_group.update()
        urchin_group.update()
        chest_group.update()
        #draw groups
        mine_group.draw(screen)
        feesh_group.draw(screen)
        urchin_group.draw(screen)
        chest_group.draw(screen)
    elif game_state ==4:
        screen.blit(complete_img, (screen_width//2-375,screen_height//3-100))
        if(play_button.draw()):
            bg_scroll = 0
            if level+1==numlevels:
                game_state = 5
            elif level+1< numlevels:
                level+=1
                world_data = reset_level()
                #load in level and create world
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile,delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World(world_data)
                playerspawn = world.process_data(world_data)
                player.reset(playerspawn[0],playerspawn[1])
                game_state = 0
        if(exit_button.draw()):
            run=False
    elif game_state ==3:
        screen.blit(start_img, (screen_width//2-300,screen_height//3-100))
        if(play_button.draw()):
            game_state=0
        if(exit_button.draw()):
            run=False
    elif game_state == -1:
        screen_scroll = 0
        if restart_button.draw():
            bg_scroll = 0
            world_data = reset_level()
            #load in level and create world
            with open(f'level{level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile,delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)
            world = World(world_data)
            playerspawn = world.process_data(world_data)
            player.reset(playerspawn[0],playerspawn[1])
            game_state = 0
        if exit_button.draw():
            run = False

    pygame.display.update()

pygame.quit()
from os import truncate
import pygame
import pygame.math
from pygame import draw
from pygame.locals import *
from pygame.sprite import Sprite
from spritesheet import SpriteSheet
import csv
from random import randint

pygame.init()

clock = pygame.time.Clock()
fps = 60 
screen_width = 1000
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tentacave')

#define game variables
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_TYPES = 21
ACCELERATION = 2
WATRES = 0.5
tile_size = screen_height//ROWS
max_velocity = 15
dt = 0
game_state = 3
screen_scroll = 0
bg_scroll = 0
playerspawn = [500, 500]
level = 0
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
octo_img = []
for num in range(1, 11):
    img = pygame.image.load(f'Assets/Octo_Sprites/Idle{num}.png')
    #img = pygame.transform.scale(img, (66,58))
    octo_img.append(img)

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


class Enemy():
    #pass in a rectangle and speed in the x and y directions
    def __init__(self, image, x, y,  hitbox, speedx, speedy):
        self.hitbox = hitbox
        self.speedx = speedx
        self.speedy = speedy
        self.width = hitbox.width
        self.height = hitbox.height
    def move(self, moving_left, moving_right, moving_up, moving_down):
        collide = False
        dx = 0
        dy = 0
        #x followed by y
        if moving_down:
            dy += self.speedy
        if moving_right:
            dx += self.speedx
        if moving_up:
            dy -= self.speedy
        if moving_left:
            dx -= self.speedx
        collide, dx, dy = self.collide(dx,dy)
        return collide, dx, dy

    def collide(self, dx, dy):
        collide = False
        for tile in world.obstacle_list:
            #x direction
            if tile[2].colliderect(self.hitbox.x+dx, self.hitbox.y, self.width, self.height):
                #check if on right side of block
                if dx < 0:
                    dx = 0
                    collide = True
                #check if on left side of block
                if dx > 0:
                    dx = 0
                    collide = True
            #y direction
            if tile[2].colliderect(self.hitbox.x, self.hitbox.y + dy, self.width, self.height):
                #check if below the block
                if dy < 0:
                    dy = 0
                    collide = True
                #check if above the block
                if dy > 0:
                    dy = 0
                    collide = True
        return collide, dx, dy









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
            for beegfeesh in beegfeesh_group:
                if beegfeesh.hitbox.colliderect(temp_rect):
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
    beegfeesh_group.empty()
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
                    mine = Mine(x*tile_size, y*tile_size)
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
                    beegfeeshR = Beegfeesh(x*tile_size, y*tile_size, True)
                    beegfeesh_group.add(beegfeeshR) 
                elif tile == 18:
                    beegfeeshL = Beegfeesh(x*tile_size, y*tile_size, False)
                    beegfeesh_group.add(beegfeeshL)
                elif tile == 19:
                    chest = Chest(x*tile_size, y*tile_size)
                    chest_group.add(chest)
                elif tile == 20:
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
        

class Urchin(Enemy, pygame.sprite.Sprite):
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/tile/Enemies/urchin.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.width = 30
        self.height = 30
        self.hitbox = pygame.Rect(x+10, y+10, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 1
        self.speedy = 2
        self.count = 0
    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        #scroll
        if self.rect.right > 0 and self.rect.left < screen_width:
            self.ai()
        self.hitbox.x+=screen_scroll
        self.rect.x+=screen_scroll   
    def ai(self):
        dx = 0
        dy = 0
        collide = False
        #little hops back and forth, adorable
        self.count+=1
        moving_left = False
        moving_right = False
        moving_down = False
        moving_up = False
        if self.count<=6:
            moving_left = True
        if self.count>6:
            moving_right = True
        if self.count <= 3 or (self.count>6 and self.count<=9):
            moving_up = True
        if (self.count <= 6 and self.count>3) or self.count > 9:
            moving_down = True
        if self.count>=12: 
            self.count=0
        collide, dx, dy = self.move(moving_left, moving_right, moving_up, moving_down)
        self.rect.x += dx
        self.rect.y += dy
        self.hitbox = pygame.Rect(self.rect.x+10, self.rect.y+10, self.width, self.height)



class Mine(Enemy, pygame.sprite.Sprite):
    direction = 1
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/tile/Enemies/mine.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = 30
        self.height = 30
        self.count = 0
        self.hitbox = pygame.Rect(x+6, y+8, self.width, self.height)
        self.speedx = 0
        Mine.direction+=1
        if Mine.direction==2:
            Mine.direction = -1
        else:
            Mine.direction = 1
        self.speedy = Mine.direction * 2
    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        if self.rect.right > 0 and self.rect.left < screen_width:
            self.ai()
        #scroll
        self.hitbox.x+=screen_scroll
        self.rect.x+=screen_scroll
    def ai(self):
        collide = False
        self.count += 1
        moving_left = False
        moving_right = False
        moving_down = False
        moving_up = True
        collide, dx, dy = self.move(moving_left, moving_right, moving_up, moving_down)
        self.rect.x += dx
        self.rect.y += dy
        self.hitbox = pygame.Rect(self.rect.x+6, self.rect.y+8, self.width, self.height)
        if collide:
            self.speedy *= -1

class Feesh(Enemy, pygame.sprite.Sprite):
    def __init__(self,x, y):
            pygame.sprite.Sprite.__init__(self)
            self.images = []
            self.index = 0
            self.elapsed = 0
            self.height = 46
            self. width = 76
            self.hitbox = pygame.Rect(x+1, y+12+25, self.width, self.height)
            margin = 2
            for num in range(1, 5):
                img = pygame.image.load(f'img/tile/Enemies/Feesh/{num}.png')
                img = pygame.transform.scale(img, (78, 60))
                self.images.append(img)
            self.rect = img.get_rect()
            self.rect.x = x
            self.rect.y = y+25
            self.speedx = 3
            self.speedy = 0
            self.image = self.images[self.index]
            self.move_counter = 0
            self.moving_left = False
            self.moving_right = True
            self.moving_down = False
            self.moving_up = False
    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        if self.rect.right > 0 and self.rect.left < screen_width:
            self.ai()
            if self.moving_right:
                self.image = self.images[self.index]
            elif self.moving_left:
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
    def ai(self):
        collide=False
        collide, dx, dy = self.move(self.moving_left, self.moving_right, self.moving_up, self.moving_down)
        self.rect.x += dx
        self.rect.y += dy
        self.hitbox = pygame.Rect(self.rect.x+1, self.rect.y+12, self.width, self.height)
        if self.move_counter > 100 or collide:
            self.moving_right = not self.moving_right
            self.moving_left = not self.moving_left
            self.move_counter = 0
        self.move_counter+=1


class Beegfeesh(Enemy, pygame.sprite.Sprite):
    def __init__(self, x, y, right):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.elapsed = 0
        self.height = 90
        self. width = 100
        self.hitbox = pygame.Rect(x+25, y+20, self.width, self.height)
        for num in range(1, 5):
            img = pygame.image.load(f'img/tile/Enemies/Beeg_Feesh/{num}.png')
            img = pygame.transform.scale(img, (160, 150))
            self.images.append(img)
        self.rect = img.get_rect()
        self.rect.x = x
        self.rect.y = y-20
        self.speedx = 15
        self.speedy = 0
        self.image = self.images[self.index]
        self.move_counter = 0
        if(right):
            self.moving_right = True
            self.moving_left = False
        elif(not right):
            self.moving_right = False
            self.moving_left = True
        self.moving_down = False
        self.moving_up = False
        self.moving = False
        self.charging = False

    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        if self.rect.right > 0 and self.rect.left < screen_width:
            self.ai()
            if self.moving_right:
                self.image = self.images[self.index]
            elif self.moving_left:
                self.image = pygame.transform.flip(
                    self.images[self.index], True, False)
            #add number of ticks transpired
            self.elapsed += dt
            #Limits update frequency
            if self.elapsed >= 100:
                self.index += 1
                if self.index == 4:
                    self.index = 0
                self.elapsed = 0
        #scroll
        self.hitbox.x += screen_scroll
        self.rect.x += screen_scroll

    def ai(self):
        dx = 0
        dy = 0
        collide = False
        if (self.moving_left and player.hitbox.x < self.hitbox.x) or (self.moving_right and player.hitbox.x > self.hitbox.x):
            if (player.hitbox.y <= self.hitbox.y+self.height+25) and (player.hitbox.y >= self.hitbox.y-25) and not self.charging:
                self.speedx = 15
                self.moving = True
                self.charging = True
        if self.moving:
            collide, dx, dy = self.move(self.moving_left, self.moving_right, self.moving_up, self.moving_down)
            self.rect.x += dx
            self.rect.y += dy
            self.hitbox = pygame.Rect(self.rect.x+25, self.rect.y+20, self.width, self.height)
        if self.move_counter == 0:
            if collide:
                self.moving = False
                self.moving_left = not self.moving_left
                self.moving_right = not self.moving_right
                if self.charging:
                    self.move_counter+=1
        elif self.move_counter <= 30:
            self.move_counter += 1
        elif self.move_counter>30:
            self.speedx = 2
            self.moving = True
            self.move_counter = 0
            self.charging = False


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
beegfeesh_group = pygame.sprite.Group()
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
count = 0
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
        beegfeesh_group.update()
        #draw groups
        mine_group.draw(screen)
        feesh_group.draw(screen)
        urchin_group.draw(screen)
        beegfeesh_group.draw(screen)
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
        screen.blit(octo_img[count//2], (screen_width//2-175,screen_height//3-150))
        screen.blit(start_img, (screen_width//2-300,screen_height//3-100))
        count+=1
        if count >=20:
            count = 0
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

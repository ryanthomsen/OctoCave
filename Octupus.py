import pygame
from pygame import draw
from pygame.locals import *
from pygame.sprite import Sprite
from spritesheet import SpriteSheet
from random import seed
from random import randint

pygame.init()

clock = pygame.time.Clock()
fps = 60 
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Octupus Game')

#define game variables
tile_size = 50
max_velocity = 75
acceleration = 2
velocity_decay = 1
dt = 0
speed_multiplier = .1
game_state = 3
#load images
bg_img = pygame.image.load('Assets/ocean.png')
restart_img = pygame.image.load('img/red/restart.png') 
play_img = pygame.image.load('img/red/play.png')
exit_img = pygame.image.load('img/red/exit.png')
start_img = pygame.image.load('img/start.png')
start_img = pygame.transform.scale(start_img, (600, 108))
complete_img = pygame.image.load('img/complete.png')
complete_img = pygame.transform.scale(complete_img, (750, 108))

class Velocity():

    def __init__(self, vel):
        self.vel = vel

    def SpeedLimit(self):
        if self.vel > max_velocity:
            self.vel = max_velocity
        if self.vel < -max_velocity:
            self.vel =-max_velocity

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
        
        self.image = self.images_U[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = 40
        self.height = 40
        self.hitbox = pygame.Rect(x+13, y+8, self.width, self.height)
        self.vel_x = Velocity(0)
        self.vel_y = Velocity(0)

    def update(self, game_state):
        global dt
        dx = 0
        dy = 0
        #animation
        if self.direction == 1:
            self.image = self.images_U[self.index]
        if self.direction == 2:
            self.image = self.images_D[self.index]
        if self.direction == 3:
            self.image = self.images_R[self.index]
        if self.direction == 4:
                self.image = self.images_L[self.index]

        if game_state == 0:
            #get keypresses
            key = pygame.key.get_pressed()
            if (key[pygame.K_LEFT]):
                self.vel_x.vel -= acceleration
                self.vel_x.SpeedLimit()
                self.direction = 4
            if (key[pygame.K_RIGHT]):
                self.vel_x.vel += acceleration
                self.vel_x.SpeedLimit()
                self.direction = 3
            if (key[pygame.K_UP]):
                self.vel_y.vel -= acceleration
                self.vel_y.SpeedLimit()
                self.direction = 1
            if (key[pygame.K_DOWN]):
                self.vel_y.vel += acceleration
                self.vel_y.SpeedLimit()
                self.direction = 2
            
            #momentum decays when not moving
            #x-decay
            if (not key[pygame.K_LEFT]) & (not key[pygame.K_RIGHT]):
                if self.vel_x.vel > velocity_decay:
                    self.vel_x.vel -=velocity_decay
                elif self.vel_x.vel < -velocity_decay:
                    self.vel_x.vel += velocity_decay
                elif (self.vel_x.vel < velocity_decay & self.vel_x.vel > -velocity_decay):
                    self.vel_x.vel=0
            #y-decay
            if (not key[pygame.K_UP]) & (not key[pygame.K_DOWN]):
                if self.vel_y.vel > velocity_decay:
                    self.vel_y.vel -= velocity_decay
                elif self.vel_y.vel < -velocity_decay:
                    self.vel_y.vel += velocity_decay           
                elif (self.vel_y.vel < velocity_decay & self.vel_y.vel > -velocity_decay):
                    self.vel_y.vel=0       
        
            #update temporary coordinates
            dx += self.vel_x.vel
            dy += self.vel_y.vel

            #check for collision
            for tile in world.tile_list:
                #x direction
                #check if on left side of block
                if tile[1].colliderect(self.hitbox.x+dx*speed_multiplier, self.hitbox.y, self.width, self.height):
                    if self.vel_x.vel < 0:
                        dx = (tile[1].right - self.hitbox.left)/speed_multiplier
                        self.vel_x.vel = 0
                #check if on right side of block
                    elif self.vel_x.vel > 0:
                        dx = (tile[1].left - self.hitbox.right)/speed_multiplier
                        self.vel_x.vel = 0
                #y direction
                if tile[1].colliderect(self.hitbox.x, self.hitbox.y+dy*speed_multiplier, self.width, self.height):
                    #check if below the block
                    if self.vel_y.vel < 0:
                        dy = (tile[1].bottom - self.hitbox.top)/speed_multiplier
                        self.vel_y.vel = 0
                    #check if above the block
                    elif self.vel_y.vel >= 0:
                        dy = (tile[1].top - self.hitbox.bottom)/speed_multiplier
                        self.vel_y.vel = 0
                #check for enemy collision
                for mine in mine_group:
                    if mine.hitbox.colliderect(self.hitbox):
                        game_state = -1
                for feesh in feesh_group:
                    if feesh.hitbox.colliderect(self.hitbox):
                        game_state = -1
                for urchin in urchin_group:
                    if urchin.hitbox.colliderect(self.hitbox):
                        game_state = -1        
                if pygame.sprite.spritecollide(self, chest_group, False):
                    game_state = 4
            #update player coordinates
            self.rect.x += dx*speed_multiplier
            self.rect.y += dy*speed_multiplier
            self.hitbox.x += dx*speed_multiplier
            self.hitbox.y += dy*speed_multiplier
        elif game_state == -1:
            self.image =self.images_Dead[self.index]
            self.image = pygame.transform.scale(self.image, (66,58))
            if (self.rect.y > 50):
                self.rect.y-=5

            
        #draw players onto screen
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255,255,255), self.hitbox, 2)

        #add number of ticks transpired
        self.elapsed += dt
        #Limits update frequency
        if self.elapsed >= 100:
            self.index+=1
            if self.index == 10:
                self.index = 0
            self.elapsed = 0

        return game_state

    def reset(self,x,y):
        self.images_U = []
        self.images_D = []
        self.images_R = []
        self.images_L = []
        self.images_Dead = []
        self.index = 0
        self.elapsed = 0
        self.direction = 2
        #player sprite loading
        for num in range(1, 11):
            self.img = pygame.image.load(f'Assets/Octo_Sprites/U ({num}).png')
            self.img = pygame.transform.scale(self.img, (66,58))
            self.images_U.append(self.img)
            self.img = pygame.transform.flip(self.img, False, True)
            self.images_D.append(self.img)
            self.img = pygame.image.load(f'Assets/Octo_Sprites/R ({num}).png')
            self.img = pygame.transform.scale(self.img, (66,58))
            self.images_R.append(self.img)
            self.img = pygame.transform.flip(self.img, True, False)
            self.images_L.append(self.img)
            self.img = pygame.image.load(f'Assets/Octo_Sprites/Dead ({num}).png')
            self.images_Dead.append(self.img)
        
        self.image = self.images_U[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = 45
        self.height = 45
        self.hitbox = pygame.Rect(x+11, y+5, self.width, self.height)
        self.vel_x = Velocity(0)
        self.vel_y = Velocity(0)



class World():
    def __init__(self, data):
        self.tile_list = []
        #load spritesheets
        #environment = SpriteSheet('Assets/underwater-diving/PNG/environment/tiles2.png')
        #margin = 16
        #load images
        main_tile_img = pygame.image.load('img/tile/TileMain.png')
        tile_top_img = pygame.image.load('img/tile/TileTop.png')
        tile_bot_img = pygame.image.load('img/tile/TileBot.png')
        tile_single_img = pygame.image.load('img/tile/TileSingle.png')


        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(main_tile_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)      
                if tile == 2:
                    img = pygame.transform.scale(tile_top_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(tile_bot_img, (tile_size, 72))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)                    
                if tile == 4:
                    img = pygame.transform.scale(tile_single_img, (tile_size, 72))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 5:
                    #Randomizer for height
                    random_int = randint(-50, 50)
                    mine = Mine(col_count * tile_size, row_count * tile_size +random_int, random_int, 100)
                    mine_group.add(mine)
                if tile == 6:
                    feesh = Feesh(col_count * tile_size, row_count * tile_size)
                    feesh_group.add(feesh)
                if tile == 7:
                    urchin = Urchin(col_count * tile_size, row_count * tile_size, 1)
                    urchin_group.add(urchin)
                if tile == 8:
                    urchin = Urchin(col_count * tile_size, row_count * tile_size, 2)
                    urchin_group.add(urchin)       
                if tile == 9:
                    chest = Chest(col_count * tile_size, row_count * tile_size)
                    chest_group.add(chest)

                col_count += 1
            row_count += 1

    def draw (self):
        for tile in self.tile_list:
            screen.blit(tile[0],tile[1])
            #pygame.draw.rect(screen, (255,0,255), tile[1], 2)

class Chest(pygame.sprite.Sprite):
    def __init__(self,x, y):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load('img/tile/chest.png')
            self.image =pygame.transform.scale(self.image, (50,40))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y+10
            self.touched = False

class Urchin(pygame.sprite.Sprite):
    def __init__(self,x, y, direction):
            pygame.sprite.Sprite.__init__(self)
            self.images = []
            self.index = 0
            self.count = 1
            if (direction == 1 or direction == 2):
                for num in range (1, 5):
                    self.img = pygame.image.load(f'img/tile/urchin/urchin{num}.png')
                    self.img = pygame.transform.scale(self.img, (54, 50))
                    self.hitbox = pygame.Rect(x+2, y+2, 48, 48)
                    if direction == 2:
                        self.img = pygame.transform.flip(self.img, True, True)
                    self.images.append(self.img)
            self.image = self.images[self.index]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        self.image = self.images[self.index]
        if(self.count%10 == 0):
            #dosomething
            self.index+=1
        if(self.count ==30):
            self.count = 0
            self.index = 0
        self.count+=1
            
        

class Mine(pygame.sprite.Sprite):
    def __init__(self,x, y, bob, bob_max):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load('img/tile/mine.png')
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

class Feesh(pygame.sprite.Sprite):
    def __init__(self,x, y):
            pygame.sprite.Sprite.__init__(self)
            feesh = SpriteSheet('img/tile/feesh.png')
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
        



world_data =[
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,-1,-1,8,-1,-1,8,-1,-1,8,-1,-1,8,-1,-1,8,-1,-1,1,1],
[1,-1,-1,-1,-1,-1,6,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,1],
[1,-1,2,2,2,2,2,2,2,2,2,2,2,2,2,1,-1,-1,1,1],
[1,-1,1,1,-1,1,1,1,1,-1,1,1,1,1,1,1,-1,-1,1,1],
[1,-1,1,1,-1,1,1,1,1,-1,1,1,1,1,1,1,-1,5,1,1],
[1,-1,-1,-1,-1,-1,6,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,1,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,-1,-1,1,-1,-1,1,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,5,-1,1,-1,-1,1,1],
[1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,-1,-1,1,-1,-1,1,1],
[1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,-1,-1,1,5,-1,1,1],
[1,2,2,2,2,2,2,2,2,2,-1,1,1,-1,5,1,-1,-1,1,1],
[1,2,1,1,1,1,1,1,1,1,5,-1,-1,-1,-1,-1,-1,-1,1,1],
[1,1,1,1,1,1,1,1,1,1,-1,2,1,-1,-1,1,-1,-1,1,1],
[1,-1,-1,-1,-1,-1,8,-1,-1,-1,-1,1,1,5,-1,1,-1,5,1,1],
[1,-1,-1,7,-1,-1,-1,-1,-1,7,-1,1,1,-1,-1,1,-1,-1,1,1],
[1,-1,2,2,2,2,2,2,2,2,2,1,1,-1,-1,1,-1,-1,-1,-1],
[1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,9,-1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1]
]


player = Player(150, screen_height//2)
mine_group = pygame.sprite.Group()
feesh_group = pygame.sprite.Group()
urchin_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
world = World(world_data)

#create buttons
restart_button = Button(screen_width//2 - 246, screen_height//2+100, restart_img)
play_button = Button(screen_width//2 - 246, screen_height//2+100, play_img)
exit_button = Button(screen_width//2 + 100, screen_height//2+100, exit_img)

#main
run= True
while run:
    dt = clock.tick(60)
    screen.blit(bg_img, (0,0))
    if game_state ==4:
        screen.blit(complete_img, (screen_width//2-375,screen_height//3-100))
        if(play_button.draw()):
            game_state=0
            player.reset(150, screen_height//2)
        if(exit_button.draw()):
            run=False
    elif game_state ==3:
        screen.blit(start_img, (screen_width//2-300,screen_height//3-100))
        if(play_button.draw()):
            game_state=0
        if(exit_button.draw()):
            run=False
    else:
        world.draw()

        if game_state==0:
            mine_group.update()
            feesh_group.update()
            urchin_group.update()
        mine_group.draw(screen)
        feesh_group.draw(screen)
        urchin_group.draw(screen)
        chest_group.draw(screen)
        game_state = player.update(game_state)

        if game_state == -1:
            if restart_button.draw():
                player.reset(150, screen_height//2)
                game_state = 0
            if exit_button.draw():
                run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()
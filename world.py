#This is the World file responsible for generating the world drom a list of tile data
import pygame
import config
from config import tile_size, screen, ROWS, COLS
from image_loader import tile_img_list, farbg_img, closebg_img, midbg_img
import enemies
import collectibles
from random import randint
pygame.init()

#Class for the world object, constains a list of obstacles, decorations
#as well as sprite groups for enemies and collectivles
class World():
    def __init__(self, data):
        self.obstacle_list = [] #Contains list of tiles that collide with player
        self.decoration_list = [] #Contains list of tiles that do not collide with player
        #world sprite groups
        #Enemies
        self.mine_group = pygame.sprite.Group()
        self.feesh_group = pygame.sprite.Group()
        self.urchin_group = pygame.sprite.Group()
        self.beegfeesh_group = pygame.sprite.Group()
        #Collectibles
        self.chest_group = pygame.sprite.Group()


    #Method designed to take a list of tile info from a data.csv file
    #And process it into a pygame readable level
    def process_data(self, data):
        self.level_length =len(data[0])
        #iterate through each value in level data list
        #And assign appropriate image rect, img, and location according
        #to info in list
        for y, row in enumerate(data):
            for x, tile in enumerate(row):

                if tile>=0 and tile <= 12:
                    img = tile_img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    #Hitbox assignment for fullsize tiles
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
                    #Hitbox assignment for smaller tiles, like corners
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
                    #Adds tiles to obstacle list
                    self.obstacle_list.append(tile_data)
                #Adds enemies to appropriate sprite groups
                #Mines
                elif tile == 13:
                    #Randomizer for height
                    random_int = randint(-50, 50)
                    mine = enemies.Mine(x*tile_size, y*tile_size)
                    self.mine_group.add(mine)
                #Feesh
                elif tile == 14:
                    feesh = enemies.Feesh(x*tile_size, y*tile_size)
                    self.feesh_group.add(feesh)
                #Urchin Facing up
                elif tile == 15:
                    urchin = enemies.Urchin(x*tile_size, y*tile_size)
                    self.urchin_group.add(urchin)
                #Urchin facing down
                elif tile == 16:
                    urchin = enemies.Urchin(x*tile_size, y*tile_size)
                    self.urchin_group.add(urchin)
                #Right facing beeg feesh       
                elif tile == 17:
                    beegfeeshR = enemies.Beegfeesh(x*tile_size, y*tile_size, True)
                    self.beegfeesh_group.add(beegfeeshR) 
                #Left facing beeg feesh
                elif tile == 18:
                    beegfeeshL = enemies.Beegfeesh(x*tile_size, y*tile_size, False)
                    self.beegfeesh_group.add(beegfeeshL)
                #Chest collectible
                elif tile == 19:
                    chest = collectibles.Chest(x*tile_size, y*tile_size)
                    self.chest_group.add(chest)
                #Player character
                elif tile == 20:
                    playerspawn = (x*tile_size, y*tile_size)
        #Returns playerspawn location for use in other classes
        return playerspawn
    #Draw method for world objects, only renders obstacles
    #and decorations as other objects have their own draw methods
    def draw (self):
        for tile in self.obstacle_list:
            tile[1][0] += config.screen_scroll
            tile[2][0] += config.screen_scroll
            screen.blit(tile[0],tile[1])
            #Option to render tile hitboxes
            #pygame.draw.rect(screen, (255,0,255), tile[2], 2)
        for tile in self.decoration_list:
            tile[1][0] += config.screen_scroll
            screen.blit(tile[0],tile[1])
    #Reset for world. empties groupss and data list
    def reset_level(self):
        self.mine_group.empty()
        self.chest_group.empty()
        self.feesh_group.empty()
        self.urchin_group.empty()
        self.beegfeesh_group.empty()
        data = []
        for row in range(ROWS):
            r = [-1]*COLS
            data.append(r)
        return data
    
    #blits 3 instances of the background image. This more than covers
    #The max level length. Should longer levels be desired plans are
    #to implement a feature to move the left background image to the right
    #once its right edge is at 0
    def draw_bg():
        #Fill background with blue color in case bg fails
        screen.fill((0,0,255))
        width = farbg_img.get_width()
        #blit 3 instances of the farbg side by side that scrolls at half the the scroll speed
        screen.blit(farbg_img, (0-config.bg_scroll*0.5,0))
        screen.blit(farbg_img, ((width)-config.bg_scroll*0.5,0))
        screen.blit(farbg_img, ((width*2)-config.bg_scroll*0.5,0))
        #blit 3 instances of the farbg side by side that scrolls at 70% of the the scroll speed
        screen.blit(midbg_img, (0-config.bg_scroll*0.7,0))
        screen.blit(midbg_img, ((width)-config.bg_scroll*0.7,0))
        screen.blit(midbg_img, ((width*2)-config.bg_scroll*0.7,0))
        #blit 3 instances of the farbg side by side that scrolls at 90% of the the scroll speed
        screen.blit(closebg_img, (0-config.bg_scroll*0.9,0))
        screen.blit(closebg_img, ((width*2)-config.bg_scroll*0.9,0))
            
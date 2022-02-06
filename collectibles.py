import pygame
import config
from image_loader import chest_img
##Currently this file only contains the chest object
#However this is where all collectibles would be stored

#Chest objects, acts as a level clear condition
class Chest(pygame.sprite.Sprite):

    #Setup for the chest object
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = chest_img
        self.image =pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.touched = False #A boolean to detect whether the player has collided with the chest
    def update(self):
        #scroll controller for the chest
        self.rect.x+=config.screen_scroll
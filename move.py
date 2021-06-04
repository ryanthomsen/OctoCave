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

ACCELERATION = .2
WATRES = .1
max_velocity = 10
dt = 0
vec = pygame.math.Vector2
class Player():
    def __init__(self, x, y):
        self.pos = vec(0,0)
        self.vel = vec(0,0)
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
                self.acc_y = ACCELERATION
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
            self.pos+=self.vel+(self.acc)/2
            self.rect.center=self.pos
            self.hitbox.center=self.pos
            #updates temporary coordinates and factors in the speed multiplier

            #check for collision
            #game_state = self.collide(dx, dy)
            #update player coordinates
            #self.rect.topleft = self.rect.x + dx, self.rect.y +dy
            #self.hitbox.topleft = self.hitbox.x + dx, self.hitbox.y + dy
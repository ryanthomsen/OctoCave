import pygame
from config import SCREEN_HEIGHT, SCREEN_WIDTH, screen
import config
from image_loader import urchin_image, mine_image, feesh_images, beeg_feesh_images
pygame.init()

##Enemy class establishing parameters standard across all enemies##
#common parameters include speed of enemy as well as its hitbox
#features a standard move method across all enemy types, as well as a collide method
class Enemy():
    #Class variable in order to allow collision to be checked against current world state
    world = []
    #Initialization for a default enemy
    #pass in a rectangle that defines the size of the hitbox for the enemy
    # and speed of the enemy in the x and y directions
    def __init__(self, hitbox, speedx, speedy):
        self.hitbox = hitbox
        self.speedx = speedx
        self.speedy = speedy
        self.width = hitbox.width
        self.height = hitbox.height
    #Move method that operates on boolean logic related to which direction the enemy is going
    #Move speed is determined by preset speeds when the enemy is created
    def move(self, moving_left, moving_right, moving_up, moving_down):
        #Initially sets change in x and y directions to 0
        dx = 0
        dy = 0
        #Moves the enemy in the corresponding direction depending on the state of the booleans
        #Positive x values move the enemy right, negative x speed = left
        #Positive y values move the enemy down, negative y speeds = up
        if moving_down:
            dy += self.speedy
        if moving_right:
            dx += self.speedx
        if moving_up:
            dy -= self.speedy
        if moving_left:
            dx -= self.speedx
        #Runs the collide method to see if the proposed change in x and y
        #coordinates would result in a collision with another tile and
        #updates the collide boolean as well as the change in x and y accordingly
        collide, dx, dy = self.collide(dx,dy)
        #Returns collide boolean as well as the change in x and y for use in later logic
        return collide, dx, dy
    def load_world(world1):
        Enemy.world = world1

    #Method to determine whether a collision will occur with the proposed movements between tile hitboxes
    def collide(self, dx, dy):
        collide = False
        #checks to make sure no collisions occur between tiles in the world's list of obstacles
        for tile in self.world.obstacle_list:
            #checks in x direction for collision between hitboxes
            if tile[2].colliderect(self.hitbox.x+dx, self.hitbox.y, self.width, self.height):
                #check if on right side of the tile that the enemy is colliding with 
                #by examining the direction the enemy is moving in
                if dx < 0:
                    #If collision does occur sets the movement in that direction to 0
                    dx = 0
                    collide = True
                #check if on left side of of the tile that the enemy is colliding with
                #by examining the direction the enemy is moving in
                if dx > 0:
                    #If collision does occur sets the movement in that direction to 0
                    dx = 0
                    collide = True
            #checks in y direction for the collision between hitboxes
            if tile[2].colliderect(self.hitbox.x, self.hitbox.y + dy, self.width, self.height):
                #check if underneath the tile that the enemy is colliding with 
                #by examining the direction the enemy is moving in
                if dy < 0:
                    #If collision does occur sets the movement in that direction to 0
                    dy = 0
                    collide = True
                #check if above the tile that the enemy is colliding with 
                #by examining the direction the enemy is moving in
                if dy > 0:
                    #If collision does occur sets the movement in that direction to 0
                    dy = 0
                    collide = True
        #Returns boolean associated with collision and new change in x and y
        return collide, dx, dy

#First enemy type. A basic obstacle that stays mostly stationary
class Urchin(Enemy, pygame.sprite.Sprite):
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = urchin_image
        self.width = 30
        self.height = 30
        self.hitbox = pygame.Rect(x+10, y+10, self.width, self.height) #hitbox smaller than actual image for more generous hit detection
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 1 #Speed added only for dynamic animation
        self.speedy = 2 #Speed added only for dynamic animation
        self.count = 0 # a tracker for animating the urchin for a more dynamic sprite than a stationary object
    def update(self):
        #Option to turn on hitboxes for debugging purposes
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)

        #Boolean logic to disable ai if off screen in order to save on resources
        if self.rect.right > 0 and self.rect.left < SCREEN_WIDTH:
            self.ai()
        #scroll controller
        self.hitbox.x+=config.screen_scroll
        self.rect.x+=config.screen_scroll   

    #Method controlling the ai of the urchin. Used only for animation in this case
    def ai(self):
        dx = 0 #change in x location
        dy = 0 #change in y location
        collide = False #Collision tracker
        ##magic behind the little hops back and forth, adorable##
        self.count+=1
        #Reset for movement booleans
        moving_left = False
        moving_right = False
        moving_down = False
        moving_up = False
        #hops left if count is less than 6
        if self.count<=6:
            moving_left = True
        #hops right if count is greater than 6
        if self.count>6:
            moving_right = True
        #Moves up for between 0-3 and 6-9
        if self.count <= 3 or (self.count>6 and self.count<=9):
            moving_up = True
        #Moves down for counts between 3-6 and 9-12
        if (self.count <= 6 and self.count>3) or self.count > 9:
            moving_down = True
        #Reset for counts = 12, loops the animation
        if self.count>=12: 
            self.count=0
        #Collision checker from enemy parent object. Assigns collision boolean as well as how far to change x and y coords
        collide, dx, dy = self.move(moving_left, moving_right, moving_up, moving_down)
        #Moves urchin position
        self.rect.x += dx
        self.rect.y += dy
        #Redraws hitbox in line with image rect. Less intensive than duplicating calculations
        self.hitbox = pygame.Rect(self.rect.x+10, self.rect.y+10, self.width, self.height)


#First dynamic Enemy. Not too dynamic, bounces up and down.
class Mine(Enemy, pygame.sprite.Sprite):
    #A global tracker for direction to ensure mines alternate directions
    global mine_direction
    #Value of 1 = down, value of -1 = up
    mine_direction = 1
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = mine_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = 30
        self.height = 30
        self.count = 0
        self.hitbox = pygame.Rect(x+6, y+8, self.width, self.height) #Hitbox for collision detection
        self.speedx = 0 #Object only moves in y direction so x speed is 0
        #Determines mine starting direction and alternates with each instance of mine object
        global mine_direction
        mine_direction+=1
        if mine_direction==2:
            mine_direction = -1
        else:
            mine_direction = 1
        self.speedy = mine_direction * 2
    #Update method for mine objects, handles scrolling and calls ai
    def update(self):
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        if self.rect.right > 0 and self.rect.left < SCREEN_WIDTH:
            self.ai()
        #scroll
        self.hitbox.x+=config.screen_scroll
        self.rect.x+=config.screen_scroll
    #MEthod controlling ai for the mine object
    def ai(self):
        collide = False #Collision checker
        self.count += 1
        #Movement booleans
        moving_left = False
        moving_right = False
        moving_down = False
        moving_up = True
        #Method from enemy parent object. Calculates change in x and y coordinate and checks for collision.
        collide, dx, dy = self.move(moving_left, moving_right, moving_up, moving_down)
        #Actually moves image Rect and hitbox
        self.rect.x += dx
        self.rect.y += dy
        self.hitbox = pygame.Rect(self.rect.x+6, self.rect.y+8, self.width, self.height)
        #If collision occurs invert direction of movement
        if collide:
            self.speedy *= -1

#Dynamic fish enemy that moves horizontally back and forth. Similar to mine but in x directions.
class Feesh(Enemy, pygame.sprite.Sprite):
    def __init__(self,x, y):
            pygame.sprite.Sprite.__init__(self)
            self.images = feesh_images #list of images as animation exists for feesh objects
            self.index = 0
            self.elapsed = 0 #Tracker for frames of animation that have occured
            self.height = 46
            self. width = 76
            self.hitbox = pygame.Rect(x+1, y+12+25, self.width, self.height) #hitbox for collision detection
            margin = 2
            self.image = self.images[self.index]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y+25
            self.speedx = 3
            self.speedy = 0
            self.move_counter = 0 #Movement counter in case a wall is not reached 
            self.moving_left = False
            self.moving_right = True
            self.moving_down = False
            self.moving_up = False

    def update(self):
        #Option to draw hitbox for debugging
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)

        #A boolean statement to reduce lag by preventing ai logic from occuring while off screen
        if self.rect.right > 0 and self.rect.left < SCREEN_WIDTH:
            self.ai()
            #Uses right facing images when moving right
            if self.moving_right:
                self.image = self.images[self.index]
            #Flips image to face left if moving left
            elif self.moving_left:
                self.image = pygame.transform.flip(self.images[self.index], True, False)
            #add number of ticks transpired since last update
            self.elapsed += config.num_ticks
            #Limits update frequency so fish does not animate too fast
            if self.elapsed >= 100:
                self.index+=1
                if self.index == 4:
                    self.index = 0
                self.elapsed = 0
        #scroll controller
        self.hitbox.x+=config.screen_scroll
        self.rect.x+=config.screen_scroll

     #Method controlling ai for the feesh object
    def ai(self):
        collide=False #Collision bool
        #Calculates change in x and y coordinate and checks for collision.
        collide, dx, dy = self.move(self.moving_left, self.moving_right, self.moving_up, self.moving_down)
        #Actually moves image Rect and hitbox
        self.rect.x += dx
        self.rect.y += dy
        self.hitbox = pygame.Rect(self.rect.x+1, self.rect.y+12, self.width, self.height)
        #Flips fish direction and resets move_counter on collison or after 100 pixels of movement
        if self.move_counter > 100 or collide:
            self.moving_right = not self.moving_right
            self.moving_left = not self.moving_left
            self.move_counter = 0
        self.move_counter+=1

#Dynamic enemy object that waits for player to be in line of sight then charges.
#Also waits after slamming into a wall for a short time
class Beegfeesh(Enemy, pygame.sprite.Sprite):
    #Initiliation for Beeg feesh object
    def __init__(self, x, y, right):
        pygame.sprite.Sprite.__init__(self)
        self.images = beeg_feesh_images #list of images as animation exists for beeg_feesh objects
        self.index = 0
        self.elapsed = 0 #Tracker for frames of animation that have occured
        self.height = 90
        self. width = 100
        self.hitbox = pygame.Rect(x+25, y+20, self.width, self.height) #hitbox for collision detection
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y-20
        self.speedx = 15
        self.speedy = 0
        self.move_counter = 0 #Movement counter for beegfeesh, used for wait after charge
        #Setup using supplied right boolean to determine initial direction to face
        if(right):
            self.triggerbox = pygame.Rect(x+125, y+20, 300, 90) #line of sight hitbox
            self.moving_right = True
            self.moving_left = False
        elif(not right):
            self.triggerbox = pygame.Rect(x-275, y+20, 300, 90) #line of sight hitbox
            self.moving_right = False
            self.moving_left = True
        #Movement Booleans for y direction, always false for beeg feesh
        self.moving_down = False
        self.moving_up = False
        self.moving = False #Bool to determine whether the enemy should be moving (slow or fast)
        self.charging = False #Bool to determine if fish is actively charging (fast movement only)
        self.triggered = False #Bool to determine if player has crossed line of sight
        self.waiting = False #Bool to determine whether the fish should be waiting after a charge

    def update(self):
        #Options to draw hitboxes for debugging
        #pygame.draw.rect(screen, (255,0,255), self.hitbox, 2)
        #pygame.draw.rect(screen, (100,30,255), self.triggerbox, 2)

        #Boolean logic to disable ai if off screen
        if self.rect.right > 0 and self.rect.left < SCREEN_WIDTH:
            self.ai()
            #Logic ensuring sprite is facing direction of possible movement as well as trigger boxes location
            if self.moving_right:
                self.image = self.images[self.index]
                self.triggerbox = pygame.Rect(self.rect.x+125, self.triggerbox.y, 300, 90) #line of sight hitbox
            elif self.moving_left:
                self.triggerbox = pygame.Rect(self.rect.x-275, self.triggerbox.y, 300, 90) #line of sight hitbox
                self.image = pygame.transform.flip(self.images[self.index], True, False)
            #add number of ticks transpired
            self.elapsed += config.num_ticks
            #Limits update frequency
            if self.elapsed >= 100:
                self.index += 1
                if self.index == 4:
                    self.index = 0
                self.elapsed = 0
        #scroll controller for all three rects
        self.hitbox.x += config.screen_scroll
        self.rect.x += config.screen_scroll
        self.triggerbox.x += config.screen_scroll

    #Ai controller for beeg feesh
    def ai(self):
        dx = 0 #change in x
        dy = 0 #change in y, always 0 for beeg_feesh
        collide = False #Collision bool
        #If moving triggered and not already charging begin charging and moving
        if (self.triggered and not self.charging and not self.waiting):
            self.speedx = 15
            self.moving = True
            self.charging = True
        #If movement bool says to move, begin moving and check for collision
        if self.moving and not self.waiting:
            collide, dx, dy = self.move(self.moving_left, self.moving_right, self.moving_up, self.moving_down)
            #Move image rect and redraws hitbox and triggerbox at new locations coordinates
            self.rect.x += dx
            self.hitbox = pygame.Rect(self.rect.x+25, self.rect.y+40, self.width, self.height)
            self.triggerbox = pygame.Rect(self.hitbox.x-200, self.rect.y+40, 500, 90)
        #Checks if a collision has occured and begins waiting if it has
        #Also reverses fish direction
        if collide:
            self.moving = False
            self.triggered = False
            self.charging = False
            self.waiting = True

        #Begins counting the wait down if fish should be waiting
        if self.waiting:
            self.move_counter += 1
            #After 90 ticks beeg feesh begins moving back to his previous location slowly
            #Trigger and charging conditions reset at this point, and both sprites and move direction flips
            #Speed is also set to 2 to simulate dejected movement back to original location if player out of los
            if self.move_counter > 90:
                self.waiting = False
                self.speedx = 2
                self.moving = True
                self.move_counter = 0
                self.moving_left = not self.moving_left
                self.moving_right = not self.moving_right

    #Method to set triggered to true if player collides with triggerbox
    def trigger(self):
        if not(self.triggered):
            self.triggered = True
import pygame 

#General Button class using pygame
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False
	#Draw method for Button, also acts as an update method
	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#checks for mouseover of button and if it is clicked
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True
		#Resets clicked state after mouse button is lifted
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draws the actual button
		surface.blit(self.image, (self.rect.x, self.rect.y))
		#Returns whether or not the button has been clicked
		return action
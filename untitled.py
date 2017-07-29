import pygame, os, sys, random
from pygame.locals import *

FPS = 60
WINDOWSIZE = (840, 560)

IMAGES = "images"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

GRAVITY = 0.3
CHAR_MAX_HORIZ_SPEED = 3
CHAR_MAX_VERT_SPEED = 600

pygame.init()

class Level:
	def __init__(self, filename, grounds):
		self.img = pygame.image.load(os.path.join(IMAGES, "foregrounds", filename)).convert_alpha()
		self.rect = self.img.get_rect()
		self.grounds = grounds

class Character:
	def __init__(self, name, pos):
		self.name = name
		self.imgs = {}
		# load movement img name and sort them
		for movement_dir in os.listdir(os.path.join(IMAGES, self.name)):
			self.imgs[movement_dir] = [img_name for img_name in os.listdir(os.path.join(IMAGES, self.name, movement_dir))]
			self.imgs[movement_dir].sort()
		# load movement imgs
		for movement_dir in os.listdir(os.path.join(IMAGES, self.name)):
			self.imgs[movement_dir] = [pygame.image.load(os.path.join(IMAGES, self.name, movement_dir, img_name)).convert_alpha() for img_name in os.listdir(os.path.join(IMAGES, self.name, movement_dir))]
		self.anim_speeds = {'idle_left': 15,
							'idle_right': 15,
							'walk_left': 5,
							'walk_right': 5,
							'jump_trans_right': 8,
							'jump_trans_left': 8,
							}
		self.anim_counter = 0
		self.walk_speed = 4
		self.jump_strength = 8
		self.xVel = 0
		self.yVel = 0
		self.movement_status = 'idle_right'
		# prev_movement_status to restore anim after jump_trans
		self.prev_movement_status = None
		# prev_movement_frame to see if movement changed from one frame to next
		self.prev_frame_movement = None
		self.img_num = 0
		self.img = self.imgs['idle_right'][self.img_num]
		self.rect = Rect(pos, self.img.get_size())
		self.is_on_ground = False
		self.is_jumping = False
		
	def check_ground(self, grounds):
		if self.rect.bottom >= WINDOWSIZE[1]:
			self.is_on_ground = True
			self.rect.bottom = WINDOWSIZE[1]
			self.yVel = 0
			return
		for ground in grounds:
			# ground: ((x, y), end_x)
			if self.rect.bottom >= ground[0][1] and self.rect.centerx >= ground[0][0] and self.rect.centerx <= ground[1]:
				self.is_on_ground = True
				self.rect.bottom = ground[0][1]
				self.yVel = 0
				return
		self.is_on_ground = False
			
	def update_rect(self):
		# self.img changes throughout anims, update rect as well
		center = self.rect.center
		self.rect.size = self.img.get_size()
		self.rect.center = center
		
	def update(self, events, grounds):
		# go through movement events and mark changes
		for event in events:
			if event.type == KEYDOWN:
				if event.key == K_LEFT:
					self.movement_status = 'walk_left'
				elif event.key == K_RIGHT:
					self.movement_status = 'walk_right'
				elif event.key == K_UP:
					if self.is_on_ground:
						self.is_jumping = True
						self.yVel = -self.jump_strength
						# save previous anim
						self.prev_movement_status = self.movement_status
						if 'left' in self.movement_status:
							self.movement_status = 'jump_trans_left'
						elif 'right' in self.movement_status:
							self.movement_status = 'jump_trans_right'
			elif event.type == KEYUP:
				if event.key == K_LEFT:
					self.movement_status = 'idle_left'
				elif event.key == K_RIGHT:
					self.movement_status = 'idle_right'
		
		# apply changes
		if self.movement_status == 'walk_left':
			self.xVel = -self.walk_speed
		elif self.movement_status == 'walk_right':
			self.xVel = self.walk_speed
		elif self.movement_status == 'idle_left':
			self.xVel = 0
		elif self.movement_status == 'idle_right':
			self.xVel = 0
				
		# apply gravity
		if not self.is_on_ground:
			self.yVel += GRAVITY
			
		# check max speeds
		if self.xVel < -CHAR_MAX_HORIZ_SPEED:
			self.xVel = -CHAR_MAX_HORIZ_SPEED
		elif self.xVel > CHAR_MAX_HORIZ_SPEED:
			self.xVel = CHAR_MAX_HORIZ_SPEED
		if self.yVel < -CHAR_MAX_VERT_SPEED:
			self.yVel = -CHAR_MAX_VERT_SPEED
		elif self.yVel > CHAR_MAX_VERT_SPEED:
			self.yVel = CHAR_MAX_VERT_SPEED
			
		self.rect.x += self.xVel
		self.rect.y += self.yVel
		
		# move char in bounds if out
		if self.rect.left < 0:
			self.rect.left = 0
			self.xVel = 0
		elif self.rect.right > WINDOWSIZE[0]:
			self.rect.right = WINDOWSIZE[0]
			self.xVel = 0
		if self.rect.top < 0:
			self.rect.top = 0
			self.yVel = 0
		
		# update is_on_ground
		self.check_ground(grounds)
		
		# if change in img, reset anim_counter as well
		if self.prev_frame_movement != self.movement_status:
			self.anim_counter = -1
		
		# update animations
		# anim_counter is -1 only upon movement change
		if self.anim_counter == -1:
			self.img_num = 0
			self.img = self.imgs[self.movement_status][self.img_num]
		self.anim_counter += 1
		# if it's time to switch to the next img...
		if self.anim_counter == self.anim_speeds[self.movement_status]:
			# go to next img
			self.img_num += 1
			# if reached end of anim for this movement...
			if self.img_num == len(self.imgs[self.movement_status]):
				# loop back over it
				self.img_num = 0
				# if jump_trans anim is over...
				if 'jump_trans' in self.movement_status:
					# restore previous anim
					self.movement_status = self.prev_movement_status
			self.anim_counter = 0
			self.img = self.imgs[self.movement_status][self.img_num]
			
		# update rect to reflect any changes in img
		self.update_rect()
			
		self.prev_frame_movement = self.movement_status

def main(args):
	windowSurf = pygame.display.set_mode(WINDOWSIZE)
	fpsClock = pygame.time.Clock()
	
	char = Character("joe", (75, 200))
	bg1 = pygame.image.load(os.path.join(IMAGES, "backgrounds", "bg1.png")).convert()
	
	# tuples of ((x, y), end_x) where (x, y) is the starting point of ground and end_x is where it ends on the x-axis
	grounds = [((0, 482), 161),
				((248, 482), 369),
				((369, 412), 472),
				((469, 354), 532),
				((535, 313), 598),
				((614, 284), 805),
				]
	level = Level("fg1.png", grounds)
	
	while True:
		# UPDATE
		
		events = pygame.event.get()
		for event in events:
			if event.type == KEYUP:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
			elif event.type == QUIT:
				pygame.quit()
				sys.exit()
				
		char.update(events, level.grounds)
		
		# DRAW
		
		windowSurf.blit(bg1, (0, 0))
		windowSurf.blit(level.img, level.rect)
		windowSurf.blit(char.img, char.rect)
		
		#pygame.draw.rect(windowSurf, BLACK, char.rect, 3)
			
		pygame.display.update()
		fpsClock.tick(FPS)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

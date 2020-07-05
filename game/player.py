import pyglet, math, copy
from pyglet.window import key
from . import physicalobject, resources, cactus, bird


'''
Jumping magic parabola equation
y = (4h / -w^2)(x^2 - wx)
y = ((4 * h) / (-(w ** 2))) * (x ** 2 - (w * x))
'''


class Player(physicalobject.PhysicalObject):

	def __init__(self, *args, **kwargs):
		super(Player, self).__init__(img=resources.playerimages['idle'], *args, **kwargs)

		self.scale = 0.25

		self.ylevel = self.y

		self.jumping = False
		self.jumpheight = 225
		self.jumplength = 16
		self.jumptime = 0
		self.jumpverticalvelocity = 0

		self.ducking = False

		self.timer = 0
		self.run = True

		self.keyrelease = False

		self.cinput = [False, False]

		self.collided = False
		self.xbuffer = 15

		self.cactidistance = None
		self.birddistance = None

		self.key_handler = key.KeyStateHandler()
		self.event_handlers = [self, self.key_handler]

	def jumppos(self, h, w, x):
		return int(round((((4 * h) / (-(w ** 2))) * (x ** 2 - (w * x))), 0))

	def update(self, dt, gameobjects, gameover, playercontrolled, cinput):
		super(Player, self).update(dt)

		if not gameover:
			us = 1/120  # update speed
			ud = us / dt

			self.cinput = cinput

			controlinput = {'up': False, 'down': False}

			if playercontrolled:
				controlinput['up'] = any([self.key_handler[i] for i in [key.UP, key.W, key.SPACE]])
				controlinput['down'] = any([self.key_handler[i] for i in [key.DOWN, key.S]])
			else:
				controlinput['up'] = self.cinput[0]
				controlinput['down'] = self.cinput[1]

			if controlinput['up']:
				if not self.jumping:
					self.jumping = True
					self.jumptime = 0

					self.image = resources.playerimages['jump']

			if controlinput['down']:
				self.ducking = True
			else:
				self.ducking = False

			if self.jumping:
				if self.ducking:
					if self.jumptime <= self.jumplength / 2:
						self.jumptime = self.jumplength - self.jumptime
					self.jumptime += ud
				addy = self.jumppos(self.jumpheight, self.jumplength, self.jumptime)
				newy = self.ylevel + addy
				self.y = newy

				if newy > 0: self.jumpverticalvelocity = 1
				elif newy < 0: self.jumpverticalvelocity = -1
				else: self.jumpverticalvelocity = 0

				self.jumptime += ud

			if self.jumptime > self.jumplength:
				self.y = self.ylevel
				self.jumping = False
				self.jumptime = 0

				# self.image = resources.playerimages['run'][0]


			self.timer += 1
			if self.timer == 6:
				self.run = not self.run
				if not self.jumping:
					if self.ducking:
						self.image = resources.playerimages['low'][0] if self.run else resources.playerimages['low'][1]
					else:
						self.image = resources.playerimages['run'][0] if self.run else resources.playerimages['run'][1]
				self.timer = 0


			try:
				self.cactidistance = next(x for x in gameobjects if type(x) == cactus.Cactus).x - (self.x + self.width)
			except StopIteration:
				self.cactidistance = -1

			try:
				self.birddistance = next(x for x in gameobjects if type(x) == bird.Bird).x - (self.x + self.width)
			except StopIteration:
				self.birddistance = -1


			for obj in gameobjects:
				if type(obj) in [cactus.Cactus, bird.Bird]:
					if self.collision(obj):
						self.collided = True
						break
					else: self.collided = False

			if self.collided:
				self.dead = True
				self.image = resources.playerimages['death']
				self.keyrelease = True

			return self.collided

		else:
			if self.keyrelease:
				if not any([self.key_handler[i] for i in [key.UP, key.W, key.SPACE]]):
					self.keyrelease = False
			elif any([self.key_handler[i] for i in [key.UP, key.W, key.SPACE]]):
				return 1
			elif any([self.key_handler[i] for i in [key.ESCAPE]]):
				return 2


	def collisiondetection(self, x1, x2, x3, x4):
		return any([
			x1 <= x3 <= x2,
			x1 <= x4 <= x2,
			x3 <= x1 <= x4,
			x3 <= x2 <= x4
		])

	def collision(self, obj):
		if self.collisiondetection(self.x + self.xbuffer, self.x + self.width, obj.x + self.xbuffer, obj.x + obj.width - self.xbuffer):
			if self.collisiondetection(self.y, self.y + self.height, obj.y, obj.y + obj.height):
				# print('ow')
				return True
		return False
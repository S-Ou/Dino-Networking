import pyglet, math, copy, random
from pyglet.window import key
from . import physicalobject, resources

class Cactus(physicalobject.PhysicalObject):

	def __init__(self, *args, **kwargs):
		n = random.randint(0, 4)
		super(Cactus, self).__init__(img=resources.enemyimages["cactus"][n], *args, **kwargs)

		self.scale = 0.2 if random.randint(1, 100) < 30 else 0.25

		self.key_handler = key.KeyStateHandler()
		self.event_handlers = [self, self.key_handler]

	def update(self, dt, basespeed, gamespeed, gameover):
		super(Cactus, self).update(dt)

		if gameover:
			self.velocityx = 0
			return

		us = 1/120  # update speed
		ud = us / dt

		self.velocityx = (-1 * basespeed * gamespeed) * ud

		if self.x < 0 - self.width:
			# self.x = 1440
			self.dead = True
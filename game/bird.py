import pyglet, math, copy, random
from pyglet.window import key
from . import physicalobject, resources

class Bird(physicalobject.PhysicalObject):

	def __init__(self, *args, **kwargs):
		super(Bird, self).__init__(img=resources.enemyimages["bird"][1], *args, **kwargs)

		self.scale = 0.25

		self.timer = 0
		self.flap = True

		self.key_handler = key.KeyStateHandler()
		self.event_handlers = [self, self.key_handler]

	def update(self, dt, basespeed, gamespeed, gameover):
		super(Bird, self).update(dt)

		if gameover: 
			self.velocityx = 0
			return

		us = 1/120  # update speed
		ud = us / dt / dt

		self.velocityx = (-1 * basespeed * gamespeed - 100) * ud

		if self.x < 0 - self.width:
			# self.x = 1440
			self.dead = True

		self.timer += 1
		if self.timer == 6:
			self.flap = not self.flap
			self.image = resources.enemyimages['bird'][0] if self.flap else resources.enemyimages['bird'][1]
			self.timer = 0
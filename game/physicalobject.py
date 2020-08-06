import pyglet


class PhysicalObject(pyglet.sprite.Sprite):

	def __init__(self, *args, **kwargs):
		super(PhysicalObject, self).__init__(*args, **kwargs)

		self.velocityx = 0.0

		self.dead = False

	def update(self, dt):
		self.x += self.velocityx * dt
		# self.x += self.velocityx
		# self.y += self.velocityy * dt
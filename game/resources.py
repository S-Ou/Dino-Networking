import pyglet, copy


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2


pyglet.resource.path = ['resources']
pyglet.resource.reindex()

def loadmultiimagedict(tree, centre=False):
	output = {}
	for k, v in tree.items():
		if type(v) == list:
			sublist = []
			for i in v:
				x = pyglet.resource.image(i)
				if centre: center_image(x)
				sublist.append(x)
			output[k] = sublist
		else:
			x = pyglet.resource.image(v)
			if centre: center_image(x)
			output[k] = copy.copy(x)
	return output

pimagedict = {
	"idle": "idle.png",
	"jump": "jump.png",
	"death": "death.png",
	"low": [
		"low1.png",
		"low2.png"
	],
	"run": [
		"run1.png",
		"run2.png"
	],
}

cimagedict = {
	"cactus": [
		"cactus1.png",
		"cactus2.png",
		"cactus3.png",
		"cactus4.png",
		"cactus5.png"
	],
	"bird": [
		"enemy1.png",
		"enemy2.png"
	]
}

bimagedict = {
	"floor": [
		"floor.png",
	],
	"cloud": [
		"cloud.png"
	]
}

playerimages = loadmultiimagedict(pimagedict, False)
enemyimages = loadmultiimagedict(cimagedict, False)
backgroundimages = loadmultiimagedict(bimagedict, False)

# print(playerimages)
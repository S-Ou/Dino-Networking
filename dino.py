import pyglet, random, math, copy, time, neat
from pyglet.window import key
from game import player, cactus, resources, bird, floor, cloud
import visualize

class Game(pyglet.window.Window):
    # gamewindow = pyglet.window.Window(1200, 675)

    def __init__(self, xs, ys, playercontrolled):
        super().__init__(width=xs, height=ys, caption="Chrome Dino x Neural Network")
        self.dinobatch = pyglet.graphics.Batch()
        self.enemybatch = pyglet.graphics.Batch()
        self.backgroundbatch = pyglet.graphics.Batch()

        pyglet.font.add_file("resources/PressStart2P-Regular.ttf")
        self.font = pyglet.font.load('Press Start 2P', 16)

        RGBA = (255,255,255,255)
        self.background = pyglet.image.SolidColorImagePattern(RGBA).create_image(self.width, self.height)

        self.counter = pyglet.window.FPSDisplay(window=self)
        self.counter.label.x = 20
        self.counter.label.y = 340
        self.counter.label.font_name = "Press Start 2P"
        self.counter.label.font_size = 15
        self.counter.label.color = (83, 83, 83, 255)

        self.key_handler = key.KeyStateHandler()
        self.keyboard = [self, self.key_handler]

        self.score = 0
        self.gameovertext = 0

        self.gameobjects = []
        self.eventstacksize = 0

        self.successcount = 0

        self.cinput = [False, False]
        self.nninput = {
            "dheight": None,
            "dwidth": None,
            "djumpheight": None,
            "dvdirection": None,
            "dcdistance": None,
            "cheight": None,
            "cwidth": None, 
            "dbdistance": None,
            "bheight": None,
            "bwidth": None,
            "bypos": None,
            "gamespeed": None,
        }

        self.gameover = False

        self.playercontrolled = playercontrolled

        self.birdlocations = [20, 76, 175]

        self.distancewait = 30
        self.wait = 0

        self.cloudwaittime = 100
        self.cloudwait = 0

        self.basespeed = 30
        self.gamespeed = 1
        self.gameaccel = 0.0001

        self.collided = False

        self.reset()

    def dinoinputs(self):
        inputs = {
            "dheight": self.dino.height,
            "dwidth": self.dino.width,
            "djumpheight": self.dino.y,
            "dvdirection": self.dino.jumpverticalvelocity,
            "dcdistance": self.dino.cactidistance,
            "dbdistance": self.dino.birddistance,
        }

        try:
            acactus = next(x for x in self.gameobjects if type(x) == cactus.Cactus)
            inputs.update({
                "cheight": acactus.height,
                "cwidth": acactus.width,
            })
        except StopIteration:
            inputs.update({
                "cheight": -1,
                "cwidth": -1,
            })


        try:
            abird = next(x for x in self.gameobjects if type(x) == bird.Bird)
            inputs.update({
                "bheight": abird.height,
                "bwidth": abird.width,
                "bypos": abird.y,
            })
        except StopIteration:
            inputs.update({
                "bheight": -1,
                "bwidth": -1,
                "bypos": -1,
            })

        inputs.update({
                "gspeed": self.gamespeed
            })
        
        return inputs

    def reset(self):
        while self.eventstacksize > 0:
            self.pop_handlers()
            self.eventstacksize -= 1

        # for to_remove in self.gameobjects:
        #     print(type(to_remove))
        #     to_remove.delete()
        #     self.gameobjects.remove(to_remove)

        # print(dir(self.enemybatch))

        self.dinobatch = pyglet.graphics.Batch()
        self.enemybatch = pyglet.graphics.Batch()
        self.backgroundbatch = pyglet.graphics.Batch()

        self.dino = player.Player(x=45, y=0, batch=self.dinobatch)
        self.ground = floor.Floor(x=-10, y=0, batch=self.backgroundbatch)
        self.enemy = []

        self.gameobjects.clear()
        self.gameobjects = [self.dino, self.ground] + self.enemy

        for obj in self.gameobjects:
            for handler in obj.event_handlers:
                self.push_handlers(handler)
                self.eventstacksize += 1
        self.push_handlers(self.keyboard)

        self.clouds = False
        self.birds = False

        self.score = 0
        self.gameovertext = 0
        self.gamespeed = 1
        self.collided = False
        self.successcount = 0

        self.gameover = False

        if not self.playercontrolled:
            for k, v in self.dinoinputs().items():
                self.nninput[k] = v
            self.nninput['gamespeed'] = self.gamespeed

        self.scoretext = pyglet.text.Label(
            text=f"{int(round(self.score, 0)):05d}", 
            x=1260,
            y=330,
            font_name='Press Start 2P',
            font_size=25,
            color=(83, 83, 83, 255),
            batch=self.backgroundbatch)

        self.gameovertext = pyglet.text.Label(
            text=f"GAME OVER", 
            x=self.width / 2,
            y=self.height / 2 + 20,
            font_name='Press Start 2P',
            font_size=25,
            color=(83, 83, 83, 0),
            anchor_x='center', anchor_y='center',
            batch=self.backgroundbatch)

        self.pressanykey = pyglet.text.Label(
            text=f"SPACE to play again  ESC to exit", 
            x=self.width / 2,
            y=self.height / 2 - 20,
            font_name='Press Start 2P',
            font_size=10,
            color=(83, 83, 83, 0),
            anchor_x='center', anchor_y='center',
            batch=self.backgroundbatch)

        self.speed = pyglet.text.Label(
            text=f"{self.gamespeed}",
            x=20,
            y=310,
            font_name='Press Start 2P',
            font_size=15,
            color=(83, 83, 83, 255),
            batch=self.backgroundbatch)

        self.countertext = pyglet.text.Label(
            text=f"{self.successcount}", 
            x=1260,
            y=290,
            font_name='Press Start 2P',
            font_size=25,
            color=(83, 83, 83, 255),
            batch=self.backgroundbatch)

        self.ow = pyglet.text.Label(
            text=f"ow", 
            x=500,
            y=200,
            font_name='Press Start 2P',
            font_size=25,
            color=(255, 255, 255, 0),
            batch=self.backgroundbatch)

    def on_draw(self):
        self.clear()
        self.background.blit(0, 0)
        self.backgroundbatch.draw()
        self.enemybatch.draw()
        self.dinobatch.draw()
        self.counter.draw()

    def changeinput(self, cinput):
        self.cinput = cinput
        return self.cinput


    def update(self, dt):
        if not self.gameover:
            us = 1/120  # update speed
            ud = us / dt
            # print(1 / dt)
            scoreadd = self.gamespeed * dt * 10
            # scoreadd = self.gamespeed * us * 10
            self.score += scoreadd
            self.scoretext.text = f"{int(round(self.score, 0)):05d}"

            # self.gamespeed += ud * self.gameaccel
            self.gamespeed += self.gameaccel
            self.gamespeed = round(self.gamespeed, 10)
            self.speed.text = f"{str(round(self.gamespeed, 4))}"

            self.countertext.text = f"{self.successcount}"

            for obj in self.gameobjects:
                if type(obj) in [cactus.Cactus, bird.Bird, floor.Floor, cloud.Cloud]:
                    obj.update(dt, self.basespeed, self.gamespeed, self.gameover)
                    continue
                if type(obj) in [player.Player]:
                    c = obj.update(dt, self.gameobjects, self.gameover, self.playercontrolled, self.cinput)
                    continue
                obj.update(dt, self.gameover)

            if not any([i.x >= 1440 - i.width for i in [obj for obj in self.gameobjects if type(obj) == floor.Floor]]):
                self.gameobjects.append(floor.Floor(x=1350, y=0, batch=self.backgroundbatch))

            if self.wait >= self.distancewait:
                if random.randint(1, 30) == 16:
                    if random.randint(1, 4) == 1 and self.birds:
                        self.gameobjects.append(bird.Bird(x=2000, y=random.choice(self.birdlocations), batch=self.enemybatch))
                    else:
                        self.gameobjects.append(cactus.Cactus(x=2000, y=0, batch=self.enemybatch))
                    self.wait = 0
            else: self.wait += 2 * ud

            if self.clouds:
                if self.cloudwait >= self.cloudwaittime:
                    # if random.randint(1, 300) == 16:
                    self.gameobjects.append(cloud.Cloud(x=1440, y=random.randint(150, 315), batch=self.backgroundbatch))
                    self.cloudwait = 0
                    self.cloudwaittime = random.randint(100, 900)
                else: self.cloudwait += ud

            if c and not self.collided:
                self.collided = True
                self.ow.x = random.randint(200, 1240)
                self.ow.y = random.randint(100, 300)
            elif not c and self.collided:
                self.collided = False

            # if self.collided: self.ow.color = (83, 83, 83, 255)
            # else: self.ow.color = (255, 255, 255, 0)

            for to_remove in [obj for obj in self.gameobjects if obj.dead]:
                if type(to_remove) not in [player.Player]:
                    if type(to_remove) in [cactus.Cactus, bird.Bird]:
                        self.successcount += 1
                    to_remove.delete()
                    self.gameobjects.remove(to_remove)
                else:
                    self.gameover = True

            if self.gameover: 
                self.gameovertext.color = (83, 83, 83, 255)
                self.pressanykey.color = (83, 83, 83, 255)
            else: 
                self.gameovertext.color = (83, 83, 83, 0)
                self.pressanykey.color = (83, 83, 83, 0)


            if not self.playercontrolled:
                for k, v in self.dinoinputs().items():
                    self.nninput[k] = v
                self.nninput['gamespeed'] = self.gamespeed


        else:
            for obj in self.gameobjects:
                if type(obj) in [cactus.Cactus, bird.Bird, floor.Floor, cloud.Cloud]:
                    obj.update(dt, self.basespeed, self.gamespeed, self.gameover)
                    continue
                if type(obj) in [player.Player]:
                    c = obj.update(dt, self.gameobjects, self.gameover, self.playercontrolled, self.cinput)
                    continue
                obj.update(dt, self.gameover)

            if not self.playercontrolled:
                self.close()

            if c == 1: 
                self.reset()
            elif c == 2:
                self.close()
                # pyglet.app.exit()


            # print(self.key_handler)
            # if any([self.key_handler[i] for i in [key.UP, key.W, key.SPACE]]):
            #     self.reset()
            #     print('hi')



def eval_genomes(genome, config):
    worky = Worker(genome, config)
    return worky.work()

class Worker(object):
    def __init__(self, genome, config):
        self.genome = genome
        self.config = config

    def work(self):
        gameinstance = Game(1440, 375, False)
        pyglet.clock.schedule_interval(gameinstance.update, 1 / 120.0)

        net = neat.nn.FeedForwardNetwork.create(self.genome, self.config)

        fitness = 0

        while pyglet.app.windows:
            pyglet.clock.tick()

            for window in pyglet.app.windows:
                actions = net.activate(list(window.dinoinputs().values()))

                window.changeinput([bool(round(i, 0)) for i in actions])
                
                # fitness = window.score
                fitness = window.successcount
                # fitness = window.score * window.successcount

                window.switch_to()
                window.dispatch_events()
                window.dispatch_event('on_draw')
                window.flip()

        return fitness


if __name__ == "__main__":
    pc = False

    if not pc:
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'neatconfig')

        p = neat.Population(config)

        pe = neat.ParallelEvaluator(4, eval_genomes)
        # No. of parallel instances ^


        # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-9')
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(1))

        winner = p.run(pe.evaluate, 5)
        # Generation Size           ^

        print('\nBest genome:\n{!s}'.format(winner))

        node_names = {
            -12: 'Dino Height',
            -11: 'Dino Width',
            -10: 'Height off ground',
            -9:  'Jump direction',
            -8:  'Distance to Cactus',
            -7:  'Distance to Bird',
            -6:  'Cactus Height',
            -5:  'Cactus Width',
            -4:  'Bird Height',
            -3:  'Bird Width',
            -2:  'Bird y-Position',
            -1:  'Game Speed',

             0:  'Jump',
             1:  'Duck',
        }

        try:
            # visualize.draw_net(config, winner, True)
            visualize.draw_net(config, winner, True, node_names=node_names)
            visualize.plot_stats(stats, ylog=False, view=True)
            visualize.plot_species(stats, view=True)
        except Exception as e:
            print('')

    else:
        gameinstance = Game(1440, 375, True)
        pyglet.clock.schedule_interval(gameinstance.update, 1 / 120.0)
        while pyglet.app.windows:
            pyglet.clock.tick()

            # for i in range(1000):
            #     random.randint(1, 10000)

            for window in pyglet.app.windows:
                window.switch_to()
                window.dispatch_events()
                window.dispatch_event('on_draw')
                window.flip()

        # pyglet.clock.unschedule(gameinstance.update)




'''
NEURAL NETWORK INPUTS

-12 Dino Height
-11 Dino Width
-10 Dino Height off ground
-9 Dino Jump positive or negative velocity

-8 Distance from Dino to nearest Cactus
-6 Cactus Height
-5 Cactus Width

-7 Distance from Dino to nearerst Bird
-4 Bird Height
-3 Bird Width
-2 Bird y Position

-1 Game Speed


REWARD

Game points


OUTPUTS

0 Jump
1 Duck

'''

# {
#     -12: 'Dino Height',
#     -11: 'Dino Width',
#     -10: 'Height off ground',
#     -9: 'Jump direction',
#     -8: 'Distance to Cactus',
#     -7: 'Distance to Bird',
#     -6: 'Cactus Height',
#     -5: 'Cactus Width',
#     -4: 'Bird Height',
#     -3: 'Bird Width',
#     -2: 'Bird y-Position',
#     -1: 'Game Speed',

#     0: 'Jump',
#     1: 'Duck',
# }
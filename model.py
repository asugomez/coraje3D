from OpenGL.GL import GL_STATIC_DRAW, GL_TRUE, GL_REPEAT, GL_NEAREST, GL_CLAMP_TO_EDGE
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es

from numpy import arange
from typing import List
from random import random, choice

from utils import create_gpu, modify_texture_flappy
from grafica.images_path import getImagesPath

##sound
#from playsound import playsound

# import required module
# from pydub import AudioSegment
# from pydub.playback import play


class FlappyBird(object):
    
    def __init__(self, pipeline):
        # shape_flappy = bs.createTextureQuadAdvance(0.18,0.85,0.15,0.9)
        # gpu_flappy = create_gpu(shape_flappy, pipeline)

        self.pos_x = -0.7 # initial position, constant
        self.pos_y = 0.5 # initial position
        self.alive = True
        self.moving = 1 # 0 down, 1 up
        self.size_bird = 0.15
        self.tubes = []
        self.win = False
        #self.gpu_flappy = gpu_flappy
        self.pipeline = pipeline
        self.model = modify_texture_flappy(self.pipeline, self.moving, self.size_bird) # todo: why not body_flappy

    @property 
    def points(self):
        # the number of tubes the flappy bird passes throw it
        return len(self.tubes)  
    
    def set_model(self, new_model):
        self.model = new_model
    
    def draw(self, pipeline):
        rotation = tr.identity()
        # dead
        if not self.alive:
            rotation = tr.matmul([
                tr.scale(-1, -1, 0)])# inverse
        # alive
        else:
            alpha = 3.14*1/9
            # moving up
            if(self.moving == 1): # todo detect when moving up (or create another function that is called from move_up)
                rotation = tr.rotationZ(alpha) 
            # moving down
            else:
                rotation = tr.rotationZ(-alpha)
        # change texture: image flappy
        new_model = modify_texture_flappy(self.pipeline, self.moving, self.size_bird)
        self.set_model(new_model)
        #self.model = modify_texture_flappy(self.gpu_flappy, self.moving, self.size_bird)
        # translate and rotate
        self.model.transform = tr.matmul([
            tr.translate(self.pos_x, self.pos_y, 0),
            rotation
        ])
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def move_up(self):
        #print("move up")
        if self.alive:
            if(self.pos_y < (1 - self.size_bird/2)): 
                dt = 0.35 #* 2
                self.pos_y += pow(dt,2)
            self.moving = 1
            
    def move_down(self, dt = 0.02):
        #print("move down")
        if self.alive:
            if(self.pos_y > (-1 + self.size_bird/2)): 
                #dt *= 4
                self.pos_y -= dt * 0.5 # lineal  #pow(dt,2)
            self.moving = 0

    def update(self, deltaTime):
        if self.alive:
            self.move_down(deltaTime)
    
    def game_lost(self, tube_creator):
        """
        update the bird tube list to indicate how many tubes the bird has passed throw
        """
        # bird axis positions
        bird_x_left = self.pos_x - self.size_bird/2 
        bird_x_right = self.pos_x + self.size_bird/2
        bird_y_inf = self.pos_y - self.size_bird/2 
        bird_y_sup = self.pos_y + self.size_bird/2 

        alpha_error = 0.01

        if not tube_creator.on:
            return
        
        if self.win:
            return

        if not ((bird_y_sup < 1) and (bird_y_inf > -1)):
            #print("ERROR")
            self.alive = False
            self.pos_y = -1 + self.size_bird/2 # todo fix this --> que sea mas lento
            tube_creator.die()
            return
        
        tubes = tube_creator.tubes
        for i, tube in enumerate(tubes):
            #print("tube: ", i)
            # tubes axis position
            tube_x_left = tube.pos_x - tube.width/2
            tube_x_right = tube.pos_x + tube.width/2
            tube_y_inf = -1 + tube.height_inf # punto alto del tubo inf
            tube_y_sup = 1 - tube.height_sup # punto bajo del tubo sup

            ##### BAD ######
            # checking height: bird same height as the tube
            if((bird_y_inf < (tube_y_inf + alpha_error)) or ((bird_y_sup > (tube_y_sup - alpha_error)))):
                # bird collide passing throw the tube
                if((bird_x_left > tube_x_left) and (bird_x_left < tube_x_right)):
                    #print("here 1")
                    self.alive = False
                    self.pos_y = -1 + self.size_bird/2 # todo fix this --> que sea mas lento
                    tube_creator.die()
            
                # bird collide at the begining of the tube
                elif((bird_x_right > tube_x_left) and (bird_x_right < tube_x_right)):
                    #print("here 2")
                    self.alive = False
                    self.pos_y = -1 + self.size_bird/2 # todo fix this --> que sea mas lento
                    tube_creator.die()
                    
            ##### GOOD ######
            # different height bird and tube
            else:
                # bird passing throw the tube (at the end)
                if((bird_x_left > tube_x_left + tube.width/2) and (bird_x_left < tube_x_right)):
                    if not tube in self.tubes:
                        self.tubes.append(tube)
                        #playsound('success.mp3')
              

    def clear(self):
        self.model.clear()
    

class Tube(object):

    def __init__(self, pipeline):
        self.pos_x = 1.25
        self.width = 0.25
        # create tube with a random dy
        self.height_inf = choice(arange(0.4, 1.2, 0.1))  # todo make it random
        min_dy = 0.2
        max_dy = 2 - self.height_inf - 0.4
        self.height_sup= choice(arange(min_dy, max_dy, 0.1))

        # tube model
        shape_tube_inf = bs.createTextureQuadAdvance(0.41,0.59,0,1)
        shape_tube_sup = bs.createTextureQuadAdvance(0.41,0.59,0,1)

        gpu_tube_inf = create_gpu(shape_tube_inf, pipeline)
        gpu_tube_sup = create_gpu(shape_tube_sup, pipeline)

        gpu_tube_inf.texture = es.textureSimpleSetup(getImagesPath("tube.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        gpu_tube_sup.texture = es.textureSimpleSetup(getImagesPath("tube.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        tube_inf = sg.SceneGraphNode('tube_inf')
        pos_y = -1 + self.height_inf/2 
        tube_inf.transform = tr.matmul([
            tr.translate(0, pos_y, 0),
            tr.scale(self.width, self.height_inf, 0)
        ])
        tube_inf.childs += [gpu_tube_inf]

        tube_sup = sg.SceneGraphNode('tube_sup')
        pos_y = 1 - self.height_sup/2
        tube_sup.transform = tr.matmul([
            tr.translate(0, pos_y, 0),
            tr.rotationZ(3.14), # rotation 180
            tr.scale(self.width, self.height_sup, 0)
        ])
        tube_sup.childs += [gpu_tube_sup]

        tube = sg.SceneGraphNode("tube")
        tube.childs = [tube_inf, tube_sup]

        self.model = tube

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, 0)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def update(self, dt):
        self.pos_x -= dt * 0.5

    def clear(self):
        self.model.clear()

class TubeCreator(object):
    tubes: List['Tube']

    def __init__(self, n_tubes: 'Int'):
        self.tubes = []
        self.n_tubes = n_tubes
        self.on = True # create tubes

    def die(self): 
        # todo print game lost
        self.on = False  # stop creating tubes

    def create_tube(self, pipeline):
        if len(self.tubes) >= self.n_tubes or not self.on: 
            return
        self.tubes.append(Tube(pipeline)) # todo add a distance between tubes

    def draw(self, pipeline):
        for tube in self.tubes:
            tube.draw(pipeline)
    
    def update(self, dt):
        for tube in self.tubes:
            tube.update(dt)

    def clear(self):
        for tube in self.tubes:
            tube.model.clear()

class Background(object):
    
    def __init__(self, pipeline):
        alpha_trans = 100000
        shape_bg = bs.createTextureQuad(alpha_trans, 1)
        gpu_bg = create_gpu(shape_bg, pipeline)
        gpu_bg.texture = es.textureSimpleSetup(getImagesPath("background.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        background = sg.SceneGraphNode('background')
        background.transform = tr.scale(alpha_trans,2, 0)
        background.childs = [gpu_bg]
        
        bg_final = sg.SceneGraphNode('bg_final')
        bg_final.childs += [background]

        self.pos_x = 0
        self.model = bg_final


    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, 0)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def update(self, dt):
        self.pos_x -= dt * 0.5


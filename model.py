#from OpenGL.GL import GL_STATIC_DRAW, GL_TRUE, GL_REPEAT, GL_NEAREST, GL_CLAMP_TO_EDGE
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import grafica.off_obj_reader as obj
from OpenGL.GL import *

import numpy as np
from typing import List
from random import random, choice

from utils import create_gpu, modify_texture_flappy
from grafica.images_path import getImagesPath

LARGO = 1000
MIN_Z = -0.4
MAX_Z = 0.48

##sound
#from playsound import playsound

# import required module
# from pydub import AudioSegment
# from pydub.playback import play


class FlappyBird(object):
    
    def __init__(self, pipeline):
        self.pos_x = 0.3 # initial position, constant
        self.pos_y = 0.1 # initial position, constant
        self.pos_z = 0.2 # changes with gravity and user input
        self.alive = True
        self.moving = 1 # 0 down, 1 up
        self.size_bird = 0.0003
        self.tubes = []
        self.win = False
        self.gpu = obj.createOBJShape(pipeline, getImagesPath('eiffel.obj'), 1.0, 1.0, 0.0)
        model = sg.SceneGraphNode('flappy')
        model.childs += [self.gpu]
        self.model = model

    @property 
    def points(self):
        # the number of tubes the flappy bird passes throw it
        return len(self.tubes)  
    
    def set_model(self, new_model):
        self.model = new_model
    
    def draw(self, pipeline):
        # dead
        if not self.alive:
            flappy_transform = tr.matmul([
                    tr.translate(self.pos_x, self.pos_y, self.pos_z), 
                    tr.rotationX(np.pi/4), # TODO change rotation
                    tr.uniformScale(self.size_bird)
                ])
        if self.alive:
            flappy_transform = tr.matmul([
                    tr.translate(self.pos_x, self.pos_y, self.pos_z), 
                    tr.rotationX(np.pi/2),
                    tr.uniformScale(0.00003)
                ])
        self.model.transform = flappy_transform
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, "model")
        #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, flappy_transform)
        #pipeline.drawCall(self.gpu)

    def move_up(self):
        if self.alive:
            if(self.pos_z < (1 - self.size_bird/2)): 
                dt = 0.35 #* 2
                self.pos_z += pow(dt,2)
            self.moving = 1
            
    def move_down(self, dt = 0.02):
        if self.alive:
            if(self.pos_z > (-0.5 + self.size_bird/2)): 
                #dt *= 4
                self.pos_z -= dt * 0.5  # lineal  #pow(dt,2)
            self.moving = 0

    def update(self, deltaTime):
        if self.alive:
            self.move_down(deltaTime)
    
    def game_lost(self, tube_creator):
        """
        update the bird tube list to indicate how many tubes the bird has passed throw
        """
        # bird axis positions
        bird_x_near = self.pos_x - self.size_bird/2 
        bird_x_far = self.pos_x + self.size_bird/2
        bird_y_left = self.pos_y - self.size_bird/2 
        bird_y_right = self.pos_y + self.size_bird/2 
        bird_z_inf = self.pos_z - self.size_bird/2
        bird_z_sup = self.pos_z +self.size_bird/2

        alpha_error = 0.01

        if not tube_creator.on:
            return
        
        if self.win:
            return

        # si el pájaro toca techo o suelo
        if not ((bird_z_sup < 0.5) and (bird_z_inf > -0.5)):
            #print("ERROR")
            self.alive = False
            self.pos_z = -0.5 + self.size_bird/2 # todo fix this --> que sea mas lento
            tube_creator.die()
            return
        
        tubes = tube_creator.tubes
        for i, tube in enumerate(tubes):
            # tubes axis position
            tube_x_near = tube.pos_x - tube.width/2
            tube_x_far = tube.pos_x + tube.width/2
            tube_z_inf = -0.5 + tube.height_inf # punto alto del tubo inf
            tube_z_sup = 0.5 - tube.height_sup # punto bajo del tubo sup

            ##### BAD ######
            # checking height: bird same height as the tube
            if((bird_z_inf < (tube_z_inf + alpha_error)) or ((bird_z_sup > (tube_z_sup - alpha_error)))):
                # bird collide passing throw the tube
                if((bird_x_near > tube_x_near) and (bird_x_near < tube_x_far)):
                    #print("here 1")
                    self.alive = False
                    self.pos_y = -1 + self.size_bird/2 # todo fix this --> que sea mas lento
                    tube_creator.die()
            
                # bird collide at the begining of the tube
                elif((bird_x_far > tube_x_near) and (bird_x_far < tube_x_far)):
                    #print("here 2")
                    self.alive = False
                    self.pos_z = -1 + self.size_bird/2 # todo fix this --> que sea mas lento
                    tube_creator.die()
                    
            ##### GOOD ######
            # different height bird and tube
            else:
                # bird passing throw the tube (at the end)
                if((bird_x_near > tube_x_near + tube.width/2) and (bird_x_near < tube_x_near)):
                    if not tube in self.tubes:
                        self.tubes.append(tube)
                        #playsound('success.mp3')
              
    def clear(self):
        self.model.clear()
    
class Tube(object):

    def __init__(self, pipeline):
        self.pos_x = 15
        self.width = 0.4
        # create tube with a random dz
        self.height_inf = choice(np.arange(0.3, 0.6, 0.1)) # altura tubo inferior
        min_distance_between_tubes = 0.3 # distancia entre tubos
        max_dz = 1 - self.height_inf - min_distance_between_tubes
        self.height_sup= choice(np.arange(0.1, max_dz, 0.1)) # altura tubo sup

        # tube model
        shape_tube_inf = bs.createColorNormalsCube(0,1,0) # todo make it cilindrique
        shape_tube_sup = bs.createColorNormalsCube(0,1,0) # todo make it cilindrique

        gpu_tube_inf = create_gpu(shape_tube_inf, pipeline)
        gpu_tube_sup = create_gpu(shape_tube_sup, pipeline)

        tube_inf = sg.SceneGraphNode('tube_inf')
        pos_z_inf = -0.5 + self.height_inf/2 
        tube_inf.transform = tr.matmul([
            tr.translate(0, 0, pos_z_inf),
            tr.scale(self.width, self.width, self.height_inf)
        ])
        tube_inf.childs += [gpu_tube_inf]

        tube_sup = sg.SceneGraphNode('tube_sup')
        pos_z_sup = 0.5- self.height_sup/2
        tube_sup.transform = tr.matmul([
            tr.translate(0, 0, pos_z_sup),
            tr.rotationZ(3.14), # rotation 180
            tr.scale(self.width, self.width, self.height_sup)
        ])
        tube_sup.childs += [gpu_tube_sup]

        tube = sg.SceneGraphNode("tube")
        tube.childs += [tube_inf]
        tube.childs += [tube_sup] 
        #self.gpu = gpu_tube_inf

        self.model = tube

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "model")
        #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        #pipeline.drawCall(self.gpu)
        

    def update(self, dt):
        self.pos_x -= dt * 7

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
    
    def __init__(self, pipeline, L = 10):
        self.night = L
        side = create_skybox(pipeline)
        floor = create_floor(pipeline)
        sky = create_sky(pipeline)

        background = sg.SceneGraphNode('background')
        background.childs += [side]
        background.childs += [floor]
        background.childs += [sky]

        self.pos_x = 0
        self.model = background


    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, 0)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, "model")

    def update(self, dt):
        self.pos_x -= dt * 0.5



def create_skybox(pipeline):
    # código del aux 6
    shapeSky = bs.createTextureNormalsCubeAdvanced('background.jfif', LARGO, 1)
    gpuSky = create_gpu(shapeSky, pipeline)
    gpuSky.texture = es.textureSimpleSetup(
        getImagesPath("background.jfif"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    
    skybox = sg.SceneGraphNode("skybox")
    skybox.transform = tr.matmul([tr.translate(0, 0, 0), tr.scale(LARGO,1,1)])
    skybox.childs += [gpuSky]

    return skybox

def create_floor(pipeline):
    # código del aux 6
    shapeFloor = bs.createTextureQuadWithNormal(LARGO, 1)
    gpuFloor = create_gpu(shapeFloor, pipeline)
    gpuFloor.texture = es.textureSimpleSetup(
        getImagesPath("grass.jfif"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    floor = sg.SceneGraphNode("floor")
    floor.transform = tr.matmul([tr.translate(0, 0, MIN_Z),tr.scale(LARGO, 1, 1)])
    floor.childs += [gpuFloor]

    return floor

def create_sky(pipeline):
    # código del aux 6
    shapeFloor = bs.createTextureQuadWithNormal(LARGO, 1)
    gpuFloor = create_gpu(shapeFloor, pipeline)
    gpuFloor.texture = es.textureSimpleSetup(
        getImagesPath("grass.jfif"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    floor = sg.SceneGraphNode("floor")
    floor.transform = tr.matmul([tr.translate(0, 0, MAX_Z),tr.scale(LARGO, 1, 1)])
    floor.childs += [gpuFloor]

    return floor

def create_sky2(pipeline,r=0,g=0,b=0):
    shapeSky = bs.createColorQuad(0.133, 0.194, 0.205)
    gpuSky = create_gpu(shapeSky, pipeline)
    sky = sg.SceneGraphNode("sky")
    sky.transform = tr.matmul([tr.translate(0, 0, 0.1),tr.uniformScale(20)])
    sky.childs += [gpuSky]

    return sky


import glfw
import numpy as np
from typing import Optional
import grafica.transformations as tr

class Controller():
    flappy_bird: Optional['FlappyBird'] 
    tubes: Optional['TubeCreator']
    tube: Optional['Tube']


    def __init__(self, width = 1000, height = 600): # referencia a objetos
        self.width = width
        self.height = height
        self.flappy_bird = None
        self.tubes = None
        self.last_release = 0
        # perspective vectors
        self.camera_theta = np.pi
        self.eye = np.array([0, 0, 0.1])  # Básicamente la posición del jugador
        self.at = np.array([0, 1, 0.1])   # Hacia dónde ve el jugador
        self.up = np.array([0, 0, 1])     # Un vector hacia arriba

        self.projection = tr.perspective(60, float(width)/float(height), 0.1, 100)

    def set_flappy_bird(self, flappy_bird: 'FlappyBird'):
        self.flappy_bird = flappy_bird

    def set_tube_creator(self, tubes: 'TubeCreator'):
        self.tubes = tubes
       
    def on_key(self, window, key, scancode, action, mods):
        #print(key, action)
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return
        ### close window
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        ### moves
        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.PRESS:
            #print("move up")
            if self.flappy_bird.alive: self.flappy_bird.move_up()

        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.RELEASE:
            #print("move down")
            if self.flappy_bird.alive: self.flappy_bird.move_down()

        elif key == glfw.KEY_DOWN and action == glfw.RELEASE:
            #print("key down")
            if self.flappy_bird.alive: self.flappy_bird.move_down()

        ### perspective

        # camera behind our character, which is pointing forward.
        elif key == glfw.KEY_1 and action == glfw.PRESS:
            # set up the controller.eye and et
            self.eye = (self.at - self.eye) * 0.05
            self.at += (self.at - self.eye) * 0.05
            self.camera_theta = np.pi
            self.projection = tr.perspective(10, float(width)/float(height), 0.1, 100)

        # side camera (view from the side, like 2D)
        elif key == glfw.KEY_2 and action == glfw.PRESS:
            # set up the controller.eye and et
            self.eye = (self.at - self.eye) * 0.05
            self.at += (self.at - self.eye) * 0.05
            self.camera_theta = np.pi/4
            self.projection = tr.perspective(40, float(width)/float(height), 0.1, 100)

        # first-person camera, what flappy bird sees
        elif key == glfw.KEY_3 and action == glfw.PRESS:
            # set up the controller.eye and et
            self.eye = (self.at - self.eye) * 0.05
            self.at += (self.at - self.eye) * 0.05
            self.camera_theta = np.pi/8
            self.projection = tr.perspective(80, float(width)/float(height), 0.1, 100)

        else:
            print('Unknown key')

    def clear_gpu(self):
        self.flappy_bird.clear
        self.tubes.clear

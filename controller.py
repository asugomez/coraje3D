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
        self.eye = np.array([-0.5, 0, 0.3])  # Básicamente la posición del jugador
        self.up = np.array([0, 0, 1])     # Un vector hacia arriba
        self.at = np.array([1, 0, 0])   # Hacia dónde ve el jugador
        self.projection = tr.perspective(45, float(self.width)/float(self.height), 0.1, 100)

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
            self.eye = np.array([-0.5, 0, 0.3])
            self.up = np.array([0, 0, 1])
            self.at = np.array([1, 0, 0])
            self.projection = tr.perspective(45, float(self.width)/float(self.height), 0.1, 100)

        # side camera (view from the side, like 2D)
        elif key == glfw.KEY_2 and action == glfw.PRESS:
            # set up the controller.eye and et
            self.eye = np.array([0, 0.5, 0.3])
            self.up = np.array([0, 0, 1])
            self.at = np.array([0, -1, 0])
            self.projection = tr.perspective(45, float(self.width)/float(self.height), 0.1, 100)

        # first-person camera, what flappy bird sees
        elif key == glfw.KEY_3 and action == glfw.PRESS:
            # set up the controller.eye and et
            self.eye = np.array([-0.3, 0, 0.3]) #[self.flappy_bird.pos_x, self.flappy_bird.pos_y, self.flappy_bird.pos_z])
            self.up = np.array([0, 0, 1])
            self.at = np.array([1, 0, 0.3]) # +- 0.3 mover hacia arriba
            self.projection = tr.perspective(45, float(self.width)/float(self.height), 0.1, 100)

        else:
            print('Unknown key')

    def clear_gpu(self):
        self.flappy_bird.clear
        self.tubes.clear

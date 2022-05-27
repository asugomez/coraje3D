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
        # perspective vectors
        self.camera_theta = 1
        self.eye = np.array([-0.4, 0, 0])  # Básicamente la posición del jugador
        self.up = np.array([0, 0, 1])     # Un vector hacia arriba
        self.at = np.array([1, 0, 0])   # Hacia dónde ve el jugador
        self.projection = tr.perspective(45, float(self.width)/float(self.height), 0.1, 100)
        self.pos_camera = "THIRD_CAMERA"


    def set_flappy_bird(self, flappy_bird: 'FlappyBird'):
        self.flappy_bird = flappy_bird

    def set_tube_creator(self, tubes: 'TubeCreator'):
        self.tubes = tubes
       
    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return
        ### close window
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        ### moves
        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.PRESS:
            if self.flappy_bird.alive: self.flappy_bird.move_up()
            if self.camera_theta <= 0.8: self.camera_theta += 0.3

        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.RELEASE:
            if self.flappy_bird.alive: self.flappy_bird.move_down()
            if self.camera_theta >= -0.9: self.camera_theta -= 0.02

        elif key == glfw.KEY_DOWN and action == glfw.RELEASE:
            if self.flappy_bird.alive: self.flappy_bird.move_down()

        ###########################################################################
        ### perspective
        # camera behind our character, which is pointing forward.
        elif key == glfw.KEY_1 and action == glfw.PRESS:
            self.pos_camera = "THIRD_CAMERA"
            self.set_up_vectors()
            self.projection = tr.perspective(45, float(self.width)/float(self.height), 0.1, 100)

        # side camera (view from the side, like 2D)
        elif key == glfw.KEY_2 and action == glfw.PRESS:
            self.pos_camera = "SIDE_CAMERA"
            self.set_up_vectors()
            self.projection = tr.perspective(80, float(self.width)/float(self.height), 0.1, 100)

        # first-person camera, what flappy bird sees
        elif key == glfw.KEY_3 and action == glfw.PRESS:
            self.pos_camera = "FIRST_CAMERA"
            self.set_up_vectors()
            self.projection = tr.perspective(100, float(self.width)/float(self.height), 0.1, 100)
       
        # diagonal camera
        elif key == glfw.KEY_4 and action == glfw.PRESS:
            self.eye = np.array([-0.4, -0.3, 0])
            self.up = np.array([0, 0, 1])
            self.at = np.array([1, 1, 0])
            self.projection = tr.perspective(80, float(self.width)/float(self.height), 0.1, 100)

        else:
            print('Unknown key')


    def set_up_vectors(self): 
        #self.modify_eye_x() # set up the eye with the bird position on axis x
        self.eye = np.array([self.flappy_bird.pos_x, self.eye[1], self.eye[2]])
        if self.pos_camera == "THIRD_CAMERA":
            eye_x = self.eye[0] - 0.5 # behind
            self.eye = np.array([eye_x, 0, 0.1])
            self.up = np.array([0, 0, 1])
            self.at = np.array([self.flappy_bird.pos_x, 0, 0.1])

        if self.pos_camera == "SIDE_CAMERA":
            eye_x = self.eye[0] + 0.3# from the side
            self.eye = np.array([eye_x, -0.5, 0])
            self.up = np.array([0, 0, 1])
            self.at = np.array([eye_x, 1, 0])

        if self.pos_camera == "FIRST_CAMERA":
            eye_x = self.eye[0]
            self.eye = np.array([self.flappy_bird.pos_x, self.flappy_bird.pos_y, self.flappy_bird.pos_z])
            self.at = np.array([self.flappy_bird.pos_x + 1, 0, self.flappy_bird.pos_z + self.camera_theta])
            self.up = np.array([0, 0, 1])

    def clear_gpu(self):
        self.flappy_bird.clear
        self.tubes.clear

import glfw
import numpy as np
from typing import Optional
import grafica.transformations as tr

class Controller():
    coraje: Optional['Coraje'] 
    tubes: Optional['TubeCreator']
    tube: Optional['Tube']


    def __init__(self, width = 1000, height = 600): # referencia a objetos
        self.mousePos = (0.0, 0.0) # from -1 to 1
        self.width = width
        self.height = height
        self.coraje = None
        self.tubes = None
        # perspective vectors
        self.camera_theta = 1
        self.eye = np.array([-0.4, 0, 0])  # Básicamente la posición del jugador
        self.up = np.array([0, 0, 1])     # Un vector hacia arriba
        self.at = np.array([1, 0, 0])   # Hacia dónde ve el jugador
        self.projection = tr.perspective(45, float(self.width)/float(self.height), 0.1, 100)
        self.pos_camera = "THIRD_CAMERA"
    
    @property
    def mouseX(self):
        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (self.mousePos[0] - self.width/2) / self.width
        return mousePosX
    
    @property
    def mouseY(self):
        # Getting the mouse location in opengl coordinates
        mousePosY = 2 * (self.height/2 - self.mousePos[1]) / self.height
        return mousePosY

    def set_coraje(self, coraje: 'Coraje'):
        self.coraje = coraje

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
            if self.coraje.alive: self.coraje.move_up()
            if self.camera_theta <= 0.8: self.camera_theta += 0.3

        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.RELEASE:
            if self.coraje.alive: self.coraje.move_down()
            if self.camera_theta >= -0.9: self.camera_theta -= 0.02

        elif key == glfw.KEY_DOWN and action == glfw.RELEASE:
            if self.coraje.alive: self.coraje.move_down()

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

        ###########################################################################
        ## BONUS
        ## camera at with mouse
        # third person
        elif key == glfw.KEY_5 and action == glfw.PRESS:
            self.pos_camera = "THIRD_CAMERA_2"
            self.set_up_vectors()
            self.projection = tr.perspective(45, float(self.width)/float(self.height), 0.1, 100)

        # first-person camera, what flappy bird sees
        elif key == glfw.KEY_6 and action == glfw.PRESS:
            self.pos_camera = "FIRST_CAMERA_2"
            self.set_up_vectors()
            self.projection = tr.perspective(100, float(self.width)/float(self.height), 0.1, 100)

        else:
            print('Unknown key')

    def set_up_vectors(self): 
        # set up the eye with the bird position on axis x
        eye_x = self.coraje.pos_x
        if self.pos_camera == "THIRD_CAMERA":
            eye_x -=  0.5 # behind
            self.eye = np.array([eye_x, 0, 0.1])
            self.up = np.array([0, 0, 1])
            self.at = np.array([self.coraje.pos_x, 0, 0.1])

        if self.pos_camera == "SIDE_CAMERA":
            eye_x += 0.3# from the side
            self.eye = np.array([eye_x, -0.5, 0])
            self.up = np.array([0, 0, 1])
            self.at = np.array([eye_x, 1, 0])

        if self.pos_camera == "FIRST_CAMERA":
            self.eye = np.array([eye_x,  self.coraje.pos_y, self.coraje.pos_z])
            self.up = np.array([0, 0, 1])
            self.at = np.array([self.coraje.pos_x + 1, 0, self.coraje.pos_z + self.camera_theta])

        ###########################################################################
        ## BONUS
        if self.pos_camera == "THIRD_CAMERA_2":
            eye_x -=  0.5 # behind
            self.eye = np.array([eye_x, 0, 0.1])
            self.up = np.array([0, 0, 1])
            self.at = np.array([self.coraje.pos_x, self.mouseX, self.mouseY])

        if self.pos_camera == "FIRST_CAMERA_2":
            self.eye = np.array([eye_x,  self.coraje.pos_y, self.coraje.pos_z])
            self.up = np.array([0, 0, 1])
            self.at = np.array([self.coraje.pos_x + 1, self.mouseX, self.mouseY])

    def clear_gpu(self):
        self.coraje.clear
        self.tubes.clear

    def cursor_pos_callback(self, window, x, y):
        #print("call back cursor")
        self.mousePos = (x,y)
    
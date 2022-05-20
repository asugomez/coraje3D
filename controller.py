import glfw
from typing import Optional

class Controller():
    flappy_bird: Optional['FlappyBird'] 
    tubes: Optional['TubeCreator']
    tube: Optional['Tube']


    def __init__(self): # referencia a objetos
        self.flappy_bird = None
        self.tubes = None
        self.last_release = 0

    def set_flappy_bird(self, flappy_bird: 'FlappyBird'):
        self.flappy_bird = flappy_bird

    def set_tube_creator(self, tubes: 'TubeCreator'):
        self.tubes = tubes
         
    def on_key(self, window, key, scancode, action, mods):

        #print(key, action)
        # 0 release
        # 1 press
        
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return

        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.PRESS:
            #print("move up")
            if self.flappy_bird.alive: self.flappy_bird.move_up()

        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.RELEASE:
            #print("move down")
            if self.flappy_bird.alive: self.flappy_bird.move_down()

        elif key == glfw.KEY_DOWN and action == glfw.RELEASE:
            #print("key down")
            if self.flappy_bird.alive: self.flappy_bird.move_down()

        else:
            print('Unknown key')

    def clear_gpu(self):
        self.flappy_bird.clear
        self.tubes.clear

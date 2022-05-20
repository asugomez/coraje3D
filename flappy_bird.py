
import glfw # GLFW just sets up the window and context
import sys
from OpenGL.GL import * #glUseProgram, glClearColor, glEnable, glBlendFunc, glClear, GL_BLEND, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA 
from random import randint

import grafica.easy_shaders as es
import grafica.text_renderer as tx

from model import *
from controller import Controller
from utils import draw_image, draw_points_2, draw_points

""" 
TODO:
- añadir sonido 
- añadir inclinasion∂
- readme
"""
if __name__ == '__main__':
    # no args given
    if(len(sys.argv) == 1):
        print("hello")
        n_tubes = randint(3,10)
    else:
        n_tubes = int(sys.argv[1])
    
    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1000
    height = 600

    window = glfw.create_window(width, height, 'Catty Bird', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    # set the controller
    controller = Controller()
    # set the current window
    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

    # A shader program that implements transformations
    pipeline = es.SimpleTextureTransformShaderProgram()
    # A shader programs for text
    textPipeline = tx.TextureTextRendererShaderProgram()

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0) # TODO: buscar por qué

    ### TEXT
    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)

    # create objects
    flappy_bird = FlappyBird(pipeline)
    tubeCreator = TubeCreator(n_tubes) # le doy el pipelin al momento de añadir un "tube" (create_tube(pipeline))
    background = Background(pipeline) # create object to apply the transformation

    controller.set_flappy_bird(flappy_bird)
    controller.set_tube_creator(tubeCreator)

    t0 = 0
    c0 = 0

    # Application loop
    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # todo check this with the background

        # Using the time as the x_0 parameter
        if flappy_bird.alive:
            ti = glfw.get_time()
            ci = ti # distance
            dc = ci - c0 # dx distance
            dt = ti - t0
            t0 = ti
        else: 
            dt = 0 # stop the game

        # create tubes with a distance between them
        if(dc > 2):
            #print("create tube c1: ", ci)
            tubeCreator.create_tube(pipeline)
            c0 = ci
        
        # update position
        tubeCreator.update(dt)
        flappy_bird.update(dt)
        background.update(dt)

        # check if flappy collide with a tube
        flappy_bird.game_lost(tubeCreator)

        # Telling OpenGL to use our shader program
        glUseProgram(pipeline.shaderProgram)

        # draw the models and background
        if flappy_bird.alive:
            # Setting up the background
            #draw_image(pipeline,2,2,"background") 
            background.draw(pipeline)
            #### Draw the points with image texture
            # draw the points
            # if(flappy_bird.points < 10):
            #     draw_points(pipeline, flappy_bird.points)
            # else:
            #     draw_points_2(pipeline, flappy_bird.points)
            if(flappy_bird.points == n_tubes): # todo fix this
                #print("WIN!!!!!")
                flappy_bird.win = True
                draw_image(pipeline,1,1,"win")
        else:
            glClearColor(1, 0, 0, 1.0)
            draw_image(pipeline,1,1,"lose")

        tubeCreator.draw(pipeline)
        flappy_bird.draw(pipeline)

        ### TEXT
        # Telling OpenGL to use our shader program
        glUseProgram(textPipeline.shaderProgram)
        headerText = str(flappy_bird.points) # points
        headerCharSize = 0.1
        headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
        gpuHeader = es.GPUShape().initBuffers() #gpu
        textPipeline.setupVAO(gpuHeader) #vao
        gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_STATIC_DRAW)
        gpuHeader.texture = gpuText3DTexture
        headerTransform = tr.matmul([
            tr.translate(-0.05, 0.5, 0),
        ])


        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 0.3,0.1,0.4,1) # purple
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0,0,0,0) # sin fondo
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, headerTransform)
        textPipeline.drawCall(gpuHeader)
        
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuHeader.clear()
    controller.clear_gpu()
    glfw.terminate()

    
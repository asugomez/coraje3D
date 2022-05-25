
"""
If it is required to draw 3D over 2D, you may need to clear the depth buffer with
glClear(GL_DEPTH_BUFFER_BIT)
"""
import glfw # GLFW just sets up the window and context
import sys
from OpenGL.GL import * #glUseProgram, glClearColor, glEnable, glBlendFunc, glClear, GL_BLEND, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA 
from random import randint

import grafica.easy_shaders as es
import grafica.text_renderer as tx
import grafica.lighting_shaders as ls

import numpy as np

from model import *
from controller import Controller
from utils import draw_image

""" 
TODO:
fun for view, projection, model
"""

if __name__ == '__main__':
    # no args given
    if(len(sys.argv) == 1):
        # give a random number between 3 and 10
        n_tubes = 10#randint(3,10)
    else:
        # user give an input
        n_tubes = int(sys.argv[1])
    
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # set the controller
    controller = Controller(width = 1000, height = 600)

    window = glfw.create_window(controller.width, controller.height, 'Catty Bird 3D', None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    # set the current window
    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

    # A shader program that implements transformations
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    simpleShaderProgram = es.SimpleModelViewProjectionShaderProgram()
    # Shader program for lights
    textureLightShaderProgram = ls.SimpleTexturePhongShaderProgram()  
    lightShaderProgram = ls.SimpleGouraudShaderProgram()
    simpleShader = es.SimpleTransformShaderProgram()
    # A shader programs for text
    #textPipeline = tx.TextureTextRendererShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.133, 0.194, 0.205, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    background_final = Background(textureShaderProgram)
    # create objects
    flappy_bird = FlappyBird(lightShaderProgram)
    tubeCreator = TubeCreator(n_tubes) # le doy el pipeline al momento de añadir un "tube" (create_tube(pipeline))
    #shape_tube_inf = bs.createColorNormalsCube(0,1,0)
    #gpu_tube_inf = create_gpu(shape_tube_inf, lightShaderProgram)

    controller.set_flappy_bird(flappy_bird)
    controller.set_tube_creator(tubeCreator)

    ### TEXT
    # # Creating texture with all characters
    # textBitsTexture = tx.generateTextBitsTexture()
    # # Moving texture to GPU memory
    # gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)
    
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0) # TODO: buscar por qué

    t0 = glfw.get_time()
    c0 = 0
    t1 = glfw.get_time()

    c_pos_sol_y = 20
    pos_sol_y = c_pos_sol_y
    c_pos_sol_z = 10
    sol_theta = 3/2 * np.pi 

    # Application loop
    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        """
        # Setting up the view transform
        # for bonus point with mouse

        camX = 10 * np.sin(camera_theta)
        camY = 10 * np.cos(camera_theta)

        viewPos = np.array([camX, camY, 10])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )
        """

        # Using the time as the x_0 parameter
        if True: #flappy_bird.alive:
            t1 = glfw.get_time()
            dx = t1 - c0 # dx distance
            # Getting the time difference from the previous iteration
            dt = t1 - t0
            t0 = t1
            if pos_sol_y >= -c_pos_sol_y:
                pos_sol_y -= 2 * dt
            else:
                pos_sol_y += 2 * dt
            
            sol_theta += 2 * dt
            pos_sol_z = c_pos_sol_z * np.cos(sol_theta)

        else: 
            dt = 0 # stop the game

        # create tubes with a distance between them
        if(dx > 2):
            #print("create tube c1: ", ci)
            tubeCreator.create_tube(lightShaderProgram)
            c0 = t1
        
        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # update position
        flappy_bird.update(dt)
        tubeCreator.update(dt)
        background_final.update(dt)

        # check if flappy collide with a tube
        flappy_bird.game_lost(tubeCreator)
        if flappy_bird.alive:
            view = tr.lookAt(controller.eye, controller.at, controller.up)
            ###########################################################################
            ##### DRAW THE BACKGROUND
            # Telling OpenGL to use our shader program
            glUseProgram(textureShaderProgram.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, controller.projection)
            # background
            background_final.draw(textureShaderProgram)
            if(flappy_bird.points == n_tubes): # todo fix this
                #print("WIN!!!!!")
                flappy_bird.win = True
                ##draw_image(textureShaderProgram,1,1,"win")
        else:
            glClearColor(1, 0, 0, 1.0)
            ##draw_image(textureShaderProgram,1,1,"lose")
        
        ###########################################################################
        ##### DRAW THE MODELS
        ## Tube
        # glUseProgram(lightShaderProgram.shaderProgram)
        # glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        # glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, controller.projection)
        # tubeCreator.draw(lightShaderProgram)
        ## Flappy
        glUseProgram(lightShaderProgram.shaderProgram)
        ###########################################################################
        #### LIGHTS
        # Setting all uniform shader variables

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "lightPosition"), 0, pos_sol_y, pos_sol_z)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "viewPosition"), controller.eye[0], controller.eye[1], controller.eye[2])
        glUniform1ui(glGetUniformLocation(lightShaderProgram.shaderProgram, "shininess"), 50)

        glUniform1f(glGetUniformLocation(lightShaderProgram.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightShaderProgram.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightShaderProgram.shaderProgram, "quadraticAttenuation"), 0.01)

        # tubes
        tube_transform = tr.matmul([
            #tr.translate(0, 0, pos_z_inf),
            tr.uniformScale(0.25)
        ])
        glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, controller.projection)
        tubeCreator.draw(lightShaderProgram)

        # flappy
        glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, controller.projection)
        flappy_bird.draw(lightShaderProgram)

        ###########################################################################
        #### DRAW THE POINTS

        """ 
        to change the light
        see ex_lighting.py
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 0.6, 0.6, 0.6)
        """
        
    
        ### TEXT
        
        # Telling OpenGL to use our shader program
        # glUseProgram(textPipeline.shaderProgram)
        # headerText = str(flappy_bird.points) # points
        # headerCharSize = 0.1
        # headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
        # gpuHeader = es.GPUShape().initBuffers() #gpu
        # textPipeline.setupVAO(gpuHeader) #vao
        # gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_STATIC_DRAW)
        # gpuHeader.texture = gpuText3DTexture
        # headerTransform = tr.matmul([
        #     tr.translate(-0.05, 0.5, 0),
        # ])


        # glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 0.3,0.1,0.4,1) # purple
        # glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0,0,0,0) # sin fondo
        # glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, headerTransform)
        # textPipeline.drawCall(gpuHeader)
        
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    #gpuHeader.clear()
    controller.clear_gpu()
    glfw.terminate()

    
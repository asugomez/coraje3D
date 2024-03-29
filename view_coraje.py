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
from utils import draw_image, setUpLightsDefault

""" 
TODO:
fun for view, projection, model
"""

if __name__ == '__main__':
    # no args given
    if(len(sys.argv) == 1):
        # give a random number between 3 and 10
        n_tubes = 10#randint(3,10)
        day_night_time = 20
    else:
        # user give an input
        n_tubes = int(sys.argv[1]) # N
        day_night_time = int(sys.argv[2]) # L

    
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # set the controller
    controller = Controller(width = 1000, height = 600)

    window = glfw.create_window(controller.width, controller.height, 'Coraje corre 3D', None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    # set the current window
    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)
    # Connecting the callback function 'cursor_pos_callback' to handle mouse events
    glfw.set_cursor_pos_callback(window, controller.cursor_pos_callback)

    # Shader program for lights
    textureLightShaderProgram = ls.SimpleTexturePhongShaderProgram()
    lightShaderProgram = ls.SimplePhongShaderProgram()
    # A shader programs for text
    textPipeline = tx.TextureTextRendererShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.133, 0.194, 0.205, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    background_final = Background(textureLightShaderProgram)
    # create objects
    coraje = Coraje(lightShaderProgram)
    tubeCreator = TubeCreator(n_tubes) # le doy el pipeline al momento de añadir un "tube" (create_tube(pipeline))

    controller.set_coraje(coraje)
    controller.set_tube_creator(tubeCreator)

    ### TEXT
    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)
    
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0) # TODO: buscar por qué

    t0 = glfw.get_time()
    t1 = glfw.get_time()
    # light time
    c_pos_sol_y = 20
    c_pos_sol_z = 10
    sol_theta = 1/2 * np.pi 
    pos_sol_z = c_pos_sol_z * -1 * np.cos(sol_theta)
    pos_sol_y = c_pos_sol_y * np.sin(sol_theta)
    # Day and night duration in seconds
    L0 = glfw.get_time()
    delta_t = 0.0009 # dt app
    day_quart_time = day_night_time/4
    # d_theta que se tiene que añadir para que en L/4 (s) recorra pi/2
    delta_theta = (np.pi/2) / (day_quart_time / delta_t) 
    # Application loop
    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Using the time as the x_0 parameter
        if coraje.alive:
            t1 = glfw.get_time()
            # Getting the time difference from the previous iteration
            dt = t1 - t0
            t0 = t1
            # set up the eye, at and up for first camera
            if controller.camera_theta >= -0.9: controller.camera_theta -= dt
            controller.set_up_vectors()
            # sun light
            L0 += dt
            sol_theta += delta_theta
            pos_sol_z = c_pos_sol_z * -1 * np.cos(sol_theta)
            pos_sol_y = c_pos_sol_y * np.sin(sol_theta)

        else: 
            dt = 0 # stop the game

        # create tubes with a distance between them
        tubeCreator.create_tube(lightShaderProgram)
        
        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # update position
        coraje.update(dt)
        
        # check if coraje collide with a tube
        coraje.game_lost(tubeCreator)
        # coraje alive
        if coraje.alive:
            view = tr.lookAt(controller.eye, controller.at, controller.up)
            ###########################################################################
            ##### DRAW THE BACKGROUND
            # Telling OpenGL to use our shader program
            glUseProgram(textureLightShaderProgram.shaderProgram)
            # Setting up the light variables
            setUpLightsDefault(textureLightShaderProgram)
            # re set up the light position (like it was the sun)
            glUniform3f(glGetUniformLocation(textureLightShaderProgram.shaderProgram, "lightPosition"), coraje.pos_x + 10, pos_sol_y, pos_sol_z)
            
            #glUniform3f(glGetUniformLocation(textureLightShaderProgram.shaderProgram, "viewPosition"), controller.eye[0], controller.eye[1], controller.eye[2])
            glUniformMatrix4fv(glGetUniformLocation(textureLightShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(textureLightShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, controller.projection)
            # background
            background_final.draw(textureLightShaderProgram)
            ###########################################################################
            ##### DRAW THE MODELS
            # Telling OpenGL to use our shader program
            glUseProgram(lightShaderProgram.shaderProgram)
            # Setting up the light variables
            setUpLightsDefault(lightShaderProgram)
            # different setting for dog and tubes
            glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ka"), .2,.2,.2)
            glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Kd"), 0.7,0.3,0.7)
            glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ks"), 0.7,0.3,0.7)
            # re set up the light position (like it was the sun)
            glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "lightPosition"), coraje.pos_x + 10, pos_sol_y, pos_sol_z)

            #glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "viewPosition"), controller.eye[0], controller.eye[1], controller.eye[2])
            glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, controller.projection)
            # tubes
            tubeCreator.draw(lightShaderProgram)
            # coraje
            coraje.draw(lightShaderProgram)
            ###########################################################################
            #### DRAW THE POINTS
            # TEXT
            # Telling OpenGL to use our shader program
            glUseProgram(textPipeline.shaderProgram)
            gpuHeader = write_text(textPipeline, coraje.points, gpuText3DTexture, 0.4, 0.5, 0)
        else:
            glClearColor(0.8, 0.2, 0, 1.0)
            glUseProgram(textPipeline.shaderProgram)
            gpuHeader = write_text(textPipeline, "You lose :(", gpuText3DTexture, -0.8, 0, 0)
        


        ###########################################################################
        # coraje win
        if(coraje.points == n_tubes):
            coraje.win = True
            glUseProgram(textPipeline.shaderProgram)
            gpuHeader = write_text(textPipeline, "You win!", gpuText3DTexture,-0.8, 0, 0)
        
        
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuHeader.clear()
    controller.clear_gpu()
    glfw.terminate()

    
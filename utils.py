
from OpenGL.GL import GL_STATIC_DRAW, GL_TRUE, GL_REPEAT, GL_NEAREST, GL_LINEAR, glUniform3f, glGetUniformLocation, glUniform1ui, glUniform1f

import grafica.easy_shaders as es
import grafica.scene_graph as sg
import grafica.basic_shapes as bs
import grafica.transformations as tr
import grafica.off_obj_reader as obj

from grafica.images_path import getImagesPath


def create_gpu(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpu

def modify_texture_flappy(pipeline, moving, size_bird): # todo make it a method!
    """
    If flappy bird is:
    moving up --> 1
    moving down --> 0
    not moving --> 0
    """
    #print("call to modify_texture_flappy: ", moving)

    if(moving == 1):
        # shape in 3d
        shape_flappy = obj.readOBJ(getImagesPath('carrot.obj'), (1.0, 0.0, 0.0))
        gpu_flappy = create_gpu(shape_flappy, pipeline)
        
        #size_bird = 0.5
    else: # center or down
        shape_flappy = bs.createTextureQuadAdvance(0.15,0.85,0.15,0.9)
        gpu_flappy = create_gpu(shape_flappy, pipeline)
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_center.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        #size_bird = 0.5
   
    body_flappy = sg.SceneGraphNode('body_flappy') # todo check if we need to clear it
    body_flappy.transform = tr.uniformScale(size_bird)
    body_flappy.childs += [gpu_flappy]

    flappy = sg.SceneGraphNode('flappy')
    flappy.childs += [body_flappy]
    return flappy


def draw_image(pipeline, w, h, name_image):
    shape_bg = bs.createTextureQuad(1, 1)
    gpu_bg = create_gpu(shape_bg, pipeline)
    gpu_bg.texture = es.textureSimpleSetup(getImagesPath(name_image + ".png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    background = sg.SceneGraphNode(name_image)
    background.childs = [gpu_bg]

    background.transform = tr.scale(w, h, 0)

    sg.drawSceneGraphNode(background, pipeline, 'transform')

def setUpLightsDefault(pipeline):
    # Setting all uniform shader variables 
    # White light in all components: ambient, diffuse and specular.
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1,1,1)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1,1,1 )
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1,1,1)

    # Object is barely visible at only ambient. Bright white for diffuse and specular components.
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), .02,.02,.02)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.7,0.3,0.7)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), .2,.2,.2)
    
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), -5, -5, 5)
    glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 200)

    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.01)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.003)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

  
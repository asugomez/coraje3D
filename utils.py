
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
    La = 1,1,1
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), *La)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1,1,1 )
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1,1,1)

    # Object is barely visible at only ambient. Bright white for diffuse and specular components.
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), .1,.05,.1)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.6,0.3,0.6)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), .2,.2,.2)
    
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), -5, -5, 5)
    glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 200)

    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.01)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.003)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

  
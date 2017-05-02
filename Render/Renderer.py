import os, math
import platform as platformModule
import time as timeModule

import pygame
from pygame.locals import *
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from Utilities import Singleton, perspective, ortho, FLOAT_ZERO
from ResourceManager import ResourceManager, DefaultFontFile
from Core import CoreManager, SceneManager, COMMAND, logger
from OpenGLContext import RenderTargets, RenderTargetManager, FrameBuffer, GLFont


class Console:
    def __init__(self):
        self.infos = []
        self.debugs = []
        self.renderer = None
        self.texture = None
        self.font = None
        self.enable = True

    def initialize(self, renderer):
        self.renderer = renderer
        self.font = GLFont(DefaultFontFile, 12, margin=(10, 0))

    def close(self):
        pass

    def clear(self):
        self.infos = []

    def toggle(self):
        self.enable = not self.enable

    # just print info
    def info(self, text):
        if self.enable:
            self.infos.append(text)

    # debug text - print every frame
    def debug(self, text):
        if self.enable:
            self.debugs.append(text)

    def render(self):
        self.renderer.ortho_view()

        # set render state
        glEnable(GL_BLEND)
        glBlendEquation(GL_FUNC_ADD)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)

        if self.enable and self.infos:
            text = '\n'.join(self.infos) if len(self.infos) > 1 else self.infos[0]
            if text:
                # render
                self.font.render(text, 0, self.renderer.height - self.font.height)
            self.infos = []


class Renderer(Singleton):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.viewportRatio = 1.0
        self.perspective = np.eye(4, dtype=np.float32)
        self.ortho = np.eye(4, dtype=np.float32)
        self.viewMode = GL_FILL
        # managers
        self.coreManager = None
        self.resourceManager = None
        self.sceneManager = None
        self.rendertarget_manager = None
        # console font
        self.console = None
        # components
        self.lastShader = None
        self.screen = None
        self.framebuffer = None

    @staticmethod
    def destroyScreen():
        # destroy
        pygame.display.quit()

    def initialize(self, width, height, screen):
        logger.info("Initialize Renderer")
        self.width = width
        self.height = height
        self.screen = screen

        self.coreManager = CoreManager.CoreManager.instance()
        self.resourceManager = ResourceManager.ResourceManager.instance()
        self.sceneManager = SceneManager.SceneManager.instance()
        self.rendertarget_manager = RenderTargetManager.instance()
        self.framebuffer = FrameBuffer(self.width, self.height)

        # console font
        self.console = Console()
        self.console.initialize(self)

        # set gl hint
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    def close(self):
        # record config
        self.coreManager.config.setValue("Screen", "size", [self.width, self.height])
        self.coreManager.config.setValue("Screen", "position", [0, 0])

        # destroy console
        self.console.close()

    def setViewMode(self, viewMode):
        if viewMode == COMMAND.VIEWMODE_WIREFRAME:
            self.viewMode = GL_LINE
        elif viewMode == COMMAND.VIEWMODE_SHADING:
            self.viewMode = GL_FILL

    def resizeScene(self, width=0, height=0):
        # You have to do pygame.display.set_mode again on Linux.
        if width <= 0 or height <= 0:
            width = self.width
            height = self.height
            if width <= 0 or height <= 0:
                return

        self.width = width
        self.height = height
        self.viewportRatio = float(width) / float(height)
        camera = self.sceneManager.getMainCamera()

        # get viewport matrix matrix
        self.perspective = perspective(camera.fov, self.viewportRatio, camera.near, camera.far)
        self.ortho = ortho(0, self.width, 0, self.height, camera.near, camera.far)

        # resize render targets
        self.rendertarget_manager.create_rendertargets(self.width, self.height)

        # Run pygame.display.set_mode at last!!! very important.
        if platformModule.system() == 'Linux':
            self.screen = pygame.display.set_mode((self.width, self.height),
                                                  OPENGL | DOUBLEBUF | RESIZABLE | HWPALETTE | HWSURFACE)

    def ortho_view(self):
        # Legacy opengl pipeline - set orthographic view
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def projection_view(self):
        # Legacy opengl pipeline - set perspective view
        camera = self.sceneManager.getMainCamera()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(camera.fov, self.viewportRatio, camera.near, camera.far)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def renderScene(self):
        startTime = timeModule.perf_counter()

        # Prepare to render into the renderbuffer and clear buffer
        self.framebuffer.bind_framebuffer()

        colortexture = self.rendertarget_manager.get_rendertarget(RenderTargets.BACKBUFFER)
        depthtexture = self.rendertarget_manager.get_rendertarget(RenderTargets.DEPTHSTENCIL)

        self.framebuffer.bind_rendertarget(colortexture, True, depthtexture, True)

        # render
        self.render_objects()
        self.render_postprocess()

        # reset shader program
        glUseProgram(0)

        # render text
        self.console.render()

        # blit frame buffer
        self.framebuffer.blitFramebuffer(self.width, self.height)

        endTime = timeModule.perf_counter()
        renderTime = endTime - startTime
        startTime = endTime

        # swap buffer
        pygame.display.flip()
        presentTime = timeModule.perf_counter() - startTime
        return renderTime, presentTime

    def render_objects(self):
        # set render state
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CW)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glShadeModel(GL_SMOOTH)
        glPolygonMode(GL_FRONT_AND_BACK, self.viewMode)

        camera = self.sceneManager.getMainCamera()
        viewTransform = camera.transform
        vpMatrix = np.dot(viewTransform.inverse_matrix, self.perspective)

        # Test Code : bind scene shader constants
        self.sceneManager.uniformSceneConstants.bindData(viewTransform.inverse_matrix, self.perspective,
                                                         viewTransform.pos, FLOAT_ZERO)
        light = self.sceneManager.lights[0]
        light.transform.setPos((math.sin(timeModule.time()) * 10.0, 0.0, math.cos(timeModule.time()) * 10.0))
        self.sceneManager.uniformLightConstants.bindData(light.transform.getPos(), FLOAT_ZERO, light.lightColor)

        # Test Code : sort tge list by mesh, material
        static_meshes = self.sceneManager.getStaticMeshes()[:]
        geometry_instances = []
        for static_mesh in static_meshes:
            geometry_instances += static_mesh.geometry_instances
        geometry_instances.sort(key=lambda x: id(x.geometry))

        # draw static meshes
        last_geometry = None
        last_material = None
        last_material_instance = None
        for geometry_instance in geometry_instances:
            obj = geometry_instance.parent_object
            material_instance = geometry_instance.material_instance
            material = material_instance.material if material_instance else None

            if last_material != material and material is not None:
                material.useProgram()

            if last_material_instance != material_instance and material_instance is not None:
                material_instance.bind_material_instance()

            obj.bind_object(vpMatrix)

            # At last, bind buffers
            if last_geometry != geometry_instance.geometry and geometry_instance is not None:
                geometry_instance.bindBuffers()

            # draw
            if geometry_instance and material_instance:
                geometry_instance.draw()

            last_material = material
            last_geometry = geometry_instance.geometry
            last_material_instance = material_instance

    def render_postprocess(self):
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        glBlendEquation(GL_FUNC_ADD)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.sceneManager.tonemapping.render()

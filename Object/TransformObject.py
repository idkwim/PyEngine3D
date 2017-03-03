import numpy as np

from Core import logger, config
from Utilities import *


class TransformObject:
    def __init__(self, pos):
        self.moved = False
        self.rotated = False
        self.scaled = False
        self.updated = False

        # transform
        self.matrix = Identity()
        self.inverse_matrix = Identity()
        self.translateMatrix = Identity()
        self.rotationMatrix = Identity()
        self.scaleMatrix = Identity()

        self.pos = Float3()
        self.oldPos = Float3()

        self.rot = Float3()
        self.oldRot = Float3()

        self.right = WORLD_RIGHT.copy()
        self.up = WORLD_UP.copy()
        self.front = WORLD_FRONT.copy()

        self.view_right = WORLD_RIGHT.copy()
        self.view_up = WORLD_UP.copy()
        self.view_front = WORLD_FRONT.copy()

        self.scale = Float3()
        self.oldScale = Float3()

        # init transform
        self.setPos(pos)
        self.setScale(Float3(1.0, 1.0, 1.0))
        self.updateTransform()

    def resetTransform(self):
        self.setPos(Float3())
        self.setRot(Float3())
        self.setScale(Float3(1.0, 1.0, 1.0))
        self.updateTransform()

    # Translate
    def getPos(self):
        return self.pos

    def setPos(self, pos):
        self.moved = True
        self.pos[...] = pos

    def setPosX(self, x):
        self.moved = True
        self.pos[0] = x

    def setPosY(self, y):
        self.moved = True
        self.pos[1] = y

    def setPosZ(self, z):
        self.moved = True
        self.pos[2] = z

    def move(self, vDelta):
        self.moved = True
        self.pos[...] = self.pos + vDelta

    def moveToFront(self, delta):
        self.moved = True
        self.pos[...] = self.pos + self.front * delta

    def moveToRight(self, delta):
        self.moved = True
        self.pos[...] = self.pos + self.right * delta

    def moveToUp(self, delta):
        self.moved = True
        self.pos[...] = self.pos + self.up * delta

    def moveToViewFront(self, delta):
        self.moved = True
        self.pos[...] = self.pos + self.view_front * delta

    def moveToViewRight(self, delta):
        self.moved = True
        self.pos[...] = self.pos + self.view_right * delta

    def moveToViewUp(self, delta):
        self.moved = True
        self.pos[...] = self.pos + self.view_up * delta

    def moveX(self, delta):
        self.moved = True
        self.pos[0] += delta

    def moveY(self, delta):
        self.moved = True
        self.pos[1] += delta

    def moveZ(self, delta):
        self.moved = True
        self.pos[2] += delta

    # Rotation
    def getRotation(self):
        return self.rot

    def setRot(self, rot):
        self.rotated = True
        self.rot[...] = rot

    def setPitch(self, pitch):
        self.rotated = True
        self.rot[0] = pitch
        if self.rot[0] > TWO_PI:
            self.rot[0] -= TWO_PI
        elif self.rot[0] < 0.0:
            self.rot[0] += TWO_PI

    def setYaw(self, yaw):
        self.rotated = True
        self.rot[1] = yaw
        if self.rot[1] > TWO_PI:
            self.rot[1] -= TWO_PI
        elif self.rot[1] < 0.0:
            self.rot[1] += TWO_PI

    def setRoll(self, roll):
        self.rotated = True
        self.rot[2] = roll
        if self.rot[2] > TWO_PI:
            self.rot[2] -= TWO_PI
        elif self.rot[2] < 0.0:
            self.rot[2] += TWO_PI

    def rotationPitch(self, delta=0.0):
        self.rotated = True
        self.rot[0] += delta
        if self.rot[0] > TWO_PI:
            self.rot[0] -= TWO_PI
        elif self.rot[0] < 0.0:
            self.rot[0] += TWO_PI

    def rotationYaw(self, delta=0.0):
        self.rotated = True
        self.rot[1] += delta
        if self.rot[1] > TWO_PI:
            self.rot[1] -= TWO_PI
        elif self.rot[1] < 0.0:
            self.rot[1] += TWO_PI

    def rotationRoll(self, delta=0.0):
        self.rotated = True
        self.rot[2] += delta
        if self.rot[2] > TWO_PI:
            self.rot[2] -= TWO_PI
        elif self.rot[2] < 0.0:
            self.rot[2] += TWO_PI

    # Scale
    def getScale(self):
        return self.scale

    def setScale(self, vScale):
        self.scaled = True
        self.scale[...] = vScale

    def setScaleX(self, x):
        self.scaled = True
        self.scale[0] = x

    def setScaleY(self, y):
        self.scaled = True
        self.scale[1] = y

    def setScaleZ(self, z):
        self.scaled = True
        self.scale[2] = z

    # update Transform
    def updateTransform(self):
        self.updated = False

        if self.moved and not all(self.oldPos == self.pos):
            self.oldPos[...] = self.pos
            self.translateMatrix = getTranslateMatrix(self.pos[0], self.pos[1], self.pos[2])
            self.moved = False
            self.updated = True

        if self.rotated and not all(self.oldRot == self.rot):
            self.oldRot[...] = self.rot
            '''
            self.rotationMatrix = getRotationMatrixZ(self.rot[2])
            rotateY(self.rotationMatrix, self.rot[1])
            rotateX(self.rotationMatrix, self.rot[0])
            self.rotated = False
            self.updated = True
            '''

        if self.scaled and not all(self.oldScale == self.scale):
            self.oldScale[...] = self.scale
            self.scaleMatrix = getScaleMatrix(self.scale[0], self.scale[1], self.scale[2])
            self.scaled = False
            self.updated = True

        if self.updated:
            self.matrix = np.dot(self.scaleMatrix, np.dot(self.rotationMatrix, self.translateMatrix))
            '''
            self.front = self.matrix[:3, 2]
            self.right = self.matrix[:3, 0]
            self.up = self.matrix[:3, 1]
            '''

    # It's view matrix.
    def updateInverseTransform(self):
        if self.updated:
            self.inverse_matrix = np.linalg.inv(self.matrix)
            self.view_front = self.inverse_matrix[:3, 2]
            self.view_right = self.inverse_matrix[:3, 0]
            self.view_up = self.inverse_matrix[:3, 1]

    def getTransformInfos(self):
        text = "\tPosition : " + " ".join(["%2.2f" % i for i in self.pos])
        text += "\n\tRotation : " + " ".join(["%2.2f" % i for i in self.rot])
        text += "\n\tFront : " + " ".join(["%2.2f" % i for i in self.front])
        text += "\n\tRight : " + " ".join(["%2.2f" % i for i in self.right])
        text += "\n\tUp : " + " ".join(["%2.2f" % i for i in self.up])
        text += "\n\tMatrix"
        text += "\n\t" + " ".join(["%2.2f" % i for i in self.matrix[:, 0]])
        text += "\n\t" + " ".join(["%2.2f" % i for i in self.matrix[:, 1]])
        text += "\n\t" + " ".join(["%2.2f" % i for i in self.matrix[:, 2]])
        text += "\n\t" + " ".join(["%2.2f" % i for i in self.matrix[:, 3]])
        return text

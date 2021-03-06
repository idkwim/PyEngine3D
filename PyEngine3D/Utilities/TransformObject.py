import numpy as np

from .Transform import *


class TransformObject:
    def __init__(self, local=None):
        self.quat = Float4(0.0, 0.0, 0.0, 1.0)
        self.local = local if local is not None else Matrix4()

        self.updated = True

        self.left = WORLD_LEFT.copy()
        self.up = WORLD_UP.copy()
        self.front = WORLD_FRONT.copy()

        self.pos = Float3()
        self.rot = Float3()
        self.scale = Float3(1, 1, 1)

        self.prev_Pos = Float3()
        self.prev_Rot = Float3()
        self.prev_Scale = Float3(1, 1, 1)

        self.rotationMatrix = Matrix4()

        self.matrix = Matrix4()
        self.inverse_matrix = Matrix4()

        self.prev_matrix = Matrix4()
        self.prev_inverse_matrix = Matrix4()

        self.update_transform(True)

    def reset_transform(self):
        self.updated = True
        self.set_pos(Float3())
        self.set_rotation(Float3())
        self.set_scale(Float3(1, 1, 1))
        self.update_transform(True)

    # Translate
    def get_pos(self):
        return self.pos

    def get_pos_x(self):
        return self.pos[0]

    def get_pos_y(self):
        return self.pos[1]

    def get_pos_z(self):
        return self.pos[2]

    def set_pos(self, pos):
        self.pos[...] = pos

    def set_pos_x(self, x):
        self.pos[0] = x

    def set_pos_y(self, y):
        self.pos[1] = y

    def set_pos_z(self, z):
        self.pos[2] = z

    def move(self, pos):
        self.pos[...] = self.pos + pos

    def move_front(self, pos):
        self.pos[...] = self.pos + self.front * pos

    def move_left(self, pos):
        self.pos[...] = self.pos + self.left * pos

    def move_up(self, pos):
        self.pos[...] = self.pos + self.up * pos

    def move_x(self, pos_x):
        self.pos[0] += pos_x

    def move_y(self, pos_y):
        self.pos[1] += pos_y

    def move_z(self, pos_z):
        self.pos[2] += pos_z

    # Rotation
    def get_rotation(self):
        return self.rot

    def get_pitch(self):
        return self.rot[0]

    def get_yaw(self):
        return self.rot[1]

    def get_roll(self):
        return self.rot[2]

    def set_rotation(self, rot):
        self.rot[...] = rot

    def set_pitch(self, pitch):
        if pitch > TWO_PI or pitch < 0.0:
            pitch %= TWO_PI
        self.rot[0] = pitch

    def set_yaw(self, yaw):
        if yaw > TWO_PI or yaw < 0.0:
            yaw %= TWO_PI
        self.rot[1] = yaw

    def set_roll(self, roll):
        if roll > TWO_PI or roll < 0.0:
            roll %= TWO_PI
        self.rot[2] = roll

    def rotation(self, rot):
        self.rotation_pitch(rot[0])
        self.rotation_yaw(rot[1])
        self.rotation_roll(rot[2])

    def rotation_pitch(self, delta=0.0):
        self.rot[0] += delta
        if self.rot[0] > TWO_PI or self.rot[0] < 0.0:
            self.rot[0] %= TWO_PI

    def rotation_yaw(self, delta=0.0):
        self.rot[1] += delta
        if self.rot[1] > TWO_PI or self.rot[1] < 0.0:
            self.rot[1] %= TWO_PI

    def rotation_roll(self, delta=0.0):
        self.rot[2] += delta
        if self.rot[2] > TWO_PI or self.rot[2] < 0.0:
            self.rot[2] %= TWO_PI

    # Scale
    def get_scale(self):
        return self.scale

    def get_scale_x(self):
        return self.scale[0]

    def get_scale_Y(self):
        return self.scale[1]

    def get_scale_z(self):
        return self.scale[2]

    def set_scale(self, scale):
        self.scale[...] = scale

    def set_scale_x(self, x):
        self.scale[0] = x

    def set_scale_y(self, y):
        self.scale[1] = y

    def set_scale_z(self, z):
        self.scale[2] = z

    def scaling(self, scale):
        self.scale[...] = self.scale + scale

    # update Transform
    def update_transform(self, update_inverse_matrix=False, force_update=False):
        prev_updated = self.updated
        self.updated = False

        if any(self.prev_Pos != self.pos) or force_update:
            self.prev_Pos[...] = self.pos
            self.updated = True

        if any(self.prev_Rot != self.rot) or force_update:
            self.prev_Rot[...] = self.rot
            self.updated = True

            # Matrix Rotation - faster
            matrix_rotation(self.rotationMatrix, *self.rot)
            matrix_to_vectors(self.rotationMatrix, self.left, self.up, self.front)

            # Euler Rotation - slow
            # p = get_rotation_matrix_x(self.rot[0])
            # y = get_rotation_matrix_y(self.rot[1])
            # r = get_rotation_matrix_z(self.rot[2])
            # self.rotationMatrix = np.dot(p, np.dot(y, r))
            # matrix_to_vectors(self.rotationMatrix, self.right, self.up, self.front)

            # Quaternion Rotation - slower
            # euler_to_quaternion(*self.rot, self.quat)
            # quaternion_to_matrix(self.quat, self.rotationMatrix)
            # matrix_to_vectors(self.rotationMatrix, self.right, self.up, self.front)

        if any(self.prev_Scale != self.scale) or force_update:
            self.prev_Scale[...] = self.scale
            self.updated = True

        if prev_updated or self.updated:
            self.prev_matrix[...] = self.matrix
            if update_inverse_matrix:
                self.prev_inverse_matrix[...] = self.inverse_matrix

        if self.updated:
            self.matrix[...] = self.local
            transform_matrix(self.matrix, self.pos, self.rotationMatrix, self.scale)

            if update_inverse_matrix:
                # self.inverse_matrix[...] = np.linalg.inv(self.matrix)
                self.inverse_matrix[...] = self.local
                inverse_transform_matrix(self.inverse_matrix, self.pos, self.rotationMatrix, self.scale)

        return self.updated

    def get_transform_infos(self):
        text = "\tPosition : " + " ".join(["%2.2f" % i for i in self.pos])
        text += "\n\tRotation : " + " ".join(["%2.2f" % i for i in self.rot])
        text += "\n\tFront : " + " ".join(["%2.2f" % i for i in self.front])
        text += "\n\tLeft : " + " ".join(["%2.2f" % i for i in self.left])
        text += "\n\tUp : " + " ".join(["%2.2f" % i for i in self.up])
        text += "\n\tMatrix"
        text += "\n\t" + " ".join(["%2.2f" % i for i in self.matrix[0, :]])
        text += "\n\t" + " ".join(["%2.2f" % i for i in self.matrix[1, :]])
        text += "\n\t" + " ".join(["%2.2f" % i for i in self.matrix[2, :]])
        text += "\n\t" + " ".join(["%2.2f" % i for i in self.matrix[3, :]])
        return text

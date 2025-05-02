import numpy as np
import math
from pyglm import glm
from glm import vec3

class Camera:
    width:                 int
    height:                int
    size:                  int
    v_fov_h:               float
    pitch:                 float
    yaw:                   float
    position:              vec3
    frame_index:           int
    viewport_height:       float
    viewport_width:        float
    pixel_delta_u:         float
    pixel_delta_v:         float
    ray_directions:        list[vec3]
    monte_carlo_accu_data: list[vec3]
    image:                 np.ndarray
    x_axis:                vec3
    y_axis:                vec3
    z_axis:                vec3

    def __init__(self, width: int, height: int, position: vec3, pitch: float, yaw: float, vfov: float):
        theta = math.radians(vfov)
        h = math.tan(theta / 2.0)
        self.width       = width
        self.height      = height
        self.v_fov_h     = h
        self.pitch       = pitch
        self.yaw         = yaw
        self.position    = position
        self.frame_index = 1
        self.z_axis      = vec3(0, 0, -1)
        self.image = np.ndarray((0))
        self.resize_camera(width, height)
        self.rotate_camera(pitch, yaw)
        self.calculate_ray_directions()

    def resize_camera(self, width: int, height: int):
        self.width = width
        self.height = height
        self.size = width * height
        self.monte_carlo_accu_data = [vec3(0, 0, 0) for _  in range(self.size)]
        self.ray_directions = [vec3(0, 0, 0) for _  in range(self.size)]
        self.image = np.zeros((self.size), np.uint8)
        self.viewport_height = 1.0 * self.v_fov_h
        self.viewport_width = self.viewport_height * float(width) / float(height)
        self.pixel_delta_u = self.viewport_width / float(self.width)
        self.pixel_delta_v = self.viewport_height / float(self.height)
        self.reset_accu_data()

    def reset_accu_data(self):
        self.frame_index = 1
        self.monte_carlo_accu_data = [vec3(0, 0, 0) for _  in range(self.size)]

    def calculate_ray_directions(self):
        up = vec3(0.0, 1.0, 0.0)
        right_direction = glm.normalize(glm.cross(self.z_axis, up)) * (self.viewport_width / 2.0)
        up_direction = glm.normalize(glm.cross(self.z_axis, right_direction)) * (self.viewport_height / 2.0)
        for y in range(self.height):
            v = float(y) / float(self.height) * 2.0 - 1.0
            scaled_up_dir = up_direction * v
            for x in range(self.width):
                u = float(x) / float(self.width) * 2.0 - 1.0
                scaled_right_dir = right_direction * u
                self.ray_directions[x + y * self.width] = (self.z_axis + scaled_right_dir + scaled_up_dir)
    
    @staticmethod
    def rotate_vector(vector: vec3, rotation_quaternion: glm.quat) -> vec3:
        quat_to_rotate = glm.quat(
            0,
            vector.x,
            vector.y,
            vector.z,
        )
        result = rotation_quaternion * quat_to_rotate * glm.conjugate(rotation_quaternion)
        return vec3(result.x, result.y, result.z)

    def rotate_camera(self, pitch_delta_radians: float, yaw_delta_radians: float):
        self.pitch += pitch_delta_radians
        self.yaw += yaw_delta_radians
        up_dir = vec3(0.0, 1.0, 0.0)
        self.x_axis = glm.normalize(glm.cross(self.z_axis, up_dir))
        self.y_axis = glm.normalize(glm.cross(self.z_axis, self.x_axis))
        self.z_axis = glm.normalize(
            Camera.rotate_vector(
                self.z_axis,
                glm.angleAxis(-pitch_delta_radians, self.x_axis) * glm.angleAxis(yaw_delta_radians, self.y_axis)
            ),
        )
        self.reset_accu_data()

    def update_x_position(self, x: float):
        self.position += self.x_axis * x
        self.reset_accu_data()

    def update_y_position(self, y: float):
        self.position.y += y
        self.reset_accu_data()

    def update_z_position(self, z: float):
        self.position = self.position + self.z_axis * z
        self.reset_accu_data()

    def update_camera(self) -> bool:
        pitch: float = 0
        yaw: float = 0
        updated = False
        # if rl.IsKeyDown(.W) {
        #     update_z_position(camera, 0.1)
        #     updated = true
        # }

        # if rl.IsKeyDown(.S) {
        #     update_z_position(camera, -0.1)
        #     updated = true
        # }

        # if rl.IsKeyDown(.D) {
        #     update_x_position(camera, 0.1)
        #     updated = true
        # }

        # if rl.IsKeyDown(.A) {
        #     update_x_position(camera, -0.1)
        #     updated = true
        # }

        # if rl.IsKeyDown(.Q) {
        #     update_y_position(camera, 0.1)
        #     updated = true
        # }

        # if rl.IsKeyDown(.E) {
        #     update_y_position(camera, -0.1)
        #     updated = true
        # }

        # if rl.IsKeyDown(.UP) {
        #     pitch -= 0.05
        # }

        # if rl.IsKeyDown(.DOWN) {
        #     pitch += 0.05
        # }

        # if rl.IsKeyDown(.LEFT) {
        #     yaw -= 0.05
        # }

        # if rl.IsKeyDown(.RIGHT) {
        #     yaw += 0.05
        # }

        # if pitch != 0 || yaw != 0 {
        #     rotate_camera(camera, pitch, yaw)
        #     calculate_ray_directions(camera)
        #     updated = true
        # }

        return updated

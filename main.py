from pyglm.glm import vec3
import serial
from camera import Camera
from src.fixedpoint import FixedPoint, fixed_t
from src.test_utils import Ray, Vec3, Triangle, Vec3_from_glm
import time
from obj import load_obj
import cv2
import numpy as np

def load_mesh(name: str, position: vec3) -> list[Triangle]:
    obj, ok = load_obj(name)
    if not ok:
        raise RuntimeError(f"Failed to load obj file {name}")
    
    tris: list[Triangle] = [Triangle.zero() for _ in range(len(obj.faces))]

    for i, face in enumerate(obj.faces):
        v0 = vec3(*obj.vertices[face[0][0]]) + position
        v1 = vec3(*obj.vertices[face[1][0]]) + position
        v2 = vec3(*obj.vertices[face[2][0]]) + position

        n0 = vec3(*obj.vertex_normals[face[0][2]])
        n1 = vec3(*obj.vertex_normals[face[1][2]])
        n2 = vec3(*obj.vertex_normals[face[2][2]])

        average = (n0 + n1 + n2) / 3.0

        tris[i].x = Vec3_from_glm(v0)
        tris[i].y = Vec3_from_glm(v1)
        tris[i].z = Vec3_from_glm(v2)
        tris[i].normal = Vec3_from_glm(average)
    return tris

def trace_ray(_ray: Ray) -> tuple[FixedPoint, int]:
    s.write(bytes([3]))
    for byte in _ray.to_bytes():
        s.write(bytes([int(byte, 2)]))

    t_data = ""

    for i in range(3):
        t_data = (bin(int(s.read().hex(), 16))[2:].zfill(8)) + t_data

    index_data = ""
    for i in range(2):
        index_data = (bin(int(s.read().hex(), 16))[2:].zfill(8)) + index_data

    return (fixed_t(t_data), int(index_data, 2))

def write_triangle(address: int, tri: Triangle):
    assert address < 2048 and address >= 0
    s.write(bytes([1]))

    address_bytes = bytes([address & 0xff, (address & 0xff00) >> 8])
    s.write(address_bytes)
    for byte in tri.to_bytes():
        s.write(bytes([int(byte, 2)]))

def read_triangle(address: int) -> Triangle:
    assert address < 2048 and address >= 0
    s.write(bytes([2]))

    address_bytes = bytes([address & 0xff, (address & 0xff00) >> 8])
    s.write(address_bytes)
    tri_bytes = ["" for _ in range(36)]
    for i in range(36):
        data = int(s.read().hex(), 16)
        tri_bytes[35 - i] = bin(data)[2:].zfill(8)
    return Triangle.from_bytes(tri_bytes)

tris = load_mesh("tri.obj", vec3(0,0,0))
camera = Camera(128, 128, vec3(-8.2, 0, -0.94), 0.0, -4.5, 45)
s = serial.Serial("/dev/ttyUSB0", 921600)
for i, tri in enumerate(tris):
    write_triangle(i, tri)

print(len(tris) - 1)
write_triangle(len(tris) - 1, Triangle.zero())
for i, direction in enumerate(camera.ray_directions):
    ray = Ray(origin=Vec3_from_glm(camera.position), direction=Vec3_from_glm(direction))
    res = trace_ray(ray)
    if res[1] != 65535:
        print(i, ray, res[0], res[1])
        camera.image[i] = 255
    else:
        camera.image[i] = 0

s.close()
image = np.reshape(camera.image, (camera.width, camera.height))
cv2.imshow("window", image)
cv2.waitKey(0)
exit()






ray = Ray(origin = Vec3(-8.5, 0, -0.94), direction = Vec3(1.23048, -0.120812304, 0.009252384))

ray = Ray(
    origin = Vec3(-8.1999998, 0, -0.94), 
    direction = Vec3(1.0053048, -0.120812304, 0.009252384)
)

triangle=Triangle(
            x=Vec3(-1.0, -1.000000, 1.000000),
            y=Vec3(-1.000000, 1.000000, 0.000000),
            z=Vec3(-1.000000, -1.000000, -1.000000),
            normal=Vec3(-1.0000, 0.0000, 0.0000),
        )


now = time.time()
# for i in range(100):
# for i in range(10):
#     if i % 2 == 1:
    #     write_triangle(i, 
    #         Triangle(
    #             x = Vec3(
    #                 x = fixed_t(0.3), 
    #                 y = fixed_t(0.4),
    #                 z = fixed_t(0.5),
    #             ),
    #             y = Vec3(
    #                 x = fixed_t(0.6), 
    #                 y = fixed_t(0.7),
    #                 z = fixed_t(0.8),
    #             ), 
    #             z = Vec3(
    #                 x = fixed_t(0.96), 
    #                 y = fixed_t(0.41),
    #                 z = fixed_t(0.23),
    #             ),
    #             normal = Vec3(
    #                 x = fixed_t(0.123), 
    #                 y = fixed_t(0.43),
    #                 z = fixed_t(0.51),
    #             ),
    #         )
    #     )
    # else:

triangle1=Triangle(
    x=Vec3(-.5, -1.000000, 1.000000),
    y=Vec3(-.5, 1.000000, 0.000000),
    z=Vec3(-.5, -1.000000, -1.000000),
    normal=Vec3(-1.0000, 0.0000, 0.0000),
)
triangle2=Triangle(
    x=Vec3(-1.0, -1.000000, 1.000000),
    y=Vec3(-1.0, 1.000000, 0.000000),
    z=Vec3(-1.0, -1.000000, -1.000000),
    normal=Vec3(-1.0000, 0.0000, 0.0000),
)
triangle3=Triangle(
    x=Vec3(1.0, -1.000000, 1.000000),
    y=Vec3(-1.0, 1.000000, 0.000000),
    z=Vec3(-1.0, -1.000000, -1.000000),
    normal=Vec3(-1.0000, 0.0000, 0.0000),
)
write_triangle(0, triangle1)
write_triangle(1, triangle2)
write_triangle(2, triangle1)
write_triangle(3, triangle2)
write_triangle(4, triangle2)
write_triangle(5, triangle1)
write_triangle(5, Triangle.zero())
print(read_triangle(0))
print(read_triangle(1))
print(read_triangle(2))
print(trace_ray(ray))
# triangle=Triangle(
#     x=Vec3(-1.0, -1.000000, 1.000000),
#     y=Vec3(-1.0, 1.000000, 0.000000),
#     z=Vec3(-1.0, -1.000000, -1.000000),
#     normal=Vec3(-1.0000, 0.0000, 0.0000),
# )
# write_triangle(0, triangle)
# write_triangle(1, triangle)
# write_triangle(2, triangle)
# triangle=Triangle(
#             x=Vec3(-.5, -1.000000, 1.000000),
#             y=Vec3(-.5, 1.000000, 0.000000),
#             z=Vec3(-.5, -1.000000, -1.000000),
#             normal=Vec3(-1.0000, 0.0000, 0.0000),
#         )
# write_triangle(3, triangle)
# write_triangle(4, triangle)

print(time.time() - now)

# now = time.time()
# for i in range(10):
#     print(read_triangle(i))
# print(time.time() - now)
    
# # 00000001
# import random
# for index in range(1000):
#     s.write(bytes([1]))
#     # time.sleep(0.001)
#     s.write(bytes([11]))
#     # time.sleep(0.001)
#     s.write(bytes([0]))
#     # time.sleep(0.001)
#     data_sent = []
#     for i in range(36):
#         data = i + random.randint(0, 100)
#         data_sent.append(data)
#         print(data, end=", ")
#         s.write(bytes([data]))
#         # time.sleep(0.001)
#     print()

#     s.write(bytes([2]))
#     # time.sleep(0.001)
#     s.write(bytes([11]))
#     # time.sleep(0.001)
#     s.write(bytes([0]))
#     for i in range(36):
#         data = int(s.read().hex(), 16)
#         print(data, end=", ")
#         if data_sent[i] != data:
#             print("============== ERROR =============")
#             time.sleep(1)
#     print(index)
s.close()
# import json
# from src.test_utils import Triangle, Vec3

# # with open("src/scene.json") as f:
# #     scene = json.load(f)

# # triangles = scene["triangles"]

# tri = Triangle(
#     x=Vec3(-1.000000, -1.000000, 1.000000),
#     y=Vec3(-1.000000, -1.000000, -1.000000),
#     z=Vec3(-1.000000, 1.000000, 0.000000),
#     normal=Vec3(-1.0000, -0.0000, -0.0000),
# )

# # for tri in triangles:
# #     tri = Triangle.from_json(tri)
# print(tri.to_vhd())
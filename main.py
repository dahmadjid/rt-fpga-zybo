import glm
from pyglm.glm import vec3
import serial
from camera import Camera
from src.fixedpoint import FixedPoint, fixed_t
from src.test_utils import Ray, Vec3, Triangle, Vec3_from_glm
from obj import load_mesh

s = serial.Serial("/dev/ttyUSB0", 921600)

def trace_ray(_ray: Ray) -> tuple[FixedPoint, int]:
    s.write(bytes([3]))
    for byte in _ray.to_bytes():
        s.write(bytes([int(byte, 2)]))

    t_data = ""

    for i in range(3):
        t_data += (bin(int(s.read().hex(), 16))[2:].zfill(8))

    index_data = ""
    for i in range(2):
        index_data += (bin(int(s.read().hex(), 16))[2:].zfill(8))


    def read_fixed_t(): 
        __data__ = ""
        for i in range(3):
            __data__ += (bin(int(s.read().hex(), 16))[2:].zfill(8))
        return  fixed_t(__data__)

    # for i in range(3):
    print("=================")
    print("=================")
    print("=================")
    print("debug_index=0")
    print("hit_info", read_fixed_t())
    print("closest_hit_info", read_fixed_t())
    print("flags", bin(int(s.read()[0])))
    print("=================")
    print("debug_index=1")
    print("hit_info", read_fixed_t())
    print("closest_hit_info", read_fixed_t())
    print("flags", bin(int(s.read()[0])))
    print("=================")
    print("debug_index=2")
    print("hit_info", read_fixed_t())
    print("closest_hit_info", read_fixed_t())
    print("flags", bin(int(s.read()[0])))
    print("=================")
    print("final=1")
    print("hit_info", read_fixed_t())
    print("flags", bin(int(s.read()[0])))
    print("=================")
    print("=================")
    
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

tris = load_mesh("ico.obj", vec3(0., 0, 0))
camera = Camera(512, 512, vec3(-11, 0, -2.), 0.0, -4.5, 45)
for i, tri in enumerate(tris):
    print(i)
    print(tri)

# tris[0].normal = tris[1].normal
for i in range(len(tris)):
    write_triangle(i, tris[i])
write_triangle(len(tris) - 1, Triangle.zero())

light = glm.normalize(vec3(-1, 1, 1))
def color(tri_index: int):
    color = glm.dot(tris[tri_index].normal.to_glm(), light) * 255
    color = max(0, color)
    color = min(255, color)
    return vec3(int(color))
    # if tri_index == 0:
    #     return vec3(255)
    # if tri_index == 1:
    #     return vec3(255, 0, 0)
    # if tri_index == 2:
    #     return vec3(0, 255, 0)
    # if tri_index == 3:
    #     return vec3(0, 0, 255)
    # if tri_index == 4:
    #     return vec3(255, 0, 255)
    # return vec3(255)



for i, direction in enumerate(camera.ray_directions):
    ray = Ray(origin=Vec3_from_glm(camera.position), direction=Vec3_from_glm(direction))
    res = trace_ray(ray)
    if res[1] != 65535:
        # print(i, ray, res[0], res[1])
        camera.image[i] = color(res[1])
    else:
        camera.image[i] = vec3(0)
camera.display_ppm()
        
# write_triangle(0, Triangle.zero())
# for i, direction in enumerate(camera.ray_directions):
#     if i - int(i / 128) * 128 < 48:
#         ray = Ray(origin=Vec3_from_glm(camera.position), direction=Vec3_from_glm(direction))
#         res = trace_ray(ray)
#         if res[1] != 65535:
#             # print(i, res[0], res[1])
#             camera.image[i] = color(res[1])
#         else:
#             camera.image[i] = vec3(0)
#         hit = res[1] != 65535

#         if hits[i] != hit:
#             print("fuckyou", i)
s.close()






# exit()






# ray = Ray(origin = Vec3(-8.5, 0, -0.94), direction = Vec3(1.23048, -0.120812304, 0.009252384))

# ray = Ray(
#     origin = Vec3(-8.1999998, 0, -0.94), 
#     direction = Vec3(1.0053048, -0.120812304, 0.009252384)
# )

# triangle=Triangle(
#             x=Vec3(-1.0, -1.000000, 1.000000),
#             y=Vec3(-1.000000, 1.000000, 0.000000),
#             z=Vec3(-1.000000, -1.000000, -1.000000),
#             normal=Vec3(-1.0000, 0.0000, 0.0000),
#         )


# now = time.time()
# # for i in range(100):
# # for i in range(10):
# #     if i % 2 == 1:
#     #     write_triangle(i, 
#     #         Triangle(
#     #             x = Vec3(
#     #                 x = fixed_t(0.3), 
#     #                 y = fixed_t(0.4),
#     #                 z = fixed_t(0.5),
#     #             ),
#     #             y = Vec3(
#     #                 x = fixed_t(0.6), 
#     #                 y = fixed_t(0.7),
#     #                 z = fixed_t(0.8),
#     #             ), 
#     #             z = Vec3(
#     #                 x = fixed_t(0.96), 
#     #                 y = fixed_t(0.41),
#     #                 z = fixed_t(0.23),
#     #             ),
#     #             normal = Vec3(
#     #                 x = fixed_t(0.123), 
#     #                 y = fixed_t(0.43),
#     #                 z = fixed_t(0.51),
#     #             ),
#     #         )
#     #     )
#     # else:

# triangle1=Triangle(
#     x=Vec3(-.5, -1.000000, 1.000000),
#     y=Vec3(-.5, 1.000000, 0.000000),
#     z=Vec3(-.5, -1.000000, -1.000000),
#     normal=Vec3(-1.0000, 0.0000, 0.0000),
# )
# triangle2=Triangle(
#     x=Vec3(-1.0, -1.000000, 1.000000),
#     y=Vec3(-1.0, 1.000000, 0.000000),
#     z=Vec3(-1.0, -1.000000, -1.000000),
#     normal=Vec3(-1.0000, 0.0000, 0.0000),
# )
# triangle3=Triangle(
#     x=Vec3(1.0, -1.000000, 1.000000),
#     y=Vec3(-1.0, 1.000000, 0.000000),
#     z=Vec3(-1.0, -1.000000, -1.000000),
#     normal=Vec3(-1.0000, 0.0000, 0.0000),
# )
# write_triangle(0, triangle1)
# # write_triangle(1, triangle2)
# # write_triangle(2, triangle1)
# # write_triangle(3, triangle2)
# # write_triangle(4, triangle2)
# # write_triangle(5, triangle1)
# # write_triangle(5, Triangle.zero())
# # print(read_triangle(0))
# # print(read_triangle(1))
# # print(read_triangle(2))
# # print(trace_ray(ray))
# # triangle=Triangle(
# #     x=Vec3(-1.0, -1.000000, 1.000000),
# #     y=Vec3(-1.0, 1.000000, 0.000000),
# #     z=Vec3(-1.0, -1.000000, -1.000000),
# #     normal=Vec3(-1.0000, 0.0000, 0.0000),
# # )
# # write_triangle(0, triangle)
# # write_triangle(1, triangle)
# # write_triangle(2, triangle)
# # triangle=Triangle(
# #             x=Vec3(-.5, -1.000000, 1.000000),
# #             y=Vec3(-.5, 1.000000, 0.000000),
# #             z=Vec3(-.5, -1.000000, -1.000000),
# #             normal=Vec3(-1.0000, 0.0000, 0.0000),
# #         )
# # write_triangle(3, triangle)
# # write_triangle(4, triangle)

# print(time.time() - now)


# s.close()




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


"""

=================
=================
debug_index=0
hit_info 13.5400390625
closest_hit_info 2047.999755859375
flags 0b0
=================
debug_index=1
hit_info 12.054931640625
closest_hit_info 2047.999755859375
flags 0b10
=================
debug_index=2
hit_info 12.054931640625
closest_hit_info 2047.999755859375
flags 0b1010
=================
final=1
hit_info 12.054931640625
flags 0b1010
=================
=================
"""

"""
=================
=================
debug_index=0
hit_info 13.5400390625
closest_hit_info 2047.999755859375
flags 0b0
=================
debug_index=1
hit_info 12.054931640625
closest_hit_info 2047.999755859375
flags 0b10
=================
debug_index=2
hit_info 12.054931640625
closest_hit_info 2047.999755859375
flags 0b1010
=================
final=1
hit_info 13.305419921875
flags 0b1111
=================
=================
11183 13.305419921875 0
"""

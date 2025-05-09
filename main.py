from pyglm.glm import vec3
import serial
from camera import Camera
from src.fixedpoint import FixedPoint, fixed_t
from src.test_utils import Ray, Vec3, Triangle, Vec3_from_glm
from obj import load_mesh

s = serial.Serial("/dev/ttyUSB0", 115200)

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


    def read_vec(): 
        __data__ = ""
        for i in range(3):
            __data__ += (bin(int(s.read().hex(), 16))[2:].zfill(8))
        return  fixed_t(__data__)

    for i in range(3):
        print(i, "x", read_vec())
        print(i, "y", read_vec())
        print(i, "z", read_vec())

    return (fixed_t(t_data), int(index_data, 2))

def write_triangle(address: int, tri: Triangle):
    assert address < 2048 and address >= 0
    s.write(bytes([1]))
    address_bytes = bytes([address & 0xff, (address & 0xff00) >> 8])
    s.write(address_bytes)
    for byte in tri.to_bytes():
        print(byte, end="")
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

    print("".join(tri_bytes))
    return Triangle.from_bytes(tri_bytes)

tris = load_mesh("test.obj", vec3(0.0, 0, 0))
camera = Camera(14, 14, vec3(-8.2, 0, -0.94), 0.0, -4.5, 45)

for i, tri in enumerate(tris):
    write_triangle(i, tris[i])
# print()
# 111111111111000110011001 111111111110111111111111000000000001000000000000111111111111000110011001000000000001000000000000000000000000000000000000111111111111000110011001111111111110111111111111111111111110111111111111111111111110111111111111000000000000000000000000000000000000000000000000
# 000000000001000110011001 111111111110111111111111000000000001000000000000000000000001000110011001000000000001000000000000000000000000000000000000000000000001000110011001111111111110111111111111111111111110111111111111111111111110111111111111000000000000000000000000000000000000000000000000
print(read_triangle(0))
print(read_triangle(1))
print(read_triangle(2))
write_triangle(len(tris) - 1, Triangle.zero())

# ray = Ray(origin = Vec3(-8.1999998, 0, -0.94), direction = Vec3(1.0053048, -0.120812304, 0.009252384))
# # print(", ".join(ray.to_bytes()[9:18]))
# res = trace_ray(ray)
# print(res)
# for i in range(len(tris)):
#     print(read_triangle(i))
def color(tri_index: int):
    if tri_index == 0:
        return vec3(255)
    if tri_index == 1:
        return vec3(255, 0, 0)
    if tri_index == 2:
        return vec3(0, 255, 0)
    if tri_index == 3:
        return vec3(0, 0, 255)
    if tri_index == 4:
        return vec3(255, 0, 255)
    return None
    
for i, direction in enumerate(camera.ray_directions):
    ray = Ray(origin=Vec3_from_glm(camera.position), direction=Vec3_from_glm(direction))
    res = trace_ray(ray)
    print(i, ray, res[0], res[1])
    if res[1] != 65535:
        camera.image[i] = color(res[1])
    else:
        camera.image[i] = vec3(0)

camera.display_ppm()
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
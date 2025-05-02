import serial
from src.fixedpoint import FixedPoint, fixed_t
from src.test_utils import Ray, Vec3, Triangle
import time
s = serial.Serial("/dev/ttyUSB0", 921600)

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
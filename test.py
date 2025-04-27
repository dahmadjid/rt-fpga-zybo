import serial
from src.fixedpoint import fixed_t
from src.test_utils import Ray, Vec3, Triangle
import time
s = serial.Serial("/dev/ttyUSB0", 921600)

# 00000011
s.write(bytes([3]))


ray = Ray(origin = Vec3(-8.5, 0, -0.94), direction = Vec3(1.1053048, -0.120812304, 0.009252384))
for byte in ray.to_bytes():
    print(f"{byte}")
    s.write(bytes([int(byte, 2)]))

t_data = ""

for i in range(3):
    t_data = (bin(int(s.read().hex(), 16))[2:].zfill(8)) + t_data

print(f"{t_data=} {fixed_t(t_data)}") 

for i in range(2):
    print(int(s.read().hex(), 16))

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
from glm import vec3
from obj import load_mesh
from src.test_utils import Triangle

tris: list[Triangle] = load_mesh("test2.obj", vec3(0))

f = open("src/ram.data", "w")

for tri in tris:
    f.write("".join(tri.to_bytes())+ "\n")

f.close()
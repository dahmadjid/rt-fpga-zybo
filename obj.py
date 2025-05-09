# thnx ai for converting this code from odin.
from pyglm.glm import vec3

from src.test_utils import Triangle, Vec3_from_glm

class ObjModel:
    def __init__(self):
        self.vertices = []
        self.vertex_normals = []
        self.uv_map = []
        self.faces = []

def load_obj(obj_file_path) -> tuple[ObjModel, bool]:
    """Loads an OBJ file and returns an ObjModel object."""
    try:
        with open(obj_file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Failed to read obj file: {obj_file_path}")
        return None, False

    model = ObjModel()
    for line in lines:
        line = line.strip()
        if not line or len(line) < 2:
            continue

        parts = line.split()
        line_type = parts[0]

        if line_type == 'v':
            try:
                vertex = [float(x) for x in parts[1:4]]
                model.vertices.append(vertex)
            except (ValueError, IndexError):
                print(f"Warning: Skipping invalid vertex line: {line}")
                continue
        elif line_type == 'vn':
            try:
                normal = [float(x) for x in parts[1:4]]
                model.vertex_normals.append(normal)
            except (ValueError, IndexError):
                print(f"Warning: Skipping invalid vertex normal line: {line}")
                continue
        elif line_type == 'vt':
            try:
                uv = [float(x) for x in parts[1:3]]
                model.uv_map.append(uv)
            except (ValueError, IndexError):
                print(f"Warning: Skipping invalid texture coordinate line: {line}")
                continue
        elif line_type == 'f':
            if len(parts) > 1:
                face_indices = []
                for i, part in enumerate(parts[1:]):
                    indices_str = part.split('/')
                    try:
                        vertex_index = int(indices_str[0]) - 1 if indices_str[0] else -1
                        normal_index = int(indices_str[2]) - 1 if len(indices_str) > 2 and indices_str[2] else -1
                        uv_index = int(indices_str[1]) - 1 if len(indices_str) > 1 and indices_str[1] else -1
                        face_indices.append((vertex_index, uv_index, normal_index))
                    except ValueError:
                        print(f"Warning: Skipping invalid face index: {part} in line: {line}")
                        face_indices = []
                        break
                if len(face_indices) == 3:
                    model.faces.append(face_indices)
                else:
                    print(f"Warning: Skipping face with less than 3 vertices in line: {line}")

    return model, True

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

if __name__ == '__main__':
    obj_file = 'suzanne.obj'  # Replace with your OBJ file path
    model, success = load_obj(obj_file)

    if success and model:
        print(f"Successfully loaded {obj_file}")
        print(f"Number of vertices: {len(model.vertices)}")
        print(f"Number of vertex normals: {len(model.vertex_normals)}")
        print(f"Number of UV coordinates: {len(model.uv_map)}")
        print(f"Number of faces: {len(model.faces)}")
        # You can now work with the 'model' object
    else:
        print("Failed to load the OBJ file.")

    
from src.test_utils import Triangle, Vec3


triangle=Triangle(
    x=Vec3(-1.001, -3.00111, 1.000000),
    y=Vec3(-1.000000, 1.000000, 0.000000),
    z=Vec3(-1.000000, -1.000000, -1.000000),
    normal=Vec3(-1.0000, 0.0000, 0.0000),
)

print(triangle.to_bytes())
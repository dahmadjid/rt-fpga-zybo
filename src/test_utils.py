import pprint
import glm
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal
from cocotb.handle import HierarchyObject, BinaryValue, ModifiableObject
from .fixedpoint import FixedPoint, fixed_t_from_bytes, fixed_t_to_bytes, fixed_t


g_total_fp_error = 0
g_max_fp_error = 0
g_min_fp_error = 1234567890
g_error_count = 0

def assign_dict_to_dut(dut: HierarchyObject, data: dict):
    for attr, value in data.items():
        dut_attr = dut.__getattr__(attr)
        if isinstance(value, dict) and isinstance(dut_attr, HierarchyObject):
            assign_dict_to_dut(dut_attr, value)
        elif isinstance(value, FixedPoint):
            dut_attr.value = value.bin_value
        elif isinstance(value, str):
            dut_attr.value = BinaryValue(value=value)
        elif isinstance(value, int):
            dut_attr.value = value
        else:
            raise RuntimeError(f"unsupported type={type(value)}")
        

def assert_fp_error(a: float, b: float, max_error: float, attr_name: str):
    err = abs(a - b)
    global g_total_fp_error
    global g_max_fp_error
    global g_min_fp_error
    global g_error_count
    if g_error_count == 0:
        g_min_fp_error = 123456789

    g_error_count += 1
    g_total_fp_error += err
    if g_max_fp_error < err:
        g_max_fp_error = err
        
    if g_min_fp_error > err:
        g_min_fp_error = err

    print(f"{g_total_fp_error/g_error_count=} {g_min_fp_error=} {g_max_fp_error=} {g_error_count=}")
    assert err < max_error, f"[{attr_name}] max fixed_point error exceeded abs({a} - {b}) == {err} {max_error=}"

def assert_dict_to_dut(dut: HierarchyObject, data: dict, fixed_point_max_error = 0.05) -> None:
    for attr, value in list(data.items()):
        dut_attr = dut.__getattr__(attr)
        if isinstance(value, dict) and isinstance(dut_attr, HierarchyObject):
            assert_dict_to_dut(dut_attr, value, fixed_point_max_error)
        elif isinstance(value, FixedPoint):
            assert_fp_error(FixedPoint(str(dut_attr.value), value.m, value.n, value.signed), value, fixed_point_max_error, attr)
        elif isinstance(value, str):
            assert str(dut_attr.value) == value
        elif isinstance(value, int):
            for c in str(dut_attr.value):
                if c != '0' and c != '1':
                    assert False, f"dut_attr.value is not a binary (or maybe you just forgot to do await rising_edge). Not supported. dut_attr.value={str(dut_attr.value)}" 

            assert int(str(dut_attr.value), base=2) == value, f"values of {attr=} are not equal ({str(dut_attr.value)} != {value})"
        else:
            assert False, f"This value type is not supported (type(value) == {type(value)})" 

    return


@dataclass
class Vec3:
    x: FixedPoint
    y: FixedPoint
    z: FixedPoint

    def __init__(self, x, y, z):
        self.x = fixed_t(x)
        self.y = fixed_t(y)
        self.z = fixed_t(z)

    @staticmethod
    def from_json(d: dict[str, float]):
        return Vec3(fixed_t(d["x"]), fixed_t(d["y"]), fixed_t(d["z"]))

    def to_vhd(self):
        return f'(x => "{self.x.fp_str}", y => "{self.y.fp_str}", z => "{self.z.fp_str}")'

    def to_rgb(self):
        def to_8_bits(x: float):
            x = min(x, 1.0)
            x = max(x, 0)
            x = round(x * 255)
            return bin(x)[2:].zfill(8)

        return f'("{to_8_bits(self.x)}", "{to_8_bits(self.y)}", "{to_8_bits(self.z)}")'
    
    def to_bytes(self) -> list[str]:
        return [*fixed_t_to_bytes(self.x), *fixed_t_to_bytes(self.y), *fixed_t_to_bytes(self.z)]
    
    @staticmethod
    def from_bytes(bytes: list[str]) -> "Vec3":
        assert len(bytes) == 9
        return Vec3(x = fixed_t_from_bytes(bytes[0:3]), 
                    y = fixed_t_from_bytes(bytes[3:6]),
                    z = fixed_t_from_bytes(bytes[6:])
                )

    @staticmethod
    def zero() -> "Vec3":
        return Vec3(fixed_t(0), fixed_t(0), fixed_t(0))

@dataclass
class Ray:
    origin: Vec3
    direction: Vec3

    @staticmethod
    def from_json(d: dict[str, Any]):
        return Ray(Vec3.from_json(d["origin"]), Vec3.from_json(d["direction"]))

    def to_bytes(self) -> list[str]:
        return [*self.origin.to_bytes(), *self.direction.to_bytes()]
    
@dataclass
class Triangle: 
    x: Vec3
    y: Vec3
    z: Vec3
    normal: Vec3

    def to_bytes(self) -> list[str]:
        return [*self.x.to_bytes(), *self.y.to_bytes(), *self.z.to_bytes(), *self.normal.to_bytes()]

    @staticmethod
    def from_bytes(bytes: list[str]) -> "Triangle":
        assert len(bytes) == 36
        return Triangle(
            x = Vec3.from_bytes(bytes[0:9]),
            y = Vec3.from_bytes(bytes[9:18]),
            z = Vec3.from_bytes(bytes[18:27]),
            normal = Vec3.from_bytes(bytes[27:]),
        )

    @staticmethod
    def from_json(d: dict[str, Any]):
        return Triangle(
            Vec3.from_json(d["x"]), 
            Vec3.from_json(d["y"]), 
            Vec3.from_json(d["z"]), 
            Vec3.from_json(d["normal"]),
        )

    
    def to_64bits(self):
        out = [
            self.x.x.fp_str + self.x.y.fp_str,
            self.x.z.fp_str + self.y.x.fp_str,
            
            self.y.y.fp_str + self.y.z.fp_str,
            self.z.x.fp_str + self.z.y.fp_str,
            
            self.z.z.fp_str + self.normal.x.fp_str,
            self.normal.y.fp_str + self.normal.z.fp_str,
        ]
        
        return out
    
    def to_vhd(self):
        out = ""
        out += f'x => (x => "{self.x.x.fp_str}", y => "{self.x.y.fp_str}", z => "{self.x.z.fp_str}"), \n'
        out += f'y => (x => "{self.y.x.fp_str}", y => "{self.y.y.fp_str}", z => "{self.y.z.fp_str}"), \n'
        out += f'z => (x => "{self.z.x.fp_str}", y => "{self.z.y.fp_str}", z => "{self.z.z.fp_str}"), \n'
        out += f'normal => (x => "{self.normal.x.fp_str}", y => "{self.normal.y.fp_str}", z => "{self.normal.z.fp_str}") \n'
        return out
    
    @staticmethod
    def zero() -> "Triangle":
        return Triangle(Vec3.zero(), Vec3.zero(), Vec3.zero(), Vec3.zero())

@dataclass
class HitInfo:
    tri_index: int
    t: FixedPoint # fixed_t
    
    @staticmethod
    def from_json(d: dict[str, Any]):
        return HitInfo(
            0,
            fixed_t(d["t"])
        )

def dut_Vec3_str(dut_vec: Any):
    return f"{fixed_t(str(dut_vec.x))} {fixed_t(str(dut_vec.y))} {fixed_t(str(dut_vec.z))}"

def Vec3_from_glm(v: glm.vec3):
    return Vec3(fixed_t(v.x), fixed_t(v.y), fixed_t(v.z))

from cocotb import log

def has_only_0_1(s: str):
    for c in s:
        if c != '0' and c != '1':
            return False
        
    return True

def create_dict_from_record(record) -> dict:
    d = {}
    for member in dir(record):
        attr = getattr(record, member)
        if isinstance(attr, HierarchyObject):
            d[member] = create_dict_from_record(attr)
        elif isinstance(attr, ModifiableObject):
            if len(str(attr.value)) == len(fixed_t(0).fp_str) and has_only_0_1(str(attr.value)):
                d[member] = str(attr.value) + f" ({fixed_t(str(attr.value))})"
            else:  
                d[member] = str(attr.value)


    return d

def format_record(record) -> str:
    if isinstance(record, ModifiableObject):
        if len(str(record.value)) == len(fixed_t(0).fp_str) and has_only_0_1(str(record.value)):
            return str(record.value) + f" ({fixed_t(str(record.value))})"
        else:  
            return str(record.value)
    d = create_dict_from_record(record)
    return pprint.pformat(d)
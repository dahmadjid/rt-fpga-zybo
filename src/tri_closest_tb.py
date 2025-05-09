from dataclasses import asdict, dataclass
import json
import cocotb
from cocotb import log
from cocotb.handle import HierarchyObject
from cocotb.triggers import Timer
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from glm import vec3

from camera import Camera
from obj import load_mesh
from src.test_utils import HitInfo, Ray, Triangle, Vec3_from_glm, assign_dict_to_dut, fixed_t, format_record

@dataclass
class Input:
    ray: Ray
    triangle: Triangle
    done_in: int
    tri_index: int
    @staticmethod 
    def from_json(d: dict):
        return Input(
            Ray.from_json(d["ray"]), 
            Triangle.from_json(d["triangle"]), 
            d["done_in"],
            0,
        )

@dataclass
class Output:
    any_hit: int
    closest_hit_info: HitInfo
    done_out: int

@cocotb.test() # type: ignore
async def test(dut: HierarchyObject):
    tris = load_mesh("../test.obj", vec3())
    cocotb.start_soon(Clock(dut.clk, 20, "ns").start())
    results = []
    camera = Camera(12, 12, vec3(-8.2, 0, -0.94), 0.0, -4.5, 45)
    debug = {}

    for ray_index in range(len(camera.ray_directions)):
        log.info(f"{ray_index=}")
        debug[ray_index] = []
        dut.clr.value = 0
        dut.rst.value = 0
        await RisingEdge(dut.clk)
        dut.clr.value = 1
        await RisingEdge(dut.clk)
        dut.rst.value = 1
                
        for tri_index in range(len(tris)):
            pipeline_delay = 0
            input_data = Input(
                ray = Ray(origin = Vec3_from_glm(camera.position), direction = Vec3_from_glm(camera.ray_directions[ray_index])),
                done_in=0 if tri_index != (len(tris) - 1) else 1,
                triangle=tris[tri_index],
                tri_index=tri_index,
            )
            assign_dict_to_dut(dut, asdict(input_data))
            await RisingEdge(dut.clk)

        i = 0
        while True:
            await RisingEdge(dut.clk)
            log.info(f"================== CYCLE {i} ({pipeline_delay=}) ==================")
            i += 1
            if dut.done_out.value != 1:
                pipeline_delay += 1
                debug[ray_index].append({
                    "hit": bool(dut.hit.value), 
                    "hit_info.t": fixed_t(str(dut.hit_info.t.value)), 
                    "hit_info.tri_index": int(str(dut.hit_info.tri_index), 2), 
                    "rst_out": bool(dut.rst_out.value), 
                    "any_hit": bool(dut.any_hit.value), 
                    "closest_hit_info.t": fixed_t(str(dut.closest_hit_info.t.value)), 
                    "closest_hit_info.tri_index": int(str(dut.closest_hit_info.tri_index), 2), 
                })
            else:
                results.append((bool(dut.any_hit.value), fixed_t(str(dut.closest_hit_info.t)), int(str(dut.closest_hit_info.tri_index), 2)))
                print("hit", dut.any_hit)
                print("t", fixed_t(str(dut.closest_hit_info.t)))
                break

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
    
    for i, res in enumerate(results):
        if res[0]:
            camera.image[i] = color(res[2])
        else:
            camera.image[i] = vec3() 
    with open("debug.json", "w") as f:
        json.dump(debug, f)

    camera.save_image_ppm(f"tri_closest.ppm")

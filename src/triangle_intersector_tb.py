from dataclasses import asdict, dataclass
import json
import os
import cocotb
from cocotb import log
from cocotb.handle import HierarchyObject
from cocotb.triggers import Timer
from cocotb.clock import Clock
from glm import vec3
from camera import Camera
from obj import load_mesh
from src.test_utils import Vec3, Vec3_from_glm, assert_dict_to_dut, assign_dict_to_dut, Ray, Triangle, HitInfo, fixed_t, format_record
from cocotb.triggers import RisingEdge

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
    hit: int
    hit_info: HitInfo
    done_out: int
    @staticmethod 
    def from_json(d: dict):
        return Output(d["hit"], HitInfo.from_json(d["hit_info"]), d["done_out"])

# @cocotb.test() # type: ignore
# async def test(dut: HierarchyObject):
#     tris = load_mesh("../test.obj", vec3(0.1, 0, 0))
#     cocotb.start_soon(Clock(dut.clk, 20, "ns").start())
#     for tri_index in range(len(tris)):
#         results = []
#         camera = Camera(32, 32, vec3(-8.2, 0, -0.94), 0.0, -4.5, 45)
#         for ray_index in range(len(camera.ray_directions)):
#             log.info(f"{ray_index=}")
#             dut.clr.value = 0
#             dut.rst.value = 0
#             await RisingEdge(dut.clk)
#             dut.clr.value = 1
#             dut.rst.value = 1
            
#             pipeline_delay = 0
#             input_data = Input(
#                 ray = Ray(origin = Vec3_from_glm(camera.position), direction = Vec3_from_glm(camera.ray_directions[ray_index])),
#                 done_in=1,
#                 triangle=tris[tri_index],
#                 tri_index=0,
#             )
#             assign_dict_to_dut(dut, asdict(input_data))
#             i = 0
#             while True:
#                 await RisingEdge(dut.clk)
#                 log.info(f"================== CYCLE {i} ({pipeline_delay=}) ==================")
#                 i += 1
#                 if dut.rst_out.value != 1:
#                     pipeline_delay += 1
#                 else:
#                     results.append((bool(dut.hit.value), fixed_t(str(dut.hit_info.t))))
#                     print("hit", dut.hit)
#                     print("done_out", dut.done_out)
#                     print("t", fixed_t(str(dut.hit_info.t)))
#                     break

#         for i, res in enumerate(results):
#             if res[0]:
#                 camera.image[i] = vec3(255)
#             else:
#                 camera.image[i] = vec3() 

#         camera.save_image_ppm(f"tri_{tri_index}.ppm")

@cocotb.test() # type: ignore
async def test(dut: HierarchyObject):
    with open("./tri_intersector_test_data.json") as f:
        test_data = json.load(f)
    cocotb.start_soon(Clock(dut.clk, 20, "ns").start())
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    pipeline_delay = 0
    for i, test in enumerate(test_data):
        input_data = Input.from_json({**test["input"], "done_in": 1})

        if i == 0:
            input_data = Input(
                ray = Ray(origin = Vec3(-8.1999998, 0, -0.94), direction = Vec3(1.0053048, -0.120812304, 0.009252384)),
                done_in=1,
                triangle=Triangle(
                    x=Vec3(-1.000000, -1.000000, 1.000000),
                    y=Vec3(-1.000000, 1.000000, 0.000000),
                    z=Vec3(-1.000000, -1.000000, -1.000000),
                    normal=Vec3(-1.0000, 0.0000, 0.0000),
                ),
                tri_index=0,
            )
        assign_dict_to_dut(dut, asdict(input_data))
        dut.rst.value = 1
        await RisingEdge(dut.clk)
        log.info(f"================== CYCLE {i} ({pipeline_delay=}) ==================")
        print(i, dut.done_out, dut.rst_out)
        # # log.info(f"{format_record(dut.stage_1_out)}")
        # # log.info(f"{format_record(dut.stage_2_out)}")
        # # log.info(f"{format_record(dut.reciprocal_out_data_d)}")
        # try:
        #     # print(f"{fixed_t(str(dut.Nd1.x.value))=}, {fixed_t(str(dut.Nd1.y.value))=}, {fixed_t(str(dut.Nd1.z.value))=}")
        #     print(f"{fixed_t(str(dut.Nd2.x.value))=}, {fixed_t(str(dut.Nd2.y.value))=}, {fixed_t(str(dut.Nd2.z.value))=}")
        #     # print(f"{fixed_t(str(dut.Nd3.x.value))=}, {fixed_t(str(dut.Nd3.y.value))=}, {fixed_t(str(dut.Nd3.z.value))=}")
        #     print("t", fixed_t(str(dut.hit_info.t)))
        # except:
        #     pass

        if dut.rst_out.value != 1:
            pipeline_delay += 1
            print(f"{dut.stage_2.hit}")
            print(f"{dut.stage_3.hit}")
            print(f"{dut.stage_7.hit}")
        else:
            output_data = Output.from_json({**test_data[i - pipeline_delay]["output"], "done_out": 1})
            if i - pipeline_delay == 0:
                output_data = Output(hit=True, hit_info=HitInfo(0, fixed_t(7.1620069)), done_out=1)
            print("hit=", dut.hit, "expected=",output_data.hit)
            print("t=", fixed_t(str(dut.hit_info.t.value)), "expected=",output_data.hit_info.t)
            break
            if dut.hit == output_data.hit:
                if output_data.hit == 1:
                    assert_dict_to_dut(dut, asdict(output_data), 0.015)
                continue
            else:
                # y [-1, 1, 0]
                # C1 [0, -1.86525857, -0.87373435]

                assert(False)
            print("done_out", dut.done_out, output_data.done_out)
            print("t", fixed_t(str(dut.hit_info.t)), output_data.hit_info.t)

    delayed_result_start_index = len(test_data) - pipeline_delay  
    for i in range(pipeline_delay):
        await RisingEdge(dut.clk)
        print(f"================== CYCLE {99 + i} ==================")
        output_data = Output.from_json( {**test_data[delayed_result_start_index + i]["output"], "done_out": 1})
        print("hit", dut.hit, output_data.hit)
        if dut.hit == output_data.hit:
            if dut.hit == 1:
                assert_dict_to_dut(dut, asdict(output_data), 0.015)
            continue
        else:
            assert(False)
        print("===========================", i)
        print("done_out", dut.done_out, output_data.done_out)
        print("hit_pos.x", fixed_t(str(dut.hit_info.hit_pos.x)), output_data.hit_info.hit_pos.x)
        print("hit_pos.y", fixed_t(str(dut.hit_info.hit_pos.y)), output_data.hit_info.hit_pos.y)
        print("hit_pos.z", fixed_t(str(dut.hit_info.hit_pos.z)), output_data.hit_info.hit_pos.z)
        print("normal.x", fixed_t(str(dut.hit_info.normal.x)), output_data.hit_info.normal.x)
        print("normal.y", fixed_t(str(dut.hit_info.normal.y)), output_data.hit_info.normal.y)
        print("normal.z", fixed_t(str(dut.hit_info.normal.z)), output_data.hit_info.normal.z)
        print("material", dut.hit_info.material, output_data.hit_info.material)
        print("t", fixed_t(str(dut.hit_info.t)), output_data.hit_info.t)
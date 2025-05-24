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
from src.test_utils import HitInfo, Ray, Triangle, Vec3, Vec3_from_glm, assign_dict_to_dut, fixed_t, format_record

@dataclass
class Input:
    ray: Ray

@dataclass
class Output:
    hit: int
    hit_info: HitInfo
    done_out: int

@cocotb.test() # type: ignore
async def test(dut: HierarchyObject):
    tris = load_mesh("../test2.obj", vec3())
    ray = Ray(origin=Vec3(x=-11.0, y=0.0, z=-2.0), direction=Vec3(x=0.9891266226768494, y=-0.0744289979338646, z=0.15701913833618164))
    test_data = [
        {
            "input": Input(
                ray = ray,
            ),
            "output": Output(
                done_out=0,
                hit=1,
                hit_info=HitInfo(
                    t=13.30,
                    tri_index=0,
                )
            )
        },
        {
            "input": Input(
                ray = ray,
            ),
            "output": Output(
                done_out=1,
                hit=0,
                hit_info=HitInfo(
                    t=12,
                    tri_index=1,
                )
            )
        }
    ]

    cocotb.start_soon(Clock(dut.clk, 20, "ns").start())
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    pipeline_delay = 0
    # for i, test in enumerate(test_data):
    input_data = test_data[0]["input"]
    assign_dict_to_dut(dut, asdict(input_data))
    #     dut.rst.value = 1
    #     await RisingEdge(dut.clk)
    #     log.info(f"================== CYCLE {i} ({pipeline_delay=}) ==================")
    #     pipeline_delay += 1
    #     log.info(f"{str(dut.current_tri_index.value)=} {str(dut.ram_q.value)}")
    #     log.info(f"{str(dut.hit_info.tri_index.value)=}")
    dut.rst.value = 1
        
    output_index = 0
    i = 0
    while True:
        log.info(f"================== CYCLE {i} ({pipeline_delay=}) ==================")
        log.info(f"{str(dut.intersector_rst.value)} {str(dut.current_tri_index.value)=} {str(dut.ram_q.value)[:10]}")
        log.info(f"{str(dut.hit_info.tri_index.value)=}")

        if dut.rst_out.value != 1:
            pipeline_delay += 1
        elif dut.intr_done_out.value == 1:
            break
            # output_data = test_data[output_index]["output"]
            # output_index += 1
            # print("hit=", dut.hit, "expected=", output_data.hit)
            # print("t=", fixed_t(str(dut.hit_info.t.value)), "expected=",output_data.hit_info.t)
            # print(f"{dut.done_out.value=}")
            # if output_index == 2:
            #     break
            # if dut.hit == output_data.hit:
            #     if output_data.hit == 1:
            #         assert_dict_to_dut(dut, asdict(output_data), 0.015)
            #     continue
            # else:
            #     assert(False)
        await RisingEdge(dut.clk)
        i += 1
        

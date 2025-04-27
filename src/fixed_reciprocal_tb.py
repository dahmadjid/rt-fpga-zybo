from dataclasses import asdict, dataclass
import json
import cocotb
from cocotb.handle import HierarchyObject
from cocotb.triggers import Timer
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import random

from src.test_utils import fixed_t


@cocotb.test() # type: ignore
async def test(dut: HierarchyObject):
    cocotb.start_soon(Clock(dut.clk, 20, "ns").start())
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    pipeline_delay = 0
    tests = []
    step = 1 / (64*1024*1024)
    for i in range(1, 100):
        random_ = int((max(random.random(), 0.1)) * 65535)
        tests.append(i * random_ * step * 10)


    for i, test in enumerate(tests):
        dut.rst.value = 1
        dut.input_data = fixed_t(test).bin_value
        await RisingEdge(dut.clk)
    
        print(f"================== CYCLE {i} ==================")
        # print(i, dut.out_rst, dut.input_data, dut.output_data)

        if dut.out_rst.value == 0:
            pipeline_delay += 1
        else:
            input_data = tests[i - pipeline_delay] 
            print(f"{dut.output_data.value=} {fixed_t(str(dut.output_data.value))} | {input_data=} {1/input_data=} {fixed_t(input_data).fp_str}")


    print(f"{pipeline_delay=}")
    for i in range(pipeline_delay):
        print(f"================== CYCLE {len(tests) + i} ==================")
        await RisingEdge(dut.clk)
        input_data = tests[len(tests) + i - pipeline_delay]
        print(f"{dut.output_data.value=} {fixed_t(str(dut.output_data.value))} | {input_data=} {1/input_data=} {fixed_t(input_data).fp_str}")
        
    # delayed_result_start_index = len(test_data) - pipeline_delay  
    # for i in range(pipeline_delay):
    #     await RisingEdge(dut.clk)
    #     print(f"================== CYCLE {99 + i} ==================")
    #     output_data = Output.from_json( {**test_data[delayed_result_start_index + i]["output"], "done_out": 1})
    #     print("hit", dut.hit, output_data.hit)
    #     if dut.hit == output_data.hit:
    #         if dut.hit == 1:
    #             assert_dict_to_dut(dut, asdict(output_data), 0.02)
    #         continue

    #     print("===========================", i)
    #     print("done_out", dut.done_out, output_data.done_out)
    #     print("hit_pos.x", sfixed_l(str(dut.hit_info.hit_pos.x)), output_data.hit_info.hit_pos.x)
    #     print("hit_pos.y", sfixed_l(str(dut.hit_info.hit_pos.y)), output_data.hit_info.hit_pos.y)
    #     print("hit_pos.z", sfixed_l(str(dut.hit_info.hit_pos.z)), output_data.hit_info.hit_pos.z)
    #     print("normal.x", sfixed_s(str(dut.hit_info.normal.x)), output_data.hit_info.normal.x)
    #     print("normal.y", sfixed_s(str(dut.hit_info.normal.y)), output_data.hit_info.normal.y)
    #     print("normal.z", sfixed_s(str(dut.hit_info.normal.z)), output_data.hit_info.normal.z)
    #     print("material", dut.hit_info.material, output_data.hit_info.material)
    #     print("t", sfixed_s(str(dut.hit_info.t)), output_data.hit_info.t)

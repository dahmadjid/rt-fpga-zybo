import cocotb
from cocotb.handle import HierarchyObject
from cocotb.triggers import Timer
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from fixedpoint import FixedPoint
from src.test_utils import HitInfo, fixed_t


"""
entity closest_hit is
    port (
        clk: in std_logic;
        rst: in std_logic;
        data_valid: in std_logic;
        done_in: in std_logic;
        hit: in std_logic;
        hit_info: in HitInfo_t;

        done_out: out std_logic;
        any_hit: out std_logic;
        closest_hit_info: out HitInfo_t
    );
end closest_hit; 
"""
@cocotb.test() # type: ignore
async def test(dut: HierarchyObject):
    cocotb.start_soon(Clock(dut.clk, 16, "ns").start())
    
    data: list[tuple[FixedPoint, int]] = [(fixed_t(0.8), 1), (fixed_t(0.5), 1), (fixed_t(0.7), 1)]

    dut.rst.value = 0
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    for i, input in enumerate(data):
        dut.data_valid.value = 1
        dut.hit.value = input[1]
        dut.hit_info.t.value = input[0].bin_value
        dut.hit_info.tri_index.value = i
        if i == (len(data) - 1):
            dut.done_in = 1
        else:
            dut.done_in = 0
        print(i, input)
        await RisingEdge(dut.clk)

        print(dut.done_out, dut.any_hit, fixed_t(str(dut.closest_hit_info.t.value)), dut.closest_hit_info.tri_index)

    await RisingEdge(dut.clk)
    print(dut.done_out, dut.any_hit, fixed_t(str(dut.closest_hit_info.t.value)), dut.closest_hit_info.tri_index)
    await RisingEdge(dut.clk)
    print(dut.done_out, dut.any_hit, fixed_t(str(dut.closest_hit_info.t.value)), dut.closest_hit_info.tri_index)


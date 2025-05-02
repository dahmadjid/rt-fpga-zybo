import cocotb
from cocotb.handle import HierarchyObject
from cocotb.triggers import Timer
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from fixedpoint import FixedPoint
from src.test_utils import HitInfo, fixed_t, format_record


@cocotb.test() # type: ignore
async def test(dut: HierarchyObject):
    cocotb.start_soon(Clock(dut.clk, 16, "ns").start())
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    print(format_record(dut.tri))
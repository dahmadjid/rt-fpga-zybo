import asyncio
from dataclasses import asdict, dataclass
import json
import cocotb
from cocotb import log
from cocotb.handle import HierarchyObject
import cocotb.queue
from cocotb.triggers import Timer
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
import random
import cocotbext.uart as uart
from src.test_utils import Ray, Vec3, fixed_t, format_record

# clk: in std_logic;
# sw: in std_logic_vector(9 downto 0);
# key: in std_logic_vector(3 downto 0);
# ledr: out std_logic_vector(9 downto 0);
# uart_tx: out std_logic;
# uart_rx: in std_logic
def reverse(data: str):
    return "".join([data[- i - 1] for i in range(len(data))])

# async def uart_send_data(dut_tx, baudrate: int, data: str):
#     if len(data) != 8:
#         raise RuntimeError("uart len(data) != 8")
#     data = reverse(data)
#     dut_tx.setimmediatevalue(1) # start bit
#     await Timer(1/baudrate, units='sec', round_mode="round")
#     dut_tx.setimmediatevalue(0) # start bit
#     await Timer(1/baudrate, units='sec', round_mode="round")
#     for bit in data:
#         dut_tx.setimmediatevalue(int(bit))
#         await Timer(1/baudrate, units='sec', round_mode="round")
#     dut_tx.setimmediatevalue(1) # end bit
#     await Timer(1/baudrate, units='sec', round_mode="round")

async def uart_receving_data(uart_sink: uart.UartSink, queue):
#     oversampling = 2
    while True:
        data = await uart_sink.read()
        log.info(f"{data=}")
        await queue.put(data)

#         await FallingEdge(dut_rx) # start bit
#         for _ in range(oversampling):
#             await Timer(1_000_000/baudrate/oversampling, units='us', round_mode="round")

#         oversampled_data = ""
#         for _ in range(8 * oversampling):
#             await Timer(1_000_000/baudrate/oversampling, units='us', round_mode="round")
#             oversampled_data += str(dut_rx)
        
#         for _ in range(oversampling):
#             await Timer(1_000_000/baudrate/oversampling, units='us', round_mode="round")
        
#         stop_bit = dut_rx
#         assert str(stop_bit) == "1"
#         data = ""
#         for i in range(8):
#             bit = oversampled_data[i * oversampling]
#             for j in range(oversampling):
#                 if bit != oversampled_data[i * oversampling + j]:
#                     raise RuntimeError(f"Oversampling failed {oversampled_data} {i=} {j=} {len(oversampled_data)=}")
#             data += bit


#         log.info(f"received={int(reverse(data), 2)}")
#         await queue.put(reverse(data))


"""
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.0053048, -0.120812304, 0.009252384]} t 7.1620069
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.0053048, -0.13807119, 0.009252384]} t 7.1620069
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.0033692, -0.086294495, 0.026402391]} t 7.1758227
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.0033692, -0.103553399, 0.026402391]} t 7.1758227
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.0033692, -0.120812304, 0.026402391]} t 7.1758227
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.0033692, -0.13807119, 0.026402391]} t 7.1758227
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.00143349, -0.0517767, 0.043552414]} t 7.1896935
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.00143349, -0.069035605, 0.043552414]} t 7.1896935
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.00143349, -0.086294495, 0.043552414]} t 7.1896935
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.00143349, -0.103553399, 0.043552414]} t 7.1896935
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.00143349, -0.120812304, 0.043552414]} t 7.1896935
Ray{origin = [-8.1999998, 0, -0.94], direction = [1.00143349, -0.13807119, 0.043552414]} t 7.1896935
Ray{origin = [-8.1999998, 0, -0.94], direction = [0.99949789, -0.017258909, 0.06070242]} t 7.2036166
Ray{origin = [-8.1999998, 0, -0.94], direction = [0.99949789, -0.03451779, 0.06070242]} t 7.2036166
"""

@cocotb.test() # type: ignore
async def test(dut: HierarchyObject):
    queue = cocotb.queue.Queue()
    cocotb.start_soon(Clock(dut.clk, 8, "ns").start())
    await RisingEdge(dut.clk)
    dut.btn.value = 0xf
    await RisingEdge(dut.clk)
    dut.btn.value = 0x2
    await RisingEdge(dut.clk)
    # print("========================= WRITE TRIANGLE =========================")

    # await uart_send_data(dut.uart_rx, 115200, "00000001")
    # dut.uart_rx_buffer_index_in.value = 0
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")

    # await uart_send_data(dut.uart_rx, 115200, "00000011")
    # await RisingEdge(dut.clk)
    # dut.uart_rx_buffer_index_in.value = 0
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")
    # dut.uart_rx_buffer_index_in.value = 0

    # await uart_send_data(dut.uart_rx, 115200, "00000000")
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")

    # for i in range(47):
    #     await uart_send_data(dut.uart_rx, 115200, "00011000")
    # await uart_send_data(dut.uart_rx, 115200, "00000011")
    
    # dut.uart_rx_buffer_index_in.value = 0
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")
    # await RisingEdge(dut.clk)
    # await RisingEdge(dut.clk)
    # await RisingEdge(dut.clk)
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")
    
    # print("========================= READ TRIANGLE =========================")

    # await uart_send_data(dut.uart_rx, 115200, "00000010")
    # dut.uart_rx_buffer_index_in.value = 0
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")

    # await uart_send_data(dut.uart_rx, 115200, "00000011")
    # await RisingEdge(dut.clk)
    # dut.uart_rx_buffer_index_in.value = 1
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")
    # dut.uart_rx_buffer_index_in.value = 2

    # await uart_send_data(dut.uart_rx, 115200, "00000000")
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")


    # for i in range(48):
    #     print(f"received data {i}", await queue.get())
    
    # dut.uart_rx_buffer_index_in.value = 3
    # await RisingEdge(dut.clk)
    # print(f"{dut.state_out.value=} {dut.uart_rx_buffer_out.value=}")
    

# 'ray': {'direction': {'x': '000101010001000000000000 (337.0)',
# 'y': '000100011111111011111111 (287.937255859375)',
#     'z': '001001010000000000000000 (592.0)'},
# 'origin': {'x': '110011000111110011111111 (-824.1875)',
# 'y': '000000000000000000000000 (0.0)',
# 'z': '111101011111000011111111 (-160.9375)'}},

    log.info("========================= TRACE =========================")
    sink = uart.UartSink(dut.uart_tx, 921600)
    source = uart.UartSource(dut.uart_rx, 921600)
    await cocotb.start(uart_receving_data(sink, queue))

    await source.write(bytes([3]))
    await source.wait()
    log.info(f"{str(dut.uart_rx_data_out)=}")
    ray = Ray(origin = Vec3(-8.1999998, 0, -0.94), direction = Vec3(1.0053048, -0.120812304, 0.009252384))
    for byte in ray.to_bytes():
        log.info(f"{byte=}")
        await source.write(bytes([int(byte, 2)]))
        # await source.wait()
    log.info(f"{str(dut.led)=}")
    # for i in range(100000):
    #     if i > 24355:
    #         log.info(f"{i=} {format_record(dut.stage_2)}")
    #         log.info(f"{i=} {format_record(dut.out_hit_info)}")
    #     if fixed_t(str(dut.out_hit_info.t.value)) != 0:
    #         break
    #     await RisingEdge(dut.clk)
    
    expected_t = fixed_t(7.1620069)
    data = ""
    for i in range(3):
        khra: bytearray = await queue.get()
        log.info(f"{i=} {khra=}")
        data = bin(int(khra[0]))[2:].zfill(8) + data

    log.info(f"{expected_t.fp_str=}, {expected_t=}, {fixed_t(data)=}")
    
    for i in range(2):
        log.info(f"{i=}")
        print(f"received data {i}", await queue.get())
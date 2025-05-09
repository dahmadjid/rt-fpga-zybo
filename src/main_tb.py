from dataclasses import asdict, dataclass
import cocotb
from cocotb import log
from cocotb.handle import HierarchyObject
import cocotb.queue
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import cocotbext.uart as uart
from glm import vec3
from src.test_utils import Ray, Triangle, Vec3, Vec3_from_glm, fixed_t, format_record
from obj import load_mesh
from camera import Camera

async def uart_receving_data(uart_sink: uart.UartSink, queue):
    while True:
        data = await uart_sink.read()
        log.info(f"{data=}")
        await queue.put(data)

@cocotb.test() # type: ignore
async def test(dut: HierarchyObject):
    queue = cocotb.queue.Queue()
    cocotb.start_soon(Clock(dut.clk, 8, "ns").start())
    
    sink = uart.UartSink(dut.uart_tx, 921600)
    source = uart.UartSource(dut.uart_rx, 921600)
    # await cocotb.start(uart_receving_data(sink, queue))

    async def write_triangle(address: int, tri: Triangle):
        assert address < 2048 and address >= 0
        await source.write(bytes([1]))
        address_bytes = bytes([address & 0xff, (address & 0xff00) >> 8])
        await source.write(address_bytes)
        for byte in tri.to_bytes():
            await source.write(bytes([int(byte, 2)]))
        
    async def read_triangle(address: int):
        assert address < 2048 and address >= 0
        await source.write(bytes([2]))

        address_bytes = bytes([address & 0xff, (address & 0xff00) >> 8])
        await source.write(address_bytes)
        tri_bytes = ["" for _ in range(36)]
        for i in range(36):
            data = int((await queue.get())[0])
            tri_bytes[35 - i] = bin(data)[2:].zfill(8)
        return Triangle.from_bytes(tri_bytes)

    async def trace_ray(ray: Ray):
        await source.write(bytes([3]))
        for byte in ray.to_bytes():
            log.info(f"{byte=}")
            await source.write(bytes([int(byte, 2)]))
            await source.wait()
        t_data = ""
        for i in range(3):
            t_data = (bin(int((await sink.read(1))[0]))[2:].zfill(8)) + t_data

        index_data = ""
        for i in range(2):
            index_data = (bin(int((await sink.read(1))[0]))[2:].zfill(8)) + index_data

        return (fixed_t(t_data), int(index_data, 2))




    await RisingEdge(dut.clk)
    dut.btn.value = 0x1
    await RisingEdge(dut.clk)
    dut.btn.value = 0x0
    await RisingEdge(dut.clk)
    
    camera = Camera(5, 5, vec3(-8.2, 0, -0.94), 0.0, -4.5, 45)
    ray = Ray(origin=Vec3_from_glm(camera.position), direction=Vec3_from_glm(camera.ray_directions[0]))
    res = await trace_ray(ray)
    print(res)
    # await uart.write_triangle(0, tris[1])
    # tri = await uart.read_triangle(0)
    # print(tri)
    
    # # for i, direction in enumerate(camera.ray_directions):
    # ray = Ray(origin=Vec3_from_glm(camera.position), direction=Vec3_from_glm(camera.ray_directions[0]))
    # res = await trace_ray(ray)
    # if res[1] != 65535:
    #     log.info(f"0, {ray}, {res[0]}, {res[1]}")
    #     camera.image[0] = vec3(255)
    # else:
    #     camera.image[0] = vec3(0)

    # # camera.display_ppm()
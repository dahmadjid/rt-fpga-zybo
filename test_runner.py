import sys
from cocotb.runner import get_runner, get_results
from pathlib import Path
import os 
import tabulate
os.environ.setdefault("COCOTB_ANSI_OUTPUT", "1")

proj_path = Path(__file__).resolve().parent
src = proj_path / "src"
fphdl = proj_path / "fphdl"

runner = get_runner("questa")

fphdl_files=[
    fphdl / "fixed_float_types_c.vhd",
    fphdl / "fixed_pkg_c.vhd",
    fphdl / "float_pkg_c.vhd",
]
if os.path.exists("work"):
    os.system("rm -rf work")

os.chdir("src")

runner.build(
    vhdl_sources=fphdl_files,
    always=True,
    hdl_library="work",
    build_dir=".",
)
# force order
vhdl_sources = [
    src / "ray_tracer_pkg.vhd",
    src / "linear_algebra_pkg.vhd",
]

verilog_sources = [
]

files_to_exclude = [
    src / "ray_tracing_unit.vhd",
]


for file in list(src.rglob("*.vhd")):
    if not file in vhdl_sources and not file in files_to_exclude:
        vhdl_sources.append(file)

for file in list(src.rglob("*.v")):
    if not file in verilog_sources and not file in files_to_exclude:
        verilog_sources.append(file)

print(f"{vhdl_sources=} {verilog_sources=}")


runner.build(
    vhdl_sources=vhdl_sources,
    verilog_sources=verilog_sources,
    always=True,
    hdl_library="work",
    build_dir=".",
)

test_benches = list(src.rglob("*_tb.py"))
if len(sys.argv) > 1:
    filtered_tbs = []
    for tb in test_benches:
        if sys.argv[1] in str(tb):
            filtered_tbs.append(tb)
    test_benches = filtered_tbs
results = []

#Color
R = "\033[0;31;40m" #RED
G = "\033[0;32;40m" # GREEN
Y = "\033[0;33;40m" # Yellow
B = "\033[0;34;40m" # Blue
N = "\033[0m" # Reset

for tb in test_benches:
    if sys.platform == "win32":
        path = str(tb.relative_to(proj_path)).split("_tb.py")[0].split("\\")
    else:
        path = str(tb.relative_to(proj_path)).split("_tb.py")[0].split("/")

    res_path = runner.test(
        hdl_toplevel=path[-1], 
        test_module=".".join(path) + "_tb",
        hdl_toplevel_library="work",
        build_dir=".",
        test_dir=".",
        hdl_toplevel_lang="vhdl"
    )
    res = get_results(res_path)
    results.append(('.'.join(path) + "_tb", G + "PASS" + N if res[1] == 0 else R + "FAIL" + N , *res))
    
print()
print(tabulate.tabulate(results, headers=["Testbench", "","Total", "Failed"], tablefmt='orgtbl'))
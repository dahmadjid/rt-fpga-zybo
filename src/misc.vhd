-- this is to confirm that ram_q_to_triangle works correctly

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.ray_tracer_pkg.all;
use work.linear_algebra_pkg.all;
use work.fixed_pkg.all;

entity misc is
    port (
        clk: in std_logic;
        tri: out Triangle_t
    );
end entity;

architecture arch of misc is
    -- Triangle(x=Vec3(x=1.75, y=-1.0, z=1.0), y=Vec3(x=-1.0, y=1.0, z=0.0), z=Vec3(x=-1.0, y=-1.0, z=-1.0), normal=Vec3(x=-1.0, y=0.0, z=0.0))
    constant tri_bytes: std_logic_vector(287 downto 0) := "000000000001110000000000111111111110111111111111000000000001000000000000111111111110111111111111000000000001000000000000000000000000000000000000111111111110111111111111111111111110111111111111111111111110111111111111111111111110111111111111000000000000000000000000000000000000000000000000";
begin
    process(clk)
    begin
        if rising_edge(clk) then
            tri <= ram_q_to_triangle(tri_bytes);
        end if;
    end process;
end arch;
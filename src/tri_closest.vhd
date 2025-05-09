-- this is to confirm that triangle_intersector + closest_hit works correctly

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.ray_tracer_pkg.all;
use work.linear_algebra_pkg.all;
use work.fixed_pkg.all;

entity tri_closest is
    port (
        clk   : in std_logic;
        clr: in std_logic;
        rst : in std_logic;
        ray: in Ray_t;
        triangle: in Triangle_t;
        tri_index: in unsigned(15 downto 0);
        done_in: in std_logic;
        done_out: out std_logic;
        any_hit: out std_logic;
        closest_hit_info: out HitInfo_t
    );
end entity;

architecture arch of tri_closest is
    signal intr_done_out: std_logic := '0';
    signal rst_out: std_logic := '0';
    signal hit: std_logic := '0';
    signal hit_info: HitInfo_t := zero_hit_info;
begin

    intersector: component triangle_intersector
    port map(
        clk => clk,
        clr => clr,
        rst => rst,
        ray => ray,
        triangle => triangle,
        tri_index => tri_index,
        done_in => done_in,
        done_out => intr_done_out,
        hit => hit,
        hit_info => hit_info,
        rst_out => rst_out
    );

    closest_hit_inst: component closest_hit
    port map(
        clk => clk,
        rst => rst,
        data_valid => rst_out,
        done_in => intr_done_out,
        hit_info =>  hit_info,
        hit => hit,
        
        done_out => done_out,
        any_hit => any_hit,
        closest_hit_info => closest_hit_info
    );
end arch;
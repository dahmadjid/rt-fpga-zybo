library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.fixed_pkg.all;
use work.ray_tracer_pkg.all;

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

architecture arch of closest_hit is
    signal reg_any_hit : std_logic := '0';
    signal reg_done : std_logic := '0';
    signal reg_closest_hit_info: HitInfo_t := zero_hit_info; 
begin

    any_hit <= reg_any_hit;
    closest_hit_info <= reg_closest_hit_info;
    done_out <= reg_done;

    main_process: process(clk, rst, data_valid, done_in, hit_info, hit)
    begin
        if rst = '0' then
            reg_any_hit <= '0';
            reg_closest_hit_info <= zero_hit_info;
            reg_done <= '0';
        elsif rising_edge(clk) then 
            if data_valid = '1' and reg_done = '0' then
                reg_done <= done_in;
                if hit = '1' then
                    reg_any_hit <= '1';
                    if hit_info.t < reg_closest_hit_info.t then
                        reg_closest_hit_info <= hit_info;
                    end if; 
                end if;
            end if;
        end if;
    end process;
end architecture;

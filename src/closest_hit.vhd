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
    type stage_1_t is record
        data_valid: std_logic;
        done_in: std_logic;
        hit: std_logic;
        hit_info: HitInfo_t;
        new_hit_info_closer: std_logic; 
    end record;

    constant zero_stage_1: stage_1_t := (
        data_valid => '0',
        done_in => '0',
        hit => '0',
        hit_info => zero_hit_info,
        new_hit_info_closer => '0'
    );

    signal stage_1: stage_1_t := zero_stage_1;
begin

    any_hit <= reg_any_hit;
    closest_hit_info <= reg_closest_hit_info;
    done_out <= reg_done;

    main_process: process(clk, rst, data_valid, done_in, hit_info, hit, reg_closest_hit_info, reg_done, reg_any_hit)
        variable temp: std_logic := '0';
    begin
        if rst = '0' then
            reg_any_hit <= '0';
            reg_closest_hit_info <= zero_hit_info;
            reg_done <= '0';
            stage_1 <= zero_stage_1;
        elsif rising_edge(clk) then
            -- reg_done <= data_valid and done_in;
            -- if data_valid = '1' and reg_done = '0' then
            --     if hit = '1' then
            --         reg_any_hit <= '1';
            --         if hit_info.t < reg_closest_hit_info.t then
            --             reg_closest_hit_info <= hit_info;
            --         end if; 
            --     end if;
            -- end if;
            -- this if means:
            -- if the value in stage_1.hit_info.t is going to get assigned, then we should compare with that because thats smaller than 
            -- the current reg_closest_hit_info.
            -- if its not going to get assigned, therefore we compare with reg_closest_hit_info_t
            -- to check if its assigned, we check all the required flags in stage_1 + stage_1.new_hit_info_closer in stage_1 which says that
            -- stage_1.hit_info.t is smaller than reg_closest_hit_info.t
            if stage_1.new_hit_info_closer = '1' and stage_1.data_valid = '1' and reg_done = '0' and stage_1.hit = '1' then
                if hit_info.t < stage_1.hit_info.t then 
                    temp := '1';
                else
                    temp := '0';
                end if;
            else
                if hit_info.t < reg_closest_hit_info.t then 
                    temp := '1';
                else
                    temp := '0';
                end if;
            end if;
            stage_1 <= (
                data_valid => data_valid,
                done_in => done_in,
                hit => hit,
                hit_info => hit_info,
                new_hit_info_closer => temp
            );

            -- delay the output by 1 clk to allow for the comparison operation

            if stage_1.data_valid = '1' and reg_done = '0' then
                reg_done <= stage_1.done_in;
                if stage_1.hit = '1' then
                    reg_any_hit <= '1';
                    if stage_1.new_hit_info_closer = '1' then
                        reg_closest_hit_info <= stage_1.hit_info;
                    end if; 
                end if;
            end if;
        end if;
    end process;
end architecture;

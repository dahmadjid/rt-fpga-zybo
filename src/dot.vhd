library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.ray_tracer_pkg.all;
use work.linear_algebra_pkg.all;
use work.fixed_pkg.all;

entity dot is 
    port(
        signal clk: in std_logic; 
        signal v1: in vec3;
        signal v2: in vec3; 
        signal ret: out fixed_t
    );
end entity;

architecture arch of dot is
    signal temp1: fixed_t := (others => '0');
    signal temp2: fixed_t := (others => '0');
    signal temp3: fixed_t := (others => '0');
    signal temp4: fixed_t := (others => '0');
    signal temp5: fixed_t := (others => '0');
    signal ret_reg: fixed_t := (others => '0');
begin
    ret <= ret_reg;

    process(clk)
    begin
        if rising_edge(clk) then
            -- cycle 1
            temp1 <= to_fixed_t(v1.x * v2.x);
            temp2 <= to_fixed_t(v1.y * v2.y);
            temp3 <= to_fixed_t(v1.z * v2.z);
    
            -- cycle 2
            temp4 <= to_fixed_t(temp1 + temp2);
            temp5 <= temp3;

            -- cycle 3
            ret_reg <= to_fixed_t(temp4 + temp5);
        end if;
    end process;
end arch;
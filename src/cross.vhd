library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.ray_tracer_pkg.all;
use work.linear_algebra_pkg.all;
use work.fixed_pkg.all;

entity cross is 
    port(
        signal clk: in std_logic; 
        signal v1: in vec3;
        signal v2: in vec3; 
        signal ret: out vec3
    );
end entity;

architecture arch of cross is
    signal temp1: sfixed(23 downto -24) := (others => '0');
    signal temp2: sfixed(23 downto -24) := (others => '0');
    signal temp3: sfixed(23 downto -24) := (others => '0');
    signal temp4: sfixed(23 downto -24) := (others => '0');
    signal temp5: sfixed(23 downto -24) := (others => '0');
    signal temp6: sfixed(23 downto -24) := (others => '0');
    signal ret_reg: vec3 := zero_vec3;
begin
    ret <= ret_reg;

    process(clk)
    begin
        if rising_edge(clk) then
            -- cycle 1
            temp1 <= v1.y * v2.z;
            temp2 <= v1.z * v2.y;
            temp3 <= v1.z * v2.x;
            temp4 <= v1.x * v2.z;
            temp5 <= v1.x * v2.y;
            temp6 <= v1.y * v2.x;
        
            -- cycle 2
            ret_reg.x <= to_fixed_t(temp1 - temp2);
            ret_reg.y <= to_fixed_t(temp3 - temp4);
            ret_reg.z <= to_fixed_t(temp5 - temp6);
        end if;
    end process;
end arch;
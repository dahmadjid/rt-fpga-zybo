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
        rst : in std_logic;
        ray: in Ray_t;
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
    signal done_in: std_logic := '0';
    signal intersector_rst: std_logic := '0';
    signal current_triangle: Triangle_t := zero_triangle;
    signal current_tri_index: unsigned(15 downto 0) := (others => '0');
    constant last_tri_index: unsigned(15 downto 0) := x"0001";
    -- RAM --
    signal ram_data: std_logic_vector(287 downto 0) := (others => '0'); 
    signal ram_q: std_logic_vector(287 downto 0) := (others => '0'); 
    signal ram_wren: std_logic := '0';
    signal ram_address: std_logic_vector(8 downto 0) := (others => '0');

    signal state: integer := 0;
begin

    current_triangle <= ram_q_to_triangle(ram_q);
    done_in <= '1' when (current_tri_index = last_tri_index) else '0';

    process(clk, rst)
    begin
        if rst = '0' then
            intersector_rst <= '0';
            ram_address <= (others => '0');
            state <= 0;
            ram_wren <= '0';
        elsif rising_edge(clk) then
            if state = 0 or state = 1 then
                if done_in = '0' then
                    current_tri_index <= "0000000" & unsigned(ram_address);
                    ram_address <= std_logic_vector(unsigned(ram_address) + 1);
                end if;
                state <= 1;
                intersector_rst <= '1';

                if intersector_rst = '1' and intr_done_out = '1' then
                    intersector_rst <= '0';
                    state <= 2;
                end if;
            end if;
        end if;    
    end process;

    ram_b: component ram
    generic map (
        DATA_WIDTH => 288,
        ADDR_WIDTH => 9,
        INIT_DATA_FILE => "ram.data"
    )
    port map(
        clk => clk,
        we => ram_wren,
        a => ram_address,
        di => ram_data,
        dout => ram_q
    );

    intersector: component triangle_intersector
    port map(
        clk => clk,
        clr => rst,
        rst => intersector_rst,
        ray => ray,
        triangle => current_triangle,
        tri_index => current_tri_index,
        done_in => done_in,
        done_out => intr_done_out,
        hit => hit,
        hit_info => hit_info,
        rst_out => rst_out
    );

    -- closest_hit_inst: component closest_hit
    -- port map(
    --     clk => clk,
    --     rst => clr,
    --     data_valid => rst_out,
    --     done_in => intr_done_out,
    --     hit_info =>  hit_info,
    --     hit => hit,
        
    --     done_out => done_out,
    --     any_hit => any_hit,
    --     closest_hit_info => closest_hit_info
    -- );
end arch;
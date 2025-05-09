library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.ray_tracer_pkg.all;
use work.linear_algebra_pkg.all;
use work.fixed_pkg.all;

entity fixed_reciprocal is
    port (
        clk   : in std_logic;
        rst : in std_logic;
        input_data: in fixed_t;
        out_rst: out std_logic;
        output_data: out fixed_t
    );
end entity;

architecture arch of fixed_reciprocal is
    signal q_0_1: std_logic_vector(23 downto 0);
    signal q_1_7: std_logic_vector(23 downto 0);
    signal q_8: std_logic_vector(23 downto 0);
    signal negative_input_data: fixed_t;
    signal selected_input_data: fixed_t;
    type input_range_t is (r0_1, r1_7, r8);
    signal selected_input_range : input_range_t;

    type stage_2_t is record
        input_data: fixed_t;
        original_sign_bit: std_logic; 
        input_range: input_range_t;
        rst: std_logic;
    end record;
    
    type stage_3_t is record
        original_sign_bit: std_logic; 
        input_range: input_range_t;
        rst: std_logic;
    end record;

    type stage_4_t is record 
        original_sign_bit: std_logic; 
        input_range: input_range_t;
        rst: std_logic;
    end record;


    constant zero_stage_2 : stage_2_t := (
        input_data => (others => '0'), 
        original_sign_bit => '0', 
        input_range => r0_1,
        rst => '0'
    );

    constant zero_stage_3 : stage_3_t := (
        original_sign_bit => '0', 
        input_range => r0_1,
        rst => '0'
    );

    constant zero_stage_4 : stage_4_t := (
        original_sign_bit => '0', 
        input_range => r0_1,
        rst => '0'
    );

    signal stage_2: stage_2_t := zero_stage_2;
    signal stage_3: stage_3_t := zero_stage_3;
    signal stage_4: stage_4_t := zero_stage_4;

    signal lookup_address: std_logic_vector(11 downto 0) := (others => '0');
    signal lookup_output: std_logic_vector(23 downto 0) := (others => '0');
begin
    negative_input_data <= not input_data;
    selected_input_data <= input_data when input_data(11) = '0' else negative_input_data;
    selected_input_range <= r0_1 when selected_input_data(11 downto 0) = x"000" else 
                            r1_7 when selected_input_data(11 downto 3) = x"00" & '0' else r8;

    out_rst <= stage_4.rst;
    output_data <= fixed_t(lookup_output) when stage_4.original_sign_bit = '0' else not fixed_t(lookup_output);

    lookup0_1_inst: rom
    generic map(
        ADDR_WIDTH => 12,
        DATA_WIDTH => 24,
        INIT_DATA_FILE => "lookup0_1.data"
    )
    port map(
        a => lookup_address,
        clk => clk,
        dout => q_0_1
    );

    lookup1_7_inst: rom
    generic map(
        ADDR_WIDTH => 12,
        DATA_WIDTH => 24,
        INIT_DATA_FILE => "lookup1_7.data"
    )
    port map(
        a => lookup_address,
        clk => clk,
        dout => q_1_7
    );

    lookup8_inst: rom
    generic map(
        ADDR_WIDTH => 12,
        DATA_WIDTH => 24,
        INIT_DATA_FILE => "lookup8.data"
    )
    port map(
        a => lookup_address,
        clk => clk,
        dout => q_8
    );

    lookup_address <= to_slv(stage_2.input_data(-1 downto -12)) when stage_2.input_range = r0_1 else
                              to_slv(stage_2.input_data(2 downto -9)) when stage_2.input_range = r1_7 else
                              to_slv(stage_2.input_data(11 downto 0));

    lookup_output  <= q_0_1 when stage_4.input_range = r0_1 else
                      q_1_7 when stage_4.input_range = r1_7 else
                      q_8;

    main: process (clk, rst)
    begin
        if rising_edge(clk) then
            -- INPUT to STAGE 2 --
            if rst = '0' then
                stage_2 <= zero_stage_2;
            else
                stage_2 <= (
                    input_data => selected_input_data,
                    original_sign_bit => input_data(11),
                    input_range => selected_input_range,
                    rst => rst
                );
            end if;

            -- STAGE 2 to STAGE 3 --
            if stage_2.rst = '0' then
                stage_3 <= zero_stage_3;
            else
                stage_3.original_sign_bit <= stage_2.original_sign_bit;
                stage_3.input_range <= stage_2.input_range;
                stage_3.rst <= stage_2.rst;
            end if;

            -- STAGE 3 to STAGE 4 --
            if stage_3.rst = '0' then
                stage_4 <= zero_stage_4;
            else
                stage_4.original_sign_bit <= stage_3.original_sign_bit;
                stage_4.input_range <= stage_3.input_range;
                stage_4.rst <= stage_3.rst;
            end if;
        end if;
    end process;
end arch;
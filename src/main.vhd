library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ray_tracer_pkg.all;
use work.fixed_pkg.all;

entity main is
    port (
        clk: in std_logic;
        sw: in std_logic_vector(3 downto 0);
        btn: in std_logic_vector(3 downto 0);
        led: out std_logic_vector(3 downto 0);
        uart_tx: out std_logic;
        -- uart_rx_data_out: out std_logic_vector(7 downto 0);
        -- uart_rx_busy_out: out std_logic;
        -- out_hit_info: out HitInfo_t;
        -- stage_2: out stage_2_t;
        uart_rx: in std_logic
    );
end main;

architecture arch of main is
    signal rst: std_logic := '0';
    type state_t is (IDLE, RECEIVING_COMMAND, RECEIVING_DATA, PROCESSING, SENDING_DATA, TERMINATED);
    signal state: state_t := IDLE;
    constant WRITE_TRIANGLE: std_logic_vector(7 downto 0) := x"01";
    constant READ_TRIANGLE: std_logic_vector(7 downto 0) := x"02";
    constant TRACE: std_logic_vector(7 downto 0) := x"03";

    -- UART --
    signal uart_tx_busy: std_logic := '0';
    signal uart_tx_data: std_logic_vector(7 downto 0) := (others => '0');
    signal uart_tx_rdy: std_logic := '0';

    signal uart_rx_valid: std_logic := '0';
    signal uart_rx_data: std_logic_vector(7 downto 0) := (others => '0');
    signal uart_rx_error: std_logic := '0';
    
    signal uart_rx_buffer: bytes(38 downto 0) := (others => (others => '0'));
    signal uart_rx_buffer_len_expected: unsigned(5 downto 0) := (others => '0');
    signal uart_rx_buffer_index: unsigned(5 downto 0) := (others => '0');

    signal uart_tx_index: unsigned(5 downto 0) := (others => '0');
    
    -- RAM --
    signal ram_data: std_logic_vector(287 downto 0) := (others => '0'); 
    signal ram_q: std_logic_vector(287 downto 0) := (others => '0'); 
    signal ram_wren: std_logic := '0';
    signal ram_address: std_logic_vector(8 downto 0) := (others => '0');

--     -- RT
    signal current_triangle: Triangle_t := zero_triangle;
    signal current_ray: Ray_t := zero_ray;
    signal current_tri_index: unsigned(15 downto 0) := (others => '0');
    signal last_tri_index: unsigned(15 downto 0) := (others => '0');
    signal done_in: std_logic := '0';
    signal done_out: std_logic := '0';
    signal rst_out: std_logic := '0';
    signal hit: std_logic := '0';
    signal hit_info: HitInfo_t := zero_hit_info;
    -- signal closest_hit_info: HitInfo_t := zero_hit_info;
    -- signal closest_done_out: std_logic := '0';
    -- signal any_hit: std_logic := '0';
    signal intersector_rst: std_logic := '0';
    signal is_processing_state: std_logic := '0';
    signal divided_clk: std_logic := '0';
    signal clk_counter: unsigned(6 downto 0) := (others => '0');
    signal state_led: std_logic_vector(2 downto 0) := (others => '0'); 

    signal receving_command_state: integer := 0;
    signal receiving_data_state : integer := 0;
    signal processing_data_state : integer := 0;
    signal sending_data_state : integer := 0;
    signal trace_tx_data: bytes(5 downto 0) := (others => (others => '0'));
begin        
    -- out_hit_info <= hit_info;
    clk_divider: process(clk)
    begin
        if rising_edge(clk) then
            clk_counter <= clk_counter + 1;
        end if;
    end process;

    divided_clk <= clk;

    rst <= not btn(0);
    -- led(0) <= uart_rx_busy;
    -- led(1) <= uart_tx_busy;
    -- led(3) <= uart_rx_busy;

    state_led <=
        "000" when state = IDLE else
        "001" when state = RECEIVING_COMMAND else
        "010" when state = RECEIVING_DATA else
        "011" when state = PROCESSING else
        "100" when state = SENDING_DATA else
        "101" when state = TERMINATED else
        "111";
     
    led <= uart_rx_buffer(0)(3 downto 0) when btn(1) = '1' else uart_rx_valid & state_led;
    -- uart_rx_data_out <= uart_rx_data;

    
--     -- hit_out <= hit;
--     -- t_out <= hit_info.t;

--     -- uart_rx_buffer_out <= uart_rx_buffer(to_integer(uart_rx_buffer_index_in));
--     -- uart_tx_index_out <= uart_tx_index;
--     -- rst <= key(0);
--     -- clk <= clock_50;
--     -- uart_rx_busy_out <= uart_rx_busy;
--     -- ram_gen: for i in 0 to 5 generate
--     --     ram_inst: component ram
--     --     port map(
--     --         address_a => ram_address,
--     --         clock => clk,
--     --         data_a => ram_data(i * 64 + 63 downto i * 64),
--     --         wren_a => ram_wren,
--     --         q_a => ram_q(i * 64 + 63 downto i * 64)
--     --     );
--     -- end generate;
        
--     ----- RT -----
    
--     -- current_tri_index <= unsigned(ram_address);
--     -- done_in <= '1' when (current_tri_index = last_tri_index) else '0';
    current_triangle <= (
        x => (x => "111111111110111111111111", y => "111111111110111111111111", z => "000000000001000000000000"), 
        y => (x => "111111111110111111111111", y => "000000000001000000000000", z => "000000000000000000000000"), 
        z => (x => "111111111110111111111111", y => "111111111110111111111111", z => "111111111110111111111111"), 
        normal => (x => "111111111110111111111111", y => "000000000000000000000000", z => "000000000000000000000000") 
    );
    

    is_processing_state <= divided_clk when state = PROCESSING else '0';
    intersector: component triangle_intersector
    port map(
        clk => divided_clk,
        rst => intersector_rst,
        ray => current_ray,
        triangle => current_triangle,
        tri_index => current_tri_index,
        done_in => done_in,
        done_out => done_out,
        hit => hit,
        hit_info => hit_info,
        rst_out => rst_out
        -- stage_2_out => stage_2
    );

    -- closest_hit_inst: component closest_hit
    -- port map(
    --     clk => is_processing_state,
    --     rst => intersector_rst,
    --     data_valid => rst_out,
    --     done_in => done_out,
    --     hit_info =>  hit_info,
    --     hit => hit,
        
    --     done_out => closest_done_out,
    --     any_hit => any_hit,
    --     closest_hit_info => closest_hit_info
    -- );
    
    ram_b: component ram
    generic map (
        DATA_WIDTH => 288,
        ADDR_WIDTH => 9,
        INIT_DATA_FILE => ""
    )
    port map(
        clk => clk,
        we => ram_wren,
        a => ram_address,
        di => ram_data,
        dout => ram_q
    );
       
    uart_rx_inst: component uartrx
    generic map(
        BIT_RATE => 921600,
        PAYLOAD_BITS => 8,
        CLK_HZ => 125_000_000
    )
    port map(
        clk => divided_clk,
        resetn => rst,
        uart_rxd => uart_rx,
        uart_rx_en => '1',
        uart_rx_valid => uart_rx_valid,
        uart_rx_data => uart_rx_data
    );

    uart_tx_inst: component uarttx
    generic map(
        BIT_RATE => 921600,
        PAYLOAD_BITS => 8,
        CLK_HZ => 125_000_000
    )
    port map(
        clk => divided_clk,
        resetn => rst,
        uart_txd => uart_tx,
        uart_tx_en => uart_tx_rdy,
        uart_tx_busy => uart_tx_busy,
        uart_tx_data => uart_tx_data
    );

    process(divided_clk, rst)
    begin
        if rising_edge(divided_clk) then
            if rst = '0' then
                state <= IDLE;
                uart_rx_buffer_index <= (others => '0');
                uart_tx_index <= (others => '0'); 
                intersector_rst <= '0';
                ram_wren <= '0';
                uart_rx_buffer <= (others => (others => '0'));
            else
                case state is
                    when IDLE =>
                        uart_tx_index <= (others => '0'); 
                        receving_command_state <= 0;
                        receiving_data_state <= 0;
                        processing_data_state <= 0;
                        sending_data_state <= 0;
                        ram_wren <= '0';
                        intersector_rst <= '0';
                        if uart_rx_valid = '1' then
                            state <= RECEIVING_DATA;
                            uart_rx_buffer(0) <= uart_rx_data;
                            uart_rx_buffer_index <= "000001";
                            if uart_rx_data = WRITE_TRIANGLE then
                                uart_rx_buffer_len_expected <= "100110"; -- 2 bytes for address + 36 bytes for triangle
                            elsif uart_rx_data = READ_TRIANGLE then
                                uart_rx_buffer_len_expected <= "000010"; -- 2 bytes for address
                            elsif uart_rx_data = TRACE then
                                uart_rx_buffer_len_expected <= "010010"; -- 18 bytes for ray_t
                            else
                                uart_rx_buffer_len_expected <= "111111";
                            end if; 
                        else
                            state <= IDLE;
                        end if;
                    when RECEIVING_DATA =>
                        if receiving_data_state = 0 then
                            if uart_rx_buffer_len_expected = "111111" then -- error
                                state <= TERMINATED;
                            elsif uart_rx_valid = '1' then -- wait until we receive smth in uart
                                receiving_data_state <= 1;
                                uart_rx_buffer(to_integer(uart_rx_buffer_index)) <= uart_rx_data;
                            else 
                                receiving_data_state <= 0;
                            end if;
                        elsif receiving_data_state = 1 then -- after we received smth
                            receiving_data_state <= 0;
                            if uart_rx_buffer_index = uart_rx_buffer_len_expected then
                                state <= PROCESSING;
                            else
                                uart_rx_buffer_index <= uart_rx_buffer_index + 1;
                            end if;
                        end if;

                    when PROCESSING =>
                        if uart_rx_buffer(0) = WRITE_TRIANGLE then
                            if processing_data_state = 0 then
                                ram_address <= uart_rx_buffer(2)(0 downto 0) & uart_rx_buffer(1);
                                for i in 35 downto 0 loop
                                    ram_data(i * 8 + 7 downto i * 8) <= uart_rx_buffer(i + 3);  
                                end loop;
                                processing_data_state <= 1;
                                ram_wren <= '0';
                            elsif processing_data_state = 1 then
                                ram_wren <= '1';
                                processing_data_state <= 2;
                            elsif processing_data_state = 2 then
                                ram_wren <= '0';
                                processing_data_state <= 0;
                                state <= IDLE;
                            end if;
                        elsif uart_rx_buffer(0) = READ_TRIANGLE then
                            ram_wren <= '0';
                            ram_address <= uart_rx_buffer(2)(0 downto 0) & uart_rx_buffer(1);
                            ram_data <= (others => '0');
                            state <= SENDING_DATA;
                            uart_tx_index <= (others => '0');
                        elsif uart_rx_buffer(0) = TRACE then
                            current_ray.origin <= bytes_to_vec3(uart_rx_buffer(9 downto 1));
                            current_ray.direction <= bytes_to_vec3(uart_rx_buffer(18 downto 10));
                            done_in <= '1';
                            intersector_rst <= '1';
                            current_tri_index <= (others => '0');
                            if done_out = '1' then
                                state <= SENDING_DATA;

                                for i in 0 to 2 loop
                                    trace_tx_data(i) <= to_slv(hit_info.t(i * 8 + 7 - 12 downto i * 8 - 12));
                                end loop;
                                
                                for i in 0 to 1 loop
                                    trace_tx_data(i+3) <= std_logic_vector(hit_info.tri_index(i * 8 + 7 downto i * 8));
                                end loop;   

                                uart_tx_index <= (others => '0');
                                intersector_rst <= '0';
                            end if;
                        else
                        end if; 
                    when SENDING_DATA =>
                        if uart_rx_buffer(0) = READ_TRIANGLE then
                            if sending_data_state = 0 then
                                uart_tx_data <= ram_q(to_integer(uart_tx_index) * 8 + 7 downto to_integer(uart_tx_index) * 8);
                                sending_data_state <= 1;
                                uart_tx_rdy <= '0';
                            elsif sending_data_state = 1 then
                                if uart_tx_index = "100100" then -- index == 36 
                                    state <= IDLE;
                                    sending_data_state <= 0;
                                else
                                    uart_tx_rdy <= '1';
                                    sending_data_state <= 2;
                                end if;
                            elsif sending_data_state = 2 then
                                if uart_tx_rdy = '1' then
                                    uart_tx_rdy <= '0';
                                    sending_data_state <= 2;
                                elsif uart_tx_busy = '0' then
                                    sending_data_state <= 0;
                                    uart_tx_index <= uart_tx_index + 1;
                                else
                                    sending_data_state <= 2;
                                end if;
                            end if;
                        elsif uart_rx_buffer(0) = TRACE then
                            if sending_data_state = 0 then
                                -- if hit = '1' then
                                -- else
                                --     for i in 0 to 4 loop
                                --         trace_tx_data(i) := x"f0";
                                --     end loop;
                                -- end if;    
                                uart_tx_data <= trace_tx_data(to_integer(uart_tx_index));
                                sending_data_state <= 1;
                                uart_tx_rdy <= '0';

                            elsif sending_data_state = 1 then
                                if uart_tx_index = "000101" then -- index == 5
                                    state <= IDLE;
                                    sending_data_state <= 0;
                                else
                                    uart_tx_rdy <= '1';
                                    sending_data_state <= 2;
                                end if;
                            elsif sending_data_state = 2 then
                                if uart_tx_rdy = '1' then
                                    uart_tx_rdy <= '0';
                                    sending_data_state <= 2;
                                    uart_tx_index <= uart_tx_index + 1;
                                elsif uart_tx_busy = '0' then
                                    sending_data_state <= 0;
                                else
                                    sending_data_state <= 2;
                                end if;
                            end if;
                        end if;
                    when TERMINATED => 
                        state <= TERMINATED;
                    when others =>
                        state <= IDLE;
                end case;
            end if;
        end if;
    end process;
end arch; -- arch
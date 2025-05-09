library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.fixed_pkg.all;

package ray_tracer_pkg is 
    subtype fixed_t is sfixed(11 downto -12);
    function to_fixed_t(arg: sfixed) return fixed_t;

    type bytes is array (NATURAL range <>) of std_logic_vector(7 downto 0);

    type vec3 is record
        x: fixed_t;
        y: fixed_t;
        z: fixed_t;
    end record;

    function bytes_to_vec3(vec3_bytes: bytes(8 downto 0)) return vec3;
    function logic_vector_to_vec3(vec3_bytes: std_logic_vector(71 downto 0)) return vec3;

    type vec3_vector is array(NATURAL range <>) of vec3;
    
    constant zero_vec3: vec3 := (
        x => (others => '0'),
        y => (others => '0'),
        z => (others => '0')
    );
    
    type Ray_t is record 
        origin: vec3;
        direction: vec3;
    end record;

    type Ray_vector is array(NATURAL range <>) of Ray_t;

    type Triangle_t is record 
        x: vec3;
        y: vec3;
        z: vec3;
        normal: vec3;
    end record;
    function ram_q_to_triangle(tri_bytes: std_logic_vector(287 downto 0)) return Triangle_t;

    type HitInfo_t is record 
        tri_index: unsigned(15 downto 0);
        t: fixed_t; 
    end record;
    
    constant zero_ray: Ray_t := (
        origin => zero_vec3,
        direction => zero_vec3
    );

    constant zero_triangle: Triangle_t := (
        x => zero_vec3,
        y => zero_vec3,
        z => zero_vec3,
        normal => zero_vec3
    ); 

    constant zero_hit_info: HitInfo_t := (
        tri_index => (others => '0'),
        t => (11 => '0', others => '1')
    );

    type DebugVectors_t is record
        x: vec3;
        y: vec3;
        z: vec3;
    end record;

    type stage_1_t is record 
        NdotOrigin: fixed_t;
        NdotRayDir: fixed_t;
        ray: Ray_t;
        triangle: Triangle_t;
        edge_x: Vec3;
        edge_y: Vec3;
        edge_z: Vec3;
        temp_t: fixed_t;
        distance_to_origin: fixed_t;
        tri_index: unsigned(15 downto 0);
        hit: std_logic;
        done: std_logic;
        rst: std_logic;
        -- debug_vectors: DebugVectors_t;
    end record;

    type stage_2_t is record 
        triangle: Triangle_t;
        ray: Ray_t;
        edge_x: Vec3;
        edge_y: Vec3;
        edge_z: Vec3;
        hit_info: HitInfo_t;
        hit: std_logic;
        done: std_logic;
        rst: std_logic;
        -- debug_vectors: DebugVectors_t;
    end record;

    type stage_3_t is record 
        ray: Ray_t;
        hit_info: HitInfo_t;
        hit_pos: vec3;
        triangle: Triangle_t;
        edge_x: Vec3;
        edge_y: Vec3;
        edge_z: Vec3;
        hit: std_logic;
        done: std_logic;
        rst: std_logic;
        -- debug_vectors: DebugVectors_t;
    end record;

    type stage_4_t is record 
        hit_info: HitInfo_t;
        c0: vec3;
        c1: vec3;
        c2: vec3;
        edge_x: vec3;
        edge_y: vec3;
        edge_z: vec3;      
        normal: vec3;  
        hit: std_logic;
        done: std_logic;
        rst: std_logic;
        debug_vectors: DebugVectors_t;
    end record;

    type stage_5_t is record 
        hit_info: HitInfo_t;
        n0: vec3;
        n1: vec3;
        n2: vec3;
        normal: vec3;
        hit: std_logic;
        done: std_logic;
        rst: std_logic;
        debug_vectors: DebugVectors_t;
    end record;

    type stage_6_t is record 
        hit_info: HitInfo_t;
        NdotN0: fixed_t;
        NdotN1: fixed_t;
        NdotN2: fixed_t;
        hit: std_logic;
        done: std_logic;
        rst: std_logic;
        debug_vectors: DebugVectors_t;
    end record;

    type stage_7_t is record 
        hit_info: HitInfo_t;
        hit: std_logic;
        done: std_logic;
        rst: std_logic;
        debug_vectors: DebugVectors_t;
    end record;

    component triangle_intersector is
        port (
            clk: in std_logic;
            clr: in std_logic;
            rst: in std_logic;
            ray: in Ray_t;
            triangle: in Triangle_t;
            tri_index: in unsigned(15 downto 0);
            done_in: in std_logic;
    
            done_out: out std_logic; -- used to indicate for the closest_hit component that the current triangle batch is done and it can calculate it.  
            hit: out std_logic;
            hit_info: out HitInfo_t;
            -- stage_1_out: out stage_1_t;
            -- stage_2_out: out stage_2_t;
            -- reciprocal_out_data_d: out fixed_t;
            debug_vectors: out DebugVectors_t;
            rst_out: out std_logic -- 1 signifies that the data is valid (its just the rst signal moved through the pipeline)
        );
    end component;

    component closest_hit is
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
    end component; 
    
    component uart is
    generic(
        clk_freq  :  integer    := 50_000_000;  --frequency of system clock in hertz
        baud_rate :  integer    := 19_200;      --data link baud rate in bits/second
        os_rate   :  integer    := 16;          --oversampling rate to find center of receive bits (in samples per baud period)
        d_width   :  integer    := 8;           --data bus width
        parity    :  integer    := 1;           --0 for no parity, 1 for parity
        parity_eo :  std_logic  := '0');        --'0' for even, '1' for odd parity
    port(
        clk      :  in   std_logic;                             --system clock
        reset_n  :  in   std_logic;                             --ascynchronous reset
        tx_ena   :  in   std_logic;                             --initiate transmission
        tx_data  :  in   std_logic_vector(d_width-1 downto 0);  --data to transmit
        rx       :  in   std_logic;                             --receive pin
        rx_busy  :  out  std_logic;                             --data reception in progress
        rx_error :  out  std_logic;                             --start, parity, or stop bit error detected
        rx_data  :  out  std_logic_vector(d_width-1 downto 0);  --data received
        tx_busy  :  out  std_logic;                             --transmission in progress
        tx       :  out  std_logic);                            --transmit pin
    end component uart;

    component ram is
    generic (
        DATA_WIDTH: natural := 32;
        ADDR_WIDTH: natural := 16;
        INIT_DATA_FILE: string := "" 
    );
    port(
        clk : in std_logic;
        we : in std_logic;
        a : in std_logic_vector(ADDR_WIDTH-1 downto 0);
        di : in std_logic_vector(DATA_WIDTH-1 downto 0);
        dout : out std_logic_vector(DATA_WIDTH-1 downto 0)
    );
    end component;
    
    component rom is
    generic (
        DATA_WIDTH: natural := 32;
        ADDR_WIDTH: natural := 16;
        INIT_DATA_FILE: string := "" 
    );
    port(
        clk : in std_logic;
        a : in std_logic_vector(ADDR_WIDTH-1 downto 0);
        dout : out std_logic_vector(DATA_WIDTH-1 downto 0)
    );
    end component;
    
    component fixed_reciprocal is
    port (
        clk   : in std_logic;
        rst : in std_logic;
        input_data: in fixed_t;
        out_rst: out std_logic;
        output_data: out fixed_t
    );
    end component;

    component uartrx is
    generic (
        BIT_RATE: natural := 9600;
        PAYLOAD_BITS: natural := 8;
        CLK_HZ: natural := 50_000_000
    );
    port (
        clk           : in std_logic;
        resetn        : in std_logic;
        uart_rxd      : in std_logic;
        uart_rx_en    : in std_logic;
        uart_rx_break : out std_logic;
        uart_rx_valid : out std_logic;
        uart_rx_data  : out std_logic_vector(PAYLOAD_BITS-1 downto 0)
    );
    end component;
    
    component uarttx is
    generic (
        BIT_RATE: natural := 9600;
        PAYLOAD_BITS: natural := 8;
        CLK_HZ: natural := 50_000_000
    );
    port (
        clk           : in std_logic;
        resetn        : in std_logic;
        uart_tx_en    : in std_logic;
        uart_tx_data  : in std_logic_vector(PAYLOAD_BITS-1 downto 0);
        uart_txd      : out std_logic;
        uart_tx_busy  : out std_logic
    );
    end component;

    component fifo is 
    generic (
        DATA_W: natural := 4; -- Data width
        DEPTH:  natural  := 8;  -- Depth of FIFO                   
        UPP_TH: natural := 4; -- Upper threshold to generate Almost-full
        LOW_TH: natural := 2  -- Lower threshold to generate Almost-empty
    );
    port (
        clk: in std_logic;                                      -- Clock
        rstn: in std_logic;                                     -- Active-low Synchronous Reset
        i_wren: in std_logic;                                   -- Write Enable
        i_wrdata: in std_logic_vector(DATA_W - 1 downto 0);     -- Write-data
        o_alm_full: out std_logic;                              -- Almost-full signal
        o_full: out std_logic;                                  -- Full signal
        i_rden: in std_logic;                                   -- Read Enable
        o_rddata: out std_logic_vector(DATA_W - 1 downto 0);    -- Read-data
        o_alm_empty: out std_logic;                             -- Almost-empty signal
        o_empty: out std_logic                                  -- Empty signal
    );
    end component;


    constant zero_stage_1: stage_1_t := (
        NdotOrigin => (others => '0'),
        NdotRayDir => (others => '0'),
        ray => zero_ray,
        triangle => zero_triangle,
        tri_index => (others => '0'),
        distance_to_origin => (others => '0'), 
        temp_t => (others => '0'), 
        edge_x => zero_vec3,
        edge_y => zero_vec3,
        edge_z => zero_vec3,
        hit => '1',
        done => '0',
        -- debug_vectors => (others => zero_vec3),
        rst => '0'
    );

    constant zero_stage_2: stage_2_t := (
        triangle => zero_triangle,
        ray => zero_ray,
        edge_x => zero_vec3,
        edge_y => zero_vec3,
        edge_z => zero_vec3,
        hit_info => zero_hit_info,
        hit => '1',
        done => '0',
        -- debug_vectors => (others => zero_vec3),
        rst => '0'
    );

    constant zero_stage_3: stage_3_t := (
        ray => zero_ray,
        triangle => zero_triangle,
        edge_x => zero_vec3,
        edge_y => zero_vec3,
        edge_z => zero_vec3,
        hit_info => zero_hit_info,
        hit_pos => zero_vec3,
        hit => '1',
        done => '0',
        -- debug_vectors => (others => zero_vec3),
        rst => '0'
    ); 

    constant zero_stage_4: stage_4_t := (
        hit_info => zero_hit_info,
        c0 => zero_vec3,
        c1 => zero_vec3,
        c2 => zero_vec3,
        edge_x => zero_vec3,
        edge_y => zero_vec3,
        edge_z => zero_vec3,
        normal => zero_vec3,        
        hit => '1',
        done => '0',
        debug_vectors => (others => zero_vec3),
        rst => '0'
    );

    constant zero_stage_5: stage_5_t := (
        hit_info => zero_hit_info,
        n0 => zero_vec3,
        n1 => zero_vec3,
        n2 => zero_vec3,
        normal => zero_vec3,
        hit => '1',
        done => '0',
        debug_vectors => (others => zero_vec3),
        rst => '0'
    );

    constant zero_stage_6: stage_6_t := (
        hit_info => zero_hit_info,
        NdotN0 => (others => '0') ,
        NdotN1 => (others => '0') ,
        NdotN2 => (others => '0') ,
        hit => '1',
        done => '0',
        debug_vectors => (others => zero_vec3),
        rst => '0'
    );

    constant zero_stage_7: stage_7_t := (
        hit_info => zero_hit_info,
        hit => '1',
        done => '0',
        debug_vectors => (others => zero_vec3),
        rst => '0'
    );

end package;


package body ray_tracer_pkg is 

    function to_fixed_t(arg: sfixed) return fixed_t is
        variable ret: fixed_t;
    begin 
        ret := resize(arg, 11, -12);
        return ret;
    end function;

    function bytes_to_vec3(vec3_bytes: bytes(8 downto 0)) return vec3 is
        variable temp: std_logic_vector(71 downto 0);
    begin
        
        
        temp := vec3_bytes(0) & vec3_bytes(1) & vec3_bytes(2) &
        vec3_bytes(3) & vec3_bytes(4) & vec3_bytes(5) &
        vec3_bytes(6) & vec3_bytes(7) & vec3_bytes(8);



        return logic_vector_to_vec3(temp);
    end function;

    
    function logic_vector_to_vec3(vec3_bytes: std_logic_vector(71 downto 0)) return vec3 is
        variable ret: vec3;
    begin
        ret.x := sfixed(vec3_bytes(71 downto 48));
        ret.y := sfixed(vec3_bytes(47 downto 24));
        ret.z := sfixed(vec3_bytes(23 downto 0));
        return ret;
    end function;

    function ram_q_to_triangle(tri_bytes: std_logic_vector(287 downto 0)) return Triangle_t is
        variable tri: Triangle_t := zero_triangle; 
    begin
        tri.x := logic_vector_to_vec3(tri_bytes(287 downto 216));
        tri.y := logic_vector_to_vec3(tri_bytes(215 downto 144));
        tri.z := logic_vector_to_vec3(tri_bytes(143 downto 72));
        tri.normal := logic_vector_to_vec3(tri_bytes(71 downto 0));
        return tri;
    end function;


end package body;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.ray_tracer_pkg.all;
use work.linear_algebra_pkg.all;
use work.fixed_pkg.all;
use ieee.std_logic_textio.all;


entity triangle_intersector is
    port (
        clk   : in std_logic;
        rst : in std_logic;
        ray: in Ray_t;
        triangle: in Triangle_t;
        tri_index: in unsigned(15 downto 0);
        done_in: in std_logic;

        done_out: out std_logic; -- used to indicate for the closest_hit component that the current triangle batch is done and it can calculate it.  
        hit: out std_logic;
        hit_info: out HitInfo_t;
        -- Nd1: out Vec3;
        -- Nd2: out Vec3;
        -- Nd3: out Vec3;
        -- NdotRayDir: out fixed_t;
        -- stage_1_out: out stage_1_t;
        -- stage_2_out: out stage_2_t;
        -- reciprocal_out_data_d: out fixed_t;
    -- debug_vectors: out DebugVectors_t;
        rst_out: out std_logic -- 1 signifies that the data is valid (its just the rst signal moved through the pipeline)
    );
end entity;

architecture arch of triangle_intersector is
    signal stage_1_d1: stage_1_t := zero_stage_1;
    signal stage_1_d2: stage_1_t := zero_stage_1;
    signal stage_1_d3: stage_1_t := zero_stage_1;
    signal stage_1: stage_1_t := zero_stage_1;
    signal stage_2: stage_2_t := zero_stage_2;
    signal stage_3: stage_3_t := zero_stage_3;
    signal stage_4: stage_4_t := zero_stage_4;
    signal stage_5: stage_5_t := zero_stage_5;
    signal stage_6: stage_6_t := zero_stage_6;
    signal stage_7: stage_7_t := zero_stage_7;
    signal reciprocal_out_data: fixed_t := (others => '0');
    signal reciprocal_out_rst: std_logic := '0';

begin

    reciprocal_inst: component fixed_reciprocal
    port map(
        clk => clk,
        rst => stage_1_d1.rst,
        input_data => stage_1_d1.NdotRayDir,
        out_rst => reciprocal_out_rst,
        output_data => reciprocal_out_data
    );

    -- stage_1_out <= stage_1;
    -- reciprocal_out_data_d <= reciprocal_out_data;
    -- stage_2_out <= stage_2;

    pipeline: process(
        clk,
        rst, 
        ray,
        triangle,
        done_in,
        stage_1,
        stage_2,
        stage_3,
        stage_4,
        stage_5,
        stage_6,
        stage_7
    ) is
        variable s2_hit: std_logic:= '1';
        variable s3_hit: std_logic:= '1';
        variable s7_hit: std_logic:= '1';
    begin        
        if rising_edge(clk) then
            -- stage 0 to stage 1
            if rst = '0' then
                stage_1_d1 <= zero_stage_1;
            else
                stage_1_d1 <= (
                    NdotOrigin => dot(triangle.normal, ray.origin),
                    NdotRayDir => dot(triangle.normal, ray.direction),
                    ray => ray,
                    triangle => triangle,
                    edge_x => triangle.y - triangle.x,
                    edge_y => triangle.z - triangle.y,
                    edge_z => triangle.x - triangle.z,
                    distance_to_origin => not dot(triangle.x, triangle.normal),
                    temp_t => (others => '0'),
                    tri_index => tri_index,
                    hit => '1',
                    done => done_in,
                    -- debug_vectors => zero_stage_1.debug_vectors,
                    rst => rst
                );
            end if;

            if stage_1_d1.rst = '0' then
                stage_1_d2 <= zero_stage_1;
            else
                stage_1_d2 <= (
                    NdotOrigin => stage_1_d1.NdotOrigin,
                    NdotRayDir => stage_1_d1.NdotRayDir,
                    ray => stage_1_d1.ray,
                    triangle => stage_1_d1.triangle,
                    edge_x => stage_1_d1.edge_x,
                    edge_y => stage_1_d1.edge_y,
                    edge_z => stage_1_d1.edge_z,
                    distance_to_origin => stage_1_d1.distance_to_origin,
                    temp_t => not to_fixed_t(stage_1_d1.NdotOrigin + stage_1_d1.distance_to_origin),
                    tri_index => stage_1_d1.tri_index,
                    hit => stage_1_d1.hit,
                    done => stage_1_d1.done,
                    -- debug_vectors => stage_1_d1.debug_vectors,
                    rst => stage_1_d1.rst
                );
            end if;

            if stage_1_d2.rst = '0' then
                stage_1 <= zero_stage_1;
            else
                stage_1 <= stage_1_d2;
            end if;

            -- if stage_1_d3.rst = '0' then
            --     stage_1 <= zero_stage_1;
            -- else
            --     stage_1 <= stage_1_d3;
            -- end if;

            -- stage 1 to stage 2
            if stage_1.rst = '0' then
                stage_2 <= zero_stage_2;
            else
                
                if stage_1.NdotRayDir > 0 then
                    s2_hit := '0';
                else
                    s2_hit := stage_1.hit;
                end if;

                stage_2 <= (
                    triangle => stage_1.triangle,
                    edge_x => stage_1.edge_x,
                    edge_y => stage_1.edge_y,
                    edge_z => stage_1.edge_z,
                    ray => stage_1.ray,
                    hit_info => (
                        tri_index => stage_1.tri_index,
                        t => to_fixed_t(stage_1.temp_t * reciprocal_out_data)
                    ),
                    hit => s2_hit,
                    done => stage_1.done,
                    -- debug_vectors => stage_1.debug_vectors,
                    rst => stage_1.rst
                );
            end if;
            
            if stage_2.rst = '0' then
                stage_3 <= zero_stage_3;
            else
            -- stage 2 to stage 3
                if stage_2.hit_info.t > x"00001f" then
                    s3_hit := stage_2.hit;
                else
                    s3_hit := '0';
                end if;

                stage_3 <= (
                    hit_info => stage_2.hit_info,
                    hit_pos => stage_2.ray.origin + stage_2.ray.direction * stage_2.hit_info.t,
                    triangle => stage_2.triangle,
                    edge_x => stage_2.edge_x,
                    edge_y => stage_2.edge_y,
                    edge_z => stage_2.edge_z,
                    hit => s3_hit,
                    done => stage_2.done,
                    -- debug_vectors => (x => (others => stage_2.t), others => zero_vec3),
                    rst => stage_2.rst
                );
            end if;

            -- stage 3 to stage 4
            if stage_3.rst = '0' then
                stage_4 <= zero_stage_4;
            else
                stage_4 <= (
                    hit_info => stage_3.hit_info,
                    c0 => stage_3.hit_pos - stage_3.triangle.x,
                    c1 => stage_3.hit_pos - stage_3.triangle.y,
                    c2 => stage_3.hit_pos - stage_3.triangle.z,
                    edge_x => stage_3.edge_x,
                    edge_y => stage_3.edge_y,
                    edge_z => stage_3.edge_z, 
                    normal => stage_3.triangle.normal,       
                    hit => stage_3.hit,
                    done => stage_3.done,
                    -- debug_vectors => stage_3.debug_vectors,
                    rst => stage_3.rst
                );
            end if;
        
            -- stage 4 to stage 5
            if stage_4.rst = '0' then
                stage_5 <= zero_stage_5;
            else
                stage_5 <= (
                    hit_info => stage_4.hit_info,
                    n0 => cross(stage_4.edge_x, stage_4.c0),
                    n1 => cross(stage_4.edge_y, stage_4.c1),
                    n2 => cross(stage_4.edge_z, stage_4.c2),
                    normal => stage_4.normal,
                    hit => stage_4.hit,
                    done => stage_4.done,
                    -- debug_vectors => stage_4.debug_vectors,
                    rst => stage_4.rst
                );
            end if;

            -- stage 5 to stage 6
            if stage_5.rst = '0' then
                stage_6 <= zero_stage_6;
            else
                stage_6 <= (
                    hit_info => stage_5.hit_info,
                    NdotN0 => dot(stage_5.n0, stage_5.normal),
                    NdotN1 => dot(stage_5.n1, stage_5.normal),
                    NdotN2 => dot(stage_5.n2, stage_5.normal),
                    hit => stage_5.hit,
                    done => stage_5.done,
                    -- debug_vectors => stage_5.debug_vectors,
                    rst => stage_5.rst
                );
            end if;
            -- stage 6 to stage 7
            if stage_6.rst = '0' then
                stage_7 <= zero_stage_7;
            else
                if stage_6.NdotN0 <= 0 or stage_6.NdotN1 <= 0 or stage_6.NdotN2 <= 0 then 
                    s7_hit := '0';
                else
                    s7_hit := stage_6.hit;
                end if;

                stage_7 <= (
                    hit_info => stage_6.hit_info,
                    hit => s7_hit,
                    done => stage_6.done,
                    -- debug_vectors => stage_6.debug_vectors,
                    rst => stage_6.rst
                );
            end if;
            done_out <= stage_7.done;
            hit_info <= stage_7.hit_info;
            hit <= stage_7.hit;
            -- debug_vectors <= stage_7.debug_vectors;
            rst_out <= stage_7.rst;
            -- Nd1 <= stage_3.hit_pos;
            -- Nd2 <= stage_3.triangle.y;
            -- Nd3 <= stage_4.c1;
            -- NdotRayDir <= stage_1.NdotRayDir;

        end if;
    end process;
end arch ; -- arch
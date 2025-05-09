library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.fixed_pkg.all;
use work.ray_tracer_pkg.all;

package linear_algebra_pkg is
    function "+"(v1, v2: vec3) return vec3;
    function "-"(v1, v2: vec3) return vec3;
    function "*"(v1, v2: vec3) return vec3;
    function "*"(v: vec3; scalar: sfixed) return vec3; 
    function "*"(v: vec3; scalar: ufixed) return vec3; 

    component cross is 
        port(
            signal clk: in std_logic; 
            signal v1: in vec3;
            signal v2: in vec3; 
            signal ret: out vec3
        );
    end component;

    component dot is 
        port(
            signal clk: in std_logic; 
            signal v1: in vec3;
            signal v2: in vec3; 
            signal ret: out fixed_t
        );
    end component;

    function negative(v: vec3) return vec3;
end package;

package body linear_algebra_pkg is 
    -- Vec3 small
    function "+"(v1, v2: vec3) return vec3 is 
        variable ret: vec3;
    begin
        ret.x := to_fixed_t(v1.x + v2.x);
        ret.y := to_fixed_t(v1.y + v2.y);
        ret.z := to_fixed_t(v1.z + v2.z);
        return ret;
    end function;

    function "-"(v1, v2: vec3) return vec3 is 
        variable ret: vec3;
    begin
        ret.x := to_fixed_t(v1.x - v2.x);
        ret.y := to_fixed_t(v1.y - v2.y);
        ret.z := to_fixed_t(v1.z - v2.z);
        return ret;
    end function;

    function "*"(v1, v2: vec3) return vec3 is 
        variable ret: vec3;
    begin
        ret.x := to_fixed_t(v1.x * v2.x);
        ret.y := to_fixed_t(v1.y * v2.y);
        ret.z := to_fixed_t(v1.z * v2.z);
        return ret;
    end function;

    function "*"(v: vec3; scalar: sfixed) return vec3 is 
        variable ret: vec3;
    begin
        ret.x := to_fixed_t(v.x * scalar);
        ret.y := to_fixed_t(v.y * scalar);
        ret.z := to_fixed_t(v.z * scalar);
        return ret;
    end function;

    function "*"(v: vec3; scalar: ufixed) return vec3 is 
        variable ret: vec3;
    begin
        ret.x := to_fixed_t(v.x * to_sfixed(scalar));
        ret.y := to_fixed_t(v.y * to_sfixed(scalar));
        ret.z := to_fixed_t(v.z * to_sfixed(scalar));
        return ret;
    end function;

    -- just one's complement it for easier hardware (the error should be insignificant)
    function negative(v: vec3) return vec3 is 
        variable ret: vec3;
    begin
        ret.x := not v.x;
        ret.y := not v.y;
        ret.z := not v.z;
        return ret;
    end function;

end package body;

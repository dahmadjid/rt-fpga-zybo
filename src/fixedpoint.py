from copy import deepcopy
from cocotb.handle import BinaryValue

def ones_complement(bin_val: str):
    out = ''
    for bit in bin_val:
        if bit == '1':
            out += '0'
        else:
            out += '1'
    return out
    
def fp_str_to_float(fixed_point: str, m: int, n: int, signed: bool = False) -> float:
    len_fixed_point = len(fixed_point)
    if len_fixed_point != m + n:
        raise RuntimeError(f"[fp_str_to_float] {len_fixed_point=} != {m=} + {n=}") 
    
    sign = 1
    if signed and fixed_point[0] == '1':
        fixed_point = ones_complement(fixed_point)
        sign = -1
    integer_part = 0
    fractional_part = 0
    if m != 0:
        integer_part = int(fixed_point[:m], 2)
    if n != 0:
        fractional_part = int(fixed_point[m:], 2)

    float_value = integer_part + fractional_part / (2 ** n)
    return sign * float_value

def float_to_fp_str(float_value: float, m: int, n: int, signed: bool = False) -> str:
    signed_range = [(2 ** (m - 1) - 2 ** (-n)), -2 ** (m - 1)]
    if m <= 1 and float_value == 1:
        # edge case in the fixed_t and ufixed_s (0.9921 is max value)
        return "0" + "1" * (m + n - 1)
    if float_value == signed_range[1]:
        out = "0" * (m + n - 1)
        return "1" + out 
    if signed and (float_value > signed_range[0] or float_value < signed_range[1]):
        raise RuntimeError(f"[float_to_fp_str] {float_value} is not in range {signed_range}")
    
    if float_value >= 2 ** (m):
        raise RuntimeError(f"[float_to_fp_str] {float_value=} >= {(2 ** (m))=}")
    
    if float_value < 0 and signed == False:
        raise RuntimeError("[float_to_fp_str] float_value < 0 and signed == False")

    flipped = False
    if float_value < 0 and signed == True:
        float_value = -float_value
        flipped = True

    integer_part = int(float_value)
    fractional_part = float_value - integer_part
    
    int_binary_str = bin(integer_part)[2:].zfill(m)
    if m == 0:
        int_binary_str = ''
    elif signed and int_binary_str[0] == '1':
        raise RuntimeError("[float_to_fp_str] error in conversion logic")
    

    frac_binary_str = ''
    for _ in range(n):
        fractional_part *= 2
        bit = '1' if fractional_part >= 1 else '0'
        frac_binary_str += bit
        fractional_part -= int(bit)

    out = int_binary_str + frac_binary_str
    if flipped:
        out = ones_complement(out)

    if len(out) != m + n:
        if flipped:
            return "0" * (m + n) # it just means it overflowed when we did it twos complement
        else:
            raise RuntimeError(f"[float_to_fp_str] len(out) != m + n ({out=} {n=} {m=})")

    return out

class FixedPoint(float):
    fp_str: str
    signed: bool
    m: int
    n: int
    n_bits: int
    bin_value: BinaryValue
    _type: str 
    integer_value: int

    def __new__(cls, float_or_fp_str: float | str, m: int, n: int, signed: bool = False) -> "FixedPoint":
        if isinstance(float_or_fp_str, str):
            return super().__new__(cls, fp_str_to_float(float_or_fp_str, m, n, signed))
        else:
            return super().__new__(cls, float(float_or_fp_str))

    def __init__(self, float_or_fp_str: float | str, m: int, n: int, signed: bool = False) -> None:
        if isinstance(float_or_fp_str, str):
            float.__init__(fp_str_to_float(float_or_fp_str, m, n, signed))
            self.fp_str = float_or_fp_str
        else:
            float.__init__(float_or_fp_str)
            self.fp_str = float_to_fp_str(float_or_fp_str, m, n, signed)

        self.m = m
        self.n = n
        self.signed = signed
        self.n_bits = len(self.fp_str)
        self.bin_value = BinaryValue(value=self.fp_str)
        self.integer_value = int(self.fp_str, 2)
        
    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls, self.fp_str, self.m, self.n, self.signed)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls, self.fp_str, self.m, self.n, self.signed)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
    
    def max(self):
        if self.signed:
            return FixedPoint(fp_str_to_float("0" + "1" * (self.m + self.n -1), self.m, self.n, self.signed), self.m, self.n, self.signed)
        else:
            return FixedPoint(fp_str_to_float("1" * (self.m + self.n), self.m, self.n, self.signed), self.m, self.n, self.signed)
        
    def min(self):
        if self.signed:
            return FixedPoint(fp_str_to_float("1" + "0" * (self.m + self.n -1), self.m, self.n, self.signed), self.m, self.n, self.signed)
        else:
            return FixedPoint(fp_str_to_float("0" * (self.m + self.n), self.m, self.n, self.signed), self.m, self.n, self.signed)
        
def fixed_t(float_or_fp_str: float | str):
    fp = FixedPoint(float_or_fp_str, 12, 12, True)
    fp._type = "fixed_t"
    return fp

def ufixed_t(float_or_fp_str: float | str):
    fp = FixedPoint(float_or_fp_str, 12, 12, False)
    fp._type = "ufixed_t"
    return fp

def fixed_t_to_bytes(fp: FixedPoint) -> list[str]:
    assert len(fp.fp_str) == 24
    return [fp.fp_str[16:24], fp.fp_str[8:16], fp.fp_str[0:8]]


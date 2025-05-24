from fixedpoint import ufixed_t, FixedPoint, fixed_t
import os 
def lookup0_1(x: int):
    # 1 here doesnt mean float 1 but it means 1 * precision (which might be smth 0.0001 or smth idk depends on size of fixed point)
    if x == 0 or x == 1:
        return ufixed_t("1" * ufixed_t(0).fp_str.__len__())
    y = float((1 << ufixed_t(0).m) / float(x))
    return ufixed_t(y)

    
def lookup1_7(x: int):
    if x == 0 or x == 1:
        return ufixed_t("1" * ufixed_t(0).fp_str.__len__())
    
    x = float(x << 3)
    y = (1 << ufixed_t(0).m) / x  
    return ufixed_t(y)
    
def lookup8(x: int):
    if x == 0 or x == 1:
        return ufixed_t("1" * ufixed_t(0).fp_str.__len__())
    return ufixed_t(bin(int((1 << ufixed_t(0).m) / x))[2:].zfill(ufixed_t(0).fp_str.__len__()))
    

high_mask = 2 ** ufixed_t(0).m - 1 << ufixed_t(0).n
low_mask = 2 ** ufixed_t(0).n - 1

def div(a: FixedPoint):
    if a < 0:
        a = ufixed_t(-float(a))

    if a < 1:
        x = lookup0_1(a.integer_value & low_mask)
        return x
    elif a < 8:
        x = lookup1_7((a.integer_value & (low_mask << 3)) >> 3) 
        return x
    else:
        x = lookup8((a.integer_value & high_mask) >> ufixed_t(0).m)
        return x


tests = [0.0 for _ in range(4096 * 20)]
step = 1.0 / 4096

for i in range(len(tests)):
    tests[i] = step * (i + 1)

highest_error = 0.0
highest_error_input = 0.0
highest_error_res = 0.0
average_error = 0.0
smallest_error = 1000000.0
if os.path.exists("data.csv"):
    os.remove("data.csv")

with open("data.csv", "w") as f:
    f.write("input,error,correct,result\n")
    for test in tests:
        input = fixed_t(test) 
        correct = 1.0 / test
        res = div(input)
        error = abs(float(res) - correct)
        if error > highest_error:
            highest_error = error
            highest_error_input = test
            highest_error_res = float(res)

        if error < smallest_error:
            smallest_error = error

        average_error += error
        f.write("{:.7f},{:.7f},{:.7f},{:.7f}\n".format(test, error, correct, float(res)))
exit()
if os.path.exists("lookup0_1.data"):
    os.remove("lookup0_1.data")

if os.path.exists("lookup1_7.data"):
    os.remove("lookup1_7.data")

if os.path.exists("lookup8.data"):
    os.remove("lookup8.data")

f0 = open("lookup0_1.data", "w")
f1 = open("lookup1_7.data", "w")
f2 = open("lookup8.data", "w")

for i in range(2 ** ufixed_t(0).m):
    f0.write(lookup0_1(i).fp_str + "\n")
    f1.write(lookup1_7(i).fp_str + "\n")
    f2.write(lookup8(i).fp_str + "\n")

f0.close()
f1.close()
f2.close()
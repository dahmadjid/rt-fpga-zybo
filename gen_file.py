
with open("test.data", "w") as f:
    for i in range(512):
        f.write(bin(i)[2:].zfill(24) + "\n")
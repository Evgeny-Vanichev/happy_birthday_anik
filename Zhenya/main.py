N = 0
f = 2 * 3 * 4
for i in range(4, 7956):
    f *= i
    N += ((-1) ** (i % 2 + 1)) * f * (i + 2)
print(N)
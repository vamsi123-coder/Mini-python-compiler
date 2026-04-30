total = 0
rows = 5
cols = 4

for r in range(rows):
    for c in range(cols):
        temp = r * c
        if temp >= 10:
            total = total + 1

print(total)

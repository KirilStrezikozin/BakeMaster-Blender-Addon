import math

size = int(input("size: "))
jilter_size = int(input("range: "))
prob = dict()


def rd(jilter):
    x = math.sin(jilter) * 10000
    return x - math.floor(x)


a = []
rep = set()
k = 0
for i in range(size):
    a.append(i + 1)
    prob[i + 1] = [0] * size

for jilter in range(jilter_size):
    if size == -1:
        break

    i = size
    while 0 != i:
        rdi = math.floor(rd(jilter) * i)
        jilter += 1
        i -= 1

        c = a[i]
        a[i] = a[rdi]
        a[rdi] = c

    length = len(rep)
    rep.add(tuple(a))
    if length == len(rep):
        k += 1

    for i in range(size):
        prob[i + 1][a.index(i + 1)] += 1

    # print(a)

for key in prob.keys():
    s = sum(prob[key])
    print(key, s, end=": ")
    for value in prob[key]:
        print(round(value / s, 2), "%", end=" ")
    print()
print("duplicates: ", k)

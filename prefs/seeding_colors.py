import math
import colorsys


def rd(seed):
    x = math.sin(seed) * 10000
    return x - math.floor(x)


color_mats = 5
colors = []
step = round(1 / color_mats, 3)
step_seed = rd(color_mats)

color = [1.0, step_seed, 1.0]
for i in range(color_mats):
    rgb = list(colorsys.hsv_to_rgb(
        color[0], color[1], color[2]))
    rgb.append(1.0)
    colors.append(tuple(rgb))
    color[0] = abs(color[0] - step)

print("----------")
for c in colors:
    print(c)

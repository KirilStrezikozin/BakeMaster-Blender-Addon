import colorsys

# given variables
Points = 10 # number of points to scatter aka colors to get, > 0
SOrbit = 4 # value indicating at what number of scattered points the first Saturation orbit should end, > 0
VOrbit = 24 # value indicating at what number of scattered points the first Value orbit should end, > 0
MinOrbit = 2 # minimum on SOrbit = SOrbit / MinOrbit, same for minimum on VOrbit, float > 0
Slope = 45 # determines the change of number of points scattered with each next Value orbit, 0 <= Slope <= 89

# how many V orbits?
# calculate V step
# know how many S orbits on the V orbit
# calculate S step
# know how many points should be on the H orbit
# calculate H step
# scatter points


# first V orbit has 1 point
# second V orbit has VOrbit points
# third V orbit has VOrbit*2 points

def get_orbit_size(orbit_capacity, points):
    n = 1
    new_points = [1]
    points_cache = 1
    while points_cache < points:
        # minimum n of points on the current V orbit
        minimum = int(orbit_capacity / MinOrbit)
        # how many points left in total
        points_left = points - points_cache
        can_contain = points_left - ((points_left - orbit_capacity) + minimum)
        # if left more than orbit can contain, add orbit_capacity
        if points_left - orbit_capacity >= orbit_capacity:
            points_cache += orbit_capacity
            new_points.append(orbit_capacity)
        elif can_contain >= minimum and can_contain <= points_left:
            points_cache += can_contain
            new_points.append(can_contain)
        else:
            points_cache += points_left
            new_points.append(points_left)
        orbit_capacity *= 2
        n += 1
    return n, sorted(new_points)

n_v, v_points = get_orbit_size(VOrbit, Points)

print("orbits: %d" % n_v)
print(v_points)

if n_v - 1 == 0:
    v_step = 0
else:
    v_step = round(1 / (n_v - 1), 3)
print(v_step)

colors = []
color = [1.0, 0.0, 0.0]
for v_orbit_size in v_points:
    color[1] = 0.0
    n_s, s_points = get_orbit_size(SOrbit, v_orbit_size)
    print(n_s, s_points)

    if n_s - 1 == 0:
        s_step = 0
    else:
        s_step = round(1 / (n_s - 1), 3)

    for s_orbit_size in s_points:
        color[0] = 1.0
        if s_orbit_size - 1 == 0:
            h_step = 0
        else:
            h_step = round(1 / s_orbit_size, 3)

        for i in range(s_orbit_size):
            rgb = list((color[0], color[1], color[2]))
            rgb.append(1.0)
            colors.append(tuple(rgb))
            color[0] -= h_step
        
        color[1] += s_step
    
    color[2] += v_step

for c in colors:
    print(c)
 
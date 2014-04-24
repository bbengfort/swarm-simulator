from swarm.vectors import *

a = Vector.arrp(90,90)
b = Vector.arrp(50,50)
c = Vector.arrp(130,130)
d = Vector.arrp(90, 50)
e = Vector.arrp(90, 130)
f = Vector.arrp(50, 90)
g = Vector.arrp(130, 90)
h = Vector.arrp(130, 50)
i = Vector.arrp(50, 130)
j = Vector.arrp(50, 70)

vel = Vector.arrp(10,10)
points = {
    'a': a,
    'b': b,
    'c': c,
    'd': d,
    'e': e,
    'f': f,
    'g': g,
    'h': h,
    'i': i,
    'j': j,
}

for name, point in points.items():
    #if name == 'a': continue
    print "%s: %0.2f" % (name, a.heading(point, vel=vel))

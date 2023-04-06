import numpy as np
import pylab as pl
from matplotlib import collections  as mc
import matplotlib.pyplot as plt
import numpy as np
import csv
from math import cos, sin, radians, dist
import matplotlib.ticker as ticker
import math

def convert(anglex, b, e, r):
    angle = radians(anglex)

    #dog
    h = 311
    w = 453

    # #dawei
    # h = 864
    # w = 804

    #centres
    cx = (e+b)//2
    cy = -r


    # offset back to the origin

    Xn = [b, -r]
    Xn2 = [e, -r]

    if anglex == 0:
        return (tuple(Xn), tuple(Xn2))


    deltax = h * math.sin(radians(anglex)) 

    m1 = math.sin(radians(anglex)) * (w/2-(h/(2*math.tan(radians(anglex)))))

    m2 = h*math.cos(radians(anglex))

    deltay = 2*m1 + m2

    if anglex > 0:
        Xn = [b-deltax, -r]
        Xn2 = [e-deltax, -r]

    if anglex < 0:
        Xn = [b, -r-deltay]
        Xn2 = [e, -r-deltay]


    Xn = [Xn[0]*np.cos(angle)-Xn[1]*np.sin(angle), Xn[0]
          * np.sin(angle)+Xn[1]*np.cos(angle)]
    Xn2 = [Xn2[0]*np.cos(angle)-Xn2[1]*np.sin(angle), Xn2[0]
           * np.sin(angle)+Xn2[1]*np.cos(angle)]


    distance = dist(Xn, Xn2)
    # print("Distance", distance)

    return (tuple(Xn), tuple(Xn2))
    #return ((b, -r), (e, -r))

res = []
with open("10d.csv", "r") as new_file:
    # must specify the correct delimiter since it's not the default delimiter of ,
    csv_reader = csv.DictReader(new_file, delimiter=",")
    for line in csv_reader:
        k = convert(float(line["angle"]), float(
            line["begin"]), float(line["end"]), float(line["row"]))
        # print(k)

        res.append({"xi": k[0][0], "xf": k[1][0], "yi": k[0][1], "yf": k[1][1], "ang": float(
            line["angle"]), "g": line["grayscale"]})

m = max([float(coordinate["g"]) for coordinate in res])
lines = []

for stroke in res:
    line = [(stroke["xi"], stroke["yi"]), (stroke["xf"], stroke["yf"])]
    lines.append(line)


# 453 × 311

width = 453
height = 311
boundary = [(0, 0), (width, 0)], [(width, 0), (width, -height)
                                  ], [(width, -height), (0, -height)], [(0, -height), (0, 0)]

box = mc.LineCollection(np.array(boundary).astype(int), linewidths=2)
lc = mc.LineCollection(np.array(lines).astype(int), linewidths=0.5)
fig, ax = pl.subplots()
ax.add_collection(lc)
# ax.add_collection(box)
ax.autoscale()
ax.margins(0.1)
ax.plot(0,0, "ro")
plt.axis('equal')
plt.xlim(-550, 550)

# ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
# ax.yaxis.set_major_locator(ticker.MultipleLocator(20))
# plt.xlim(0, 453)
# plt.ylim(-311, 0)
plt.show()

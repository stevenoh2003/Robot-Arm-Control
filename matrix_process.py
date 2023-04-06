
import numpy as np
import csv
from math import cos, sin, radians, dist

def convert(angle, b, e, r):
    angle = radians(angle)
    h = 311
    w = 453

    #centres
    cx = (e+b)//2
    cy = -r
    # print("Centre", cx, cy)

    Xn = [
        (((b - (w/2))*np.cos(angle))-(((-r+(h/2))*np.sin(angle)))), 
        (((b - (w/2))*np.sin(angle))+(((-r+(h/2))*np.cos(angle))))
    ]

    Xn2 = [
        (((e - (w/2))*np.cos(angle))-(((-r+(h/2))*np.sin(angle)))), 
        (((e - (w/2))*np.sin(angle))+(((-r+(h/2))*np.cos(angle))))
    ]

    factor = ((b+e)/2, r)

    # offset back to the origin
    Xn = [b-factor[0], -r+factor[1]]
    Xn2 = [e-factor[0], -r+factor[1]]

    # print(Xn, Xn2)

    #rotate
    Xn = [Xn[0]*np.cos(angle)-Xn[1]*np.sin(angle), Xn[0]*np.sin(angle)+Xn[1]*np.cos(angle)]
    Xn2 = [Xn2[0]*np.cos(angle)-Xn2[1]*np.sin(angle), Xn2[0]*np.sin(angle)+Xn2[1]*np.cos(angle)]

    # offset back to original coordinate system
    Xn = [Xn[0]+factor[0], Xn[1]-factor[1]]
    Xn2 = [Xn2[0]+factor[0],Xn2[1]-factor[1]]

    # in normal cordinate system (not 4th q)
    # print("Xn", tuple(Xn))
    # print("Xn2", tuple(Xn2))

    distance = dist(Xn, Xn2)
    # print("Distance", distance)

    return (tuple(Xn), tuple(Xn2))

res = []
with open("doglist.csv", "r") as new_file:
    csv_reader = csv.DictReader(new_file, delimiter=",") #must specify the correct delimiter since it's not the default delimiter of ,
    for line in csv_reader:
        k = convert(float(line["angle"]), float(line["begin"]), float(line["end"]), float(line["row"]))
        # print(k)

        res.append({"xi":k[0][0],"xf":k[1][0], "yi":k[0][1], "yf":k[1][1], "ang":float(line["angle"]), "g":line["grayscale"]})

m = max([float(coordinate["g"]) for coordinate in res])

print(res[6]["g"])
print(m)
print(float(res[6]["g"])/float(m)*2)



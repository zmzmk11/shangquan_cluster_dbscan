# -*- coding:gb18030-*-
import numpy
import math

R = 6371.004

def count_dist(latA, lonA, latB, lonB):
    C = math.sin(latA)*math.sin(latB)+math.cos(lonA)*math.cos(lonB)*math.cos(lonA-lonB)
    Distance = R * numpy.arccos(C) * math.pi / 180
    return Distance

if __name__ == '__main__':
    dist = count_dist(31.547256, 120.439034, 31.547392, 120.438675)
    print(dist)

import math
import dcs


def getDistance(point1=dcs.Point, point2=dcs.Point):
    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y
    dX = abs(x1-x2)
    dY = abs(y1-y2)
    distance = math.sqrt(dX*dX + dY*dY)
    return distance

def convertMeterToNM(meters=int):
    nm = meters / 1852
    return nm
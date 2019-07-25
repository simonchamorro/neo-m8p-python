import cv2

from neom8p.gmaps import get_gmap

map = get_gmap(45.530807,-73.613293, 19)
cv2.imshow("map", map)
cv2.waitKey(1)
print ("yo")
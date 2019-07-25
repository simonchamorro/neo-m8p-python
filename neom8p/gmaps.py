import urllib
import numpy as np
import requests
import cv2

def get_gmap(lat, lon, zoom=20):
    urlparams = urllib.parse.urlencode({
        'center': f"{lat},{lon}",
        'zoom': str(zoom),
        'size': "600x600",
        'maptype': 'roadmap',
        "markers": f"|{lat},{lon}",
        "key": "AIzaSyCyatXqpMiOdsAjLnrkIxwagXCfHIZSyKc"
    })
    url = 'http://maps.google.com/maps/api/staticmap?' + urlparams
    data = requests.get(url).content
    # img = Image.open(io.BytesIO(data))
    # print (img.shape)

    nparr = np.fromstring(data, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img_np
import cv2
import numpy as np
import requests
import traceback

from detector import Detector

class ConnectException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class Foscam():
    def __init__(self, cam_address, cam_user, cam_pass, detector_options = {}):
        self.detector = Detector(**detector_options)
        self.cam_address = cam_address
        self.cam_user = cam_user
        self.cam_pass = cam_pass
        self.byts = bytes()
        try:
            cv2.namedWindow(self.detector.winName, cv2.WINDOW_AUTOSIZE)
        except AttributeError, e:
            pass

   def videostream(self):
       r = requests.get(self.cam_address, auth=(self.cam_user, self.cam_pass), stream=True)

       if(r.status_code == 200):
           for chunk in r.iter_content(chunk_size=1024):
               self.byts += chunk
               a = self.byts.find(b'\xff\xd8')
               b = self.byts.find(b'\xff\xd9')
               if a != -1 and b != -1:
                   try:
                       jpg = self.byts[a:b+2]
                       self.byts = self.byts[b+2:]
                       yield cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                   except:
                       cv2.destroyWindow(self.detector.winName)
                       raise

       else:
           raise ConnectException("It was not possible to connect to the camera. Error {}.".format(r.status_code))

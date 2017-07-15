import os
import time
import sys

import cv2
import requests
import numpy as np

class Detector():
    def __init__(self, winName = None, DELTA_COUNT_THRESHOLD = 1000, pathToSave = None,
                 freq_t = 3, freq_count = 1, secs_to_alert = 3, triggerAlert = None):
        self.start_time = time.time()
        self.DELTA_COUNT_THRESHOLD = DELTA_COUNT_THRESHOLD # sensibility
        self.delta_count_last = 1
        self.moving = {'state':False, 'log':[]}
        self.winName = winName
        self.triggerAlert = triggerAlert
        self.freq_t = freq_t
        self.freq_count = freq_count
        self.secs_to_alert = secs_to_alert

        if pathToSave is not None:
            self.photoInMov = True
            try:
                os.mkdir(pathToSave)
            except:
                pass
        else:
            self.photoInMov = False

    def delta_images(self, t0, t1, t2):
        d1 = cv2.absdiff(t2, t0)
        return d1

    def detect(self, cam):
        if not hasattr(self, 'cam'):
            self.samples = {'minus': cam, 'now': cam, 'plus': cam}
            self.cam = True

        record_video_state = False
        now = time.time()
        delta_view = self.delta_images(self.samples['minus'], self.samples['now'], self.samples['plus'])
        retval, delta_view = cv2.threshold(delta_view, 16, 255, 3)
        cv2.normalize(delta_view, delta_view, 0, 255, cv2.NORM_MINMAX)
        img_count_view = cv2.cvtColor(delta_view, cv2.COLOR_RGB2GRAY)
        delta_count = cv2.countNonZero(img_count_view)

        if self.winName is not None:
            delta_view = cv2.flip(delta_view, 1)
            cv2.putText(delta_view, "DELTA: %d"%(delta_count), (5, 15), cv2.FONT_HERSHEY_PLAIN, 0.8, (255,255,255))
            cv2.putText(delta_view, "UPTIME: %d "%(time.time()-self.start_time), (5, 26), cv2.FONT_HERSHEY_PLAIN, 0.8, (255,255,255))
            cv2.imshow(self.winName, cam)

        if (self.delta_count_last < self.DELTA_COUNT_THRESHOLD and delta_count >= self.DELTA_COUNT_THRESHOLD):
            record_video_state = True
            sys.stdout.write("MOVEMENT %f\n" % time.time())
            sys.stdout.flush()

            if self.moving['state'] == False:
                self.moving['state'] = True
                self.moving['log'].append(now)
                self.moving['log'] = self.moving['log'][-10000:] # limit the log in 10.000 entries to save memory.
            if self.triggerAlert is not None: self.check_alert()

        elif self.delta_count_last >= self.DELTA_COUNT_THRESHOLD and delta_count < self.DELTA_COUNT_THRESHOLD:
            record_video_state = False
            self.moving['state'] = False
            sys.stdout.write("STILL    %f\n" % time.time())
            sys.stdout.flush()
        self.delta_count_last = delta_count

        if self.photoInMov == True and record_video_state == True:
            cv2.imwrite('MOVEMENT_FRAMES/movement-pong-%f.png' % (now),cam)
        # move images through the queue.
        self.samples['minus'] = self.samples['now']
        self.samples['now'] = self.samples['plus']
        self.samples['plus'] = cam
        self.samples['plus'] = cv2.blur(self.samples['plus'],(8,8))
        self.samples['plus'] = cv2.resize(self.samples['plus'], (640, 480))


    def check_alert(self):
        def freq_mov(movimentos):
            last_seconds = 0
            for mov in movimentos:
                if time.time()-mov<=self.freq_t:
                    last_seconds+=1
            return last_seconds

        if ((self.moving['state'] == True and (time.time()-self.moving['log'][-1]>self.secs_to_alert)) or
           (freq_mov(self.moving['log'])>self.freq_count)):
                self.triggerAlert()


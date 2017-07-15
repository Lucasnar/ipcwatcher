import os
import cv2
import time

from ipcwatcher import Foscam

def main():
    cam_address = os.environ['CAM_ADDRESS']
    cam_user = os.environ['CAM_USER']
    cam_pass = os.environ['CAM_PASS']
    winName = 'Kitchen Cam'
    detector_options = { 'triggerAlert': alert, 'winName': winName }
    camera = Foscam(cam_address, cam_user, cam_pass, detector_options)

    try:
        for sample in camera.videostream():
            camera.detector.detect(sample)

            key = cv2.waitKey(10)
            if key == 0x1b or key == ord('q'):
                cv2.destroyWindow(winName)
                break
            elif key == ord('l'):
                print('Last moving action: %s'%(time.strftime('%Y-%m-%d %H:%M:%S',
                                                              time.localtime(camera.detector.moving['log'][-1]))))
    except:
        cv2.destroyWindow(winName)
        raise

def alert():
    print("ALERT!!!")

if __name__ == "__main__":
    main()

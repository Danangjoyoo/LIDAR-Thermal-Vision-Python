from modules import camera
import cv2
from cv2 import dnn_superres
import numpy as np
import time

class SuperResolutionEngine():
    availableFramework = ["edsr", "lapsrn", "espcn", "fsrcnn"]
    def __init__(self, framework = "espcn", scale = 2, modelPath = ""):
        self.framework = framework
        self.scale = scale
        self.sr = dnn_superres.DnnSuperResImpl_create()        
        if not modelPath: modelPath = self.getModelPath()
        print(modelPath)
        self.sr.readModel(modelPath)
        self.sr.setModel(framework, scale)
        self.sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    
    def getModelPath(self):
        return f"models/SuperResolution/{str.upper(self.framework)}_x{self.scale}.pb"
    
    def upscale(self, frame):
        frame = self.sr.upsample(frame)
        return frame

# sr = SuperResolutionEngine("espcn", 4)
# ori = cv2.imread("bf.png")
# downscale = cv2.resize(ori, (480, 270))
# upscale = sr.upscale(downscale)
# cv2.imshow("ori", ori)
# cv2.imshow("down", downscale)
# cv2.imshow("up", upscale)
# cv2.waitKey(0)

scale = 2
# sr = SuperResolutionEngine("fsrcnn", 2, f"models/SuperResolution/FSRCNN-small_x{scale}.pb")
# sr = SuperResolutionEngine("fsrcnn", scale)
sr = SuperResolutionEngine("espcn", scale)
# sr = SuperResolutionEngine("lapsrn", scale)
# cap = cv2.VideoCapture(2)
cap = camera.Camera([1920, 1080], [640,480])
now = time.perf_counter()
while 1:
    last = now
    now = time.perf_counter()
    rsf = cap.read()
    ori = rsf.color
    # ori = cv2.resize(ori, (960, 540))
    # downscale = cv2.resize(ori, None, fx=1/scale, fy=1/scale)
    # upscale = sr.upscale(ori)

    cv2.imshow("ori", ori)
    # cv2.imshow("down", downscale)
    # cv2.imshow("up", upscale)

    print(f"FPS: {int(1/(now-last))}           ",end="\r",flush=True)

    if cv2.waitKey(1) > 0: break
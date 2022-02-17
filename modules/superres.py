import cv2
from cv2 import dnn_superres
import numpy as np

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
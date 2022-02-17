import os, json, logging

with open("config.json","r") as f:
    rawConfig = json.load(f)

### CAMERA DETECTION

camRaw = rawConfig["camera"]

class _Resolution:
    def __init__(self,w,h):
        self.w = w
        self.h = h

class Frame:
    """
    Singleton class for Framesize config (color, depth, thermal)
    """
    color = _Resolution(
        camRaw["colorFrame"]["w"],
        camRaw["colorFrame"]["h"]
        )
    depth = _Resolution(
        camRaw["depthFrame"]["w"],
        camRaw["depthFrame"]["h"]
        )
    thermal = _Resolution(
        camRaw["thermalFrame"]["w"],
        camRaw["thermalFrame"]["h"]
        )

class Scale:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    @staticmethod
    def getCalibratedDepthScale():
        if(Frame.color.w == 1920 and Frame.color.h == 1080):
            if(Frame.depth.w == 1280 and Frame.depth.h== 720):
                return Scale(0.336*2, 0.354*2)
            elif(Frame.depth.w == 640 and Frame.depth.h== 480):
                return Scale(0.42*2, 0.31215*2)
        elif(Frame.color.w == 1280 and Frame.color.h == 720):
            if(Frame.depth.w == 1280 and Frame.depth.h== 720):
                return Scale(0.348*2, 0.34*2)
            elif(Frame.depth.w == 640 and Frame.depth.h== 480):
                return Scale(0.422*2, 0.3125*2)
        elif(Frame.color.w == 640 and Frame.color.h == 480):
            if(Frame.depth.w == 1280 and Frame.depth.h== 720):
                return Scale(0.258*2, 0.345*2)
            elif(Frame.depth.w == 640 and Frame.depth.h== 480):
                return Scale(0.3125*2, 0.3125*2)
        return Scale(0.36*2, 0.36*2)

### OBJECT DETECTION

class Model():
    """
    Singleton class for DNN config
    """
    def __init__(self):
        detConfig = rawConfig["objectDetection"]
        network = detConfig["network"]
        modelIdx = detConfig["frameworkIndex"]
        networkConfig = detConfig["framework"][network][modelIdx]

        self.confidenceThresh = detConfig["confidenceThreshold"]
        self.inputSize = networkConfig["inputSize"]
        self.config = networkConfig["config"]
        self.model = networkConfig["model"]

        with open(networkConfig["classfile"],"r") as cf:
            availableObject = json.load(cf)["object"]
        self.classes = [i["name"] for i in availableObject]
        self.colors = [i["color"] for i in availableObject]

model = Model()

### MEDIAPIPE

mpRaw = rawConfig["mediapipe"]

class Mediapipe:
    """
    Singleton class for Mediapipe config
    """
    maxObject = mpRaw["maxObject"]
    detectionConfidence = mpRaw["detectionConfidence"]
    trackingConfidence = mpRaw["trackingConfidence"]
    boxScale = mpRaw["boxScale"]
    centerOffset = mpRaw["centerOffset"]

### OBJECT TRACKING

trackerRaw = rawConfig["objectTracking"]

class Tracker:
    """
    Singleton class for Object Tracker config
    """
    swap = trackerRaw["swapEntryExit"]
    trackFactor = trackerRaw["trackFactor"]
    validDistanceCM = trackerRaw["validDistanceCM"]
    registerThreshold = trackerRaw["registerThreshold"]
    deleteThreshold = trackerRaw["deleteThreshold"]
    updateTemperatureAttempt = trackerRaw["updateTemperatureAttempt"]

### LOGGER

loggerRaw = rawConfig["logger"]
class Logger:
    """
    Singleton class for logger config
    """
    name = loggerRaw["name"]
    disable = not loggerRaw["enable"]
    levels = [logging._nameToLevel[l] for l in loggerRaw["showLevels"] if l in logging._nameToLevel]

### FLIR

flirRaw = rawConfig["flir"]
class Flir:
    """
    Singleton class for flir config
    """
    refreshThresh = flirRaw["refreshThresh"]
    showFrameBoundary = flirRaw["showFrameBoundary"]
    distancePolynom = flirRaw["distancePolynom"]
    distancePolynomRange = flirRaw["distancePolynomRange"]
    tempPolynom = flirRaw["tempPolynom"]
    tempPolynomRange = flirRaw["tempPolynomRange"]
    maxTemp = flirRaw["maxTemp"]
    minTemp = flirRaw["minTemp"]
    class frameSafetyFactor:
        x = flirRaw["frameSafetyFactor"]["x"]
        y = flirRaw["frameSafetyFactor"]["y"]

### GUI HANDLER

class _GUIConfigHandler:
    def __init__(self):
        pass

    def getRaw(self):
        with open("config.json","r") as f:
            rawConfig = json.load(f)
        return rawConfig
    
    def updateRaw(self, raw):
        with open("config.json","w") as f:
            json.dump(raw, f, indent=4)

    @property
    def entryX(self):
        return self.__getEntryX
    
    @entryX.setter
    def entryX(self, val):
        raw = self.getRaw()
        raw["GUI"]["entryLineX"] = int(val)
        self.updateRaw(raw)

    @entryX.getter
    def __getEntryX(self):
        rawConfig = self.getRaw()
        return rawConfig["GUI"]["entryLineX"]
    
    @property
    def exitX(self):
        return self.__getExitX
    
    @exitX.setter
    def exitX(self, val):
        raw = self.getRaw()
        raw["GUI"]["exitLineX"] = int(val)
        self.updateRaw(raw)

    @exitX.getter
    def __getExitX(self):
        rawConfig = self.getRaw()
        return rawConfig["GUI"]["exitLineX"]
    
    @property
    def swapBoundary(self):
        return self.__getSwap
    
    @swapBoundary.setter
    def swapBoundary(self, val):
        raw = self.getRaw()
        raw["objectTracking"]["swapEntryExit"] = bool(val)
        self.updateRaw(raw)

    @swapBoundary.getter
    def __getSwap(self):
        rawConfig = self.getRaw()
        return rawConfig["objectTracking"]["swapEntryExit"]

GUI = _GUIConfigHandler()
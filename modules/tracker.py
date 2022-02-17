from modules import config, utils
import os, sys, time
import cv2

kargv = utils.getKwargv()

class TrackedObject():
    """
    Tracked Object Handler. This class handles either valid or invalid objects.
    """
    id = 0
    trackedList = []
    totalValidObject = 0
    trackFactor = config.Tracker.trackFactor
    registerThreshold = config.Tracker.registerThreshold
    deleteThreshold = config.Tracker.deleteThreshold
    updateTemperatureAttempt = config.Tracker.updateTemperatureAttempt

    @staticmethod
    def verifyAll(detectedObj):
        """
        Verify the detected object over the whole tracked object thats still alive
        """
        for trackedObj in TrackedObject.trackedList:
            if trackedObj.isAlive:
                if trackedObj.verify(detectedObj):
                    return trackedObj.id
        return -1
    
    @staticmethod
    def refreshAll():
        """
        Refresh every alive tracked object
        """
        for trackedObj in TrackedObject.trackedList:
            trackedObj.refresh()
    
    @staticmethod
    def refreshAllWithBoundary(xentry, xexit):
        """
        Refresh every alive tracked object with entry and exit boundary
        """
        config.Tracker.swap = config.GUI.swapBoundary
        for trackedObj in TrackedObject.trackedList:
            trackedObj.refreshWithBoundary(xentry, xexit)
    
    @staticmethod
    def scanTrackedObject(detectedObj, flirCap):
        """
        Scan possible tracked object within trackFactor
        """
        objectID = TrackedObject.verifyAll(detectedObj)
        if objectID < 0:
            trackedObj = TrackedObject(detectedObj, flirCap)
            objectID = trackedObj.id
        return TrackedObject.trackedList[objectID]            

    def __init__(self, detectedObj, flirCap):
        self.id = TrackedObject.id
        self.timeout = self.deleteThreshold
        self.firstCenter = detectedObj.center
        self.object = detectedObj
        self.flirCap = flirCap
        self.isAlive = True
        self.temp = 0.
        self.tempUpdated = False
        self.valid = False
        self.validCount = 0
        self.drawn = False
        self.tempClass = -1
        TrackedObject.trackedList.append(self)
        TrackedObject.id += 1
    
    @property
    def boxColor(self):
        return [
            (200,200,5),
            (5,255,20),
            (5,5,255)
        ][self.tempClass]
    
    def refresh(self):
        if self.isAlive:
            self.timeout -= 1
            self.drawn = False
            self.isAlive = bool(self.timeout)
            if not self.valid:
                self.valid = self.validCount >= TrackedObject.registerThreshold
                TrackedObject.totalValidObject += int(self.valid)
    
    def refreshWithBoundary(self, xEntry, xExit):
        if self.isAlive:
            self.timeout -= 1
            self.drawn = False
            self.isAlive = bool(self.timeout)
            if not self.valid:
                if config.Tracker.swap:
                    validEntryExit = (self.firstCenter[0] >= xEntry) and (self.object.center[0] <= xExit)
                else:
                    validEntryExit = (self.firstCenter[0] <= xEntry) and (self.object.center[0] >= xExit)
                self.valid = (self.validCount >= TrackedObject.registerThreshold) and validEntryExit
                TrackedObject.totalValidObject += int(self.valid)

    def verify(self, detectedObj):
        """
        Verify if the detected object is already tracked or not
        """
        xValid = self.object.center[0]-(self.object.box[2]*self.trackFactor) <= detectedObj.center[0] <= self.object.center[0]+(self.object.box[2]*self.trackFactor)
        yValid = self.object.center[1]-(self.object.box[3]*self.trackFactor) <= detectedObj.center[1] <= self.object.center[1]+(self.object.box[3]*self.trackFactor)
        if xValid and yValid:
            self.validCount += 1
            self.object.center = detectedObj.center
            self.timeout = TrackedObject.deleteThreshold
            return True
        return False

    def updateTemp(self, tframe, box):
        try:
            temp = self.flirCap.getTemp(tframe, box)
            if temp:
                self.temp = temp
                self.tempUpdated = True
        except:
            pass
    
    def getCalibratedTemp(self, dist):
        temp = self.flirCap.calibrateTemp(self.temp, dist)
        self.determineFever(temp)
        return temp

    def determineFever(self, temp):
        if config.Flir.maxTemp <= temp: self.tempClass = 2
        elif config.Flir.minTemp <= temp <= config.Flir.maxTemp: self.tempClass = 1
        else: self.tempClass = 0
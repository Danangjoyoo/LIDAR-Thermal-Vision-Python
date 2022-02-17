from .config import Frame
from .logger import logger
from . import config
import os, sys, time
import cv2
import numpy as np

class ThermalFrame():
    def __init__(self, raw16bit):
        self.frame16bit = raw16bit
        self.__coloredFrame = None
        self.__externalColoring = False
    
    @property
    def frame8bit(self):
        cv2.normalize(self.frame16bit, self.frame16bit, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(self.frame16bit, 8, self.frame16bit)
        return cv2.cvtColor(np.uint8(self.frame16bit), cv2.COLOR_GRAY2RGB)        

    @property
    def color(self):
        return self.__getColor
    
    @color.setter
    def color(self, frame):
        self.__coloredFrame = frame
        self.__externalColoring = True

    @color.getter
    def __getColor(self):
        if not self.__externalColoring:
            self.__coloredFrame = cv2.applyColorMap(self.frame8bit, cv2.COLORMAP_JET)
        return self.__coloredFrame


class FLIR():
    def __init__(self, width, height):
        logger.info(f"FLIR,constructor,instantiation,w={width},h={height},START")
        self.xSafeFactor = config.Flir.frameSafetyFactor.x
        self.ySafeFactor = config.Flir.frameSafetyFactor.y
        self.refreshThreshold = config.Flir.refreshThresh
        self.refreshCounter = 0
        self.width = width
        self.height = height
        self.enableResize = not (self.width==160 and self.height==120)
        self.xmin = int(self.width*self.xSafeFactor)
        self.ymin = int(self.height*self.ySafeFactor)
        self.xmax = int(self.width*(1-self.xSafeFactor))
        self.ymax = int(self.height*(1-self.ySafeFactor))
        self.camID = 0
        self.cap = None
        self.scanCameraID()
        self.distRange = config.Flir.distancePolynomRange
        self.tempRange = config.Flir.tempPolynomRange
        self.polyDist = config.Flir.distancePolynom
        self.polyTemp = config.Flir.tempPolynom
        self.tempCalibrated = False
        logger.info("FLIR,constructor,instantiation,END")
    
    def scanCameraID(self, targetID=0):
        if 0 <= targetID <= 20:
            try:
                logger.info(f"FLIR,scanCameraID,id={targetID},START")
                self.cap = cv2.VideoCapture(targetID, cv2.CAP_V4L2)
                if self.cap.isOpened():
                    _, frame = self.cap.read()
                    try:
                        if frame.shape[1] == 160 and frame.shape[0] == 120:
                            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*"Y16 "))
                            self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.)
                            logger.info(f"FLIR,scanCameraID,id={targetID},VALID")
                            self.camID = targetID
                            return self.cap
                    except Exception as e:
                        logger.error("FLIR,scanCameraID,emptyFrame,INVALID")
                self.cap.release()
                logger.info(f"FLIR,scanCameraID,id={targetID},INVALID")
                return self.scanCameraID(targetID+1)
            except Exception as e:
                logger.error(str(e))
            return None
        raise BaseException("ERROR: Flir Camera can't be opened, Try to restart the programs or replug the device")
    
    def release(self):
        self.cap.release()
        logger.info("FLIR,release,closing flir camera,DONE")

    def safeCrop(self, frame):
        return frame[self.ymin:self.ymax, self.xmin:self.xmax]
    
    def read(self):
        logger.debug("FLIR,readRaw,START")
        _,frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        try:
            if self.enableResize:
                frame = cv2.resize(frame, (self.width, self.height))
            frame = self.safeCrop(frame)
            logger.debug("FLIR,readRaw,status=SUCCEED,END")
            return ThermalFrame(frame)
        except Exception as e:
            logger.error(str(e))
            logger.debug("FLIR,readRaw,status=FAILED,END")
            raise BaseException("Empty Frame : Try to restart the programs or replug the device")

    def getTemp(self, frame, box):
        logger.debug("FLIR,getTemp,START")
        try:
            box = self.cvtBoxColor2Thermal(box)            
            xcenter = int(box[0]+(box[2]/2))
            ycenter = int(box[1]+(box[3]/2))
            print(self.xmin, xcenter, self.xmax)
            print(self.ymin, ycenter, self.ymax)
            if self.xmin <= xcenter <= self.xmax and self.ymin <= ycenter <= self.ymax:
                roi = frame[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
                # print([box[0],box[0]+box[2], box[1],box[1]+box[3]])
                # roic = ThermalFrame(roi)
                # cv2.imshow("aaaa", roic.color)
                _, maxVal, _, _ = cv2.minMaxLoc(roi)
                # temp = round((maxVal - 27315)/100.,1)
                temp = (maxVal - 27315)/100.
                logger.debug(f"FLIR,getTemp,value={temp},END")
                return temp
        except Exception as e:
            logger.error(str(e))
        logger.debug(f"FLIR,getTemp,FAILED,END")
        return 0
    
    def calibrateTemp(self, temp, dist):
        logger.debug("FLIR,calibrateTemp,START")
        if self.tempRange[0] <= temp <= self.tempRange[1] and self.distRange[0] <= dist <= self.distRange[1]:
            pd = self.polyDist
            pt = self.polyTemp
            # distance correction
            # calTemp = temp+self.applyPolynom(dist, self.polyDist)
            # distCor = (pd[0]*(dist**2))+(pd[1]*dist)+pd[2]
            distCor = (pd[0]*(dist**2))+(pd[1]*dist)+pd[2]
            calTemp = temp+distCor
            logger.debug(f"FLIR,distanceCorrection,temp={temp},dist={dist},calTemp={calTemp},distCor={distCor},DONE")

            # temp correction
            # calTemp = self.applyPolynom(calTemp, self.polyTemp)
            calTemp = (pt[0]*(calTemp**2))+(pt[1]*calTemp)+pt[2]
            logger.debug(f"FLIR,tempCorrection,temp={temp},calTemp={calTemp},DONE")

            logger.debug(f"FLIR,calibrateTemp,valid,temp={calTemp},END")
            return round(calTemp,1)

        logger.debug(f"FLIR,calibrateTemp,invalid,END")
        return 0

    def applyPolynom(self, initVal, polyvals):
        ln = len(polyvals)
        res = 0
        for val in polyvals:
            ln -= 1
            res += (initVal**ln)*val
        return res
    
    def getCalibratedThermalFrameFactor(self):
        # format [[offsetX, offsetY], [calWidth, calHeight]]
        if(Frame.color.w == 1920 and Frame.color.h == 1080):
            # return [[350,175], [1440,1050]] # for jetson
            # return [[350,120], [1435,960]] # for PC
            return [[-80,190], [1420,960]] # for PC
        elif(Frame.color.w == 1280 and Frame.color.h == 720):
            return [[185,75], [965, 705]] # for jetson
            # return [[225,75], [970, 690]] # for PC
        elif(Frame.color.w == 640 and Frame.color.h == 480):
            # return [[185,75], [965, 705]] # for jetson
            return [[225,75], [970, 690]] # for PC
        return [[], []]
    
    def cvtPointColor2Thermal(self, center):
        calThermal = self.getCalibratedThermalFrameFactor()
        x = int(((center[0]+calThermal[0][0])*1./calThermal[1][0])*Frame.thermal.w) + self.xmin
        y = int(((center[1]-calThermal[0][1])*1./calThermal[1][1])*Frame.thermal.h) + self.ymin
        return (x, y)
    
    def cvtBoxColor2Thermal(self, box):
        calThermal = self.getCalibratedThermalFrameFactor()
        x = int(((box[0]+calThermal[0][0])*1./calThermal[1][0])*Frame.thermal.w) + self.xmin
        y = int(((box[1]-calThermal[0][1])*1./calThermal[1][1])*Frame.thermal.h) + self.ymin
        w = int(box[2]*Frame.thermal.w/Frame.color.w)
        h = int(box[3]*Frame.thermal.h/Frame.color.h)
        return [x, y, w, h]
from .config import Frame, Scale
from .logger import logger
import pyrealsense2 as rs
import cv2
import numpy as np

from modules import config

class RealFrame():
    """
    RealSense Output Frame Handlers
    """
    def __init__(self, rsframe):
        color_data = rsframe.get_color_frame().as_frame().get_data()
        self.color = cv2.flip(np.asanyarray(color_data), 1)
        self.depth = rsframe.get_depth_frame()
        self.__coloredDepth = None
        self.__externalColoring = False
    
    @property
    def coloredDepth(self):
        return self.__getColorDepth

    @coloredDepth.setter
    def coloredDepth(self, frame):
        self.__coloredDepth = frame
        self.__externalColoring = True
        
    @coloredDepth.getter
    def __getColorDepth(self):
        if not self.__externalColoring:
            vframe = rs.colorizer().colorize(self.depth)
            color_data = vframe.as_frame().get_data()
            self.__coloredDepth = cv2.flip(np.asanyarray(color_data), 1)
        return self.__coloredDepth


class Camera():
    """
    RealSense Camera Handler :

    Main use :
    - read -> Get RealSense Frame Containing RGB and depth frame
    - release -> release RealSense Camera
    """
    def __init__(self, colorSize=[], depthSize=[]):
        logger.info("Camera,Instantiation,START")
        self.pipe = rs.pipeline()
        rsconfig = rs.config()
        rsconfig.enable_stream(rs.stream.color, colorSize[0], colorSize[1], rs.format.bgr8, 0)
        rsconfig.enable_stream(rs.stream.depth, depthSize[0], depthSize[1], rs.format.z16, 0)
        profile = self.pipe.start(rsconfig)
        profile.get_device().first_depth_sensor().set_option(rs.option.enable_auto_exposure, 1.)
        self.depthScale = Scale.getCalibratedDepthScale()
        self.depthOffsetX = int((Frame.depth.w-(Frame.depth.w*self.depthScale.x))/2)
        self.depthOffsetY = int((Frame.depth.h-(Frame.depth.h*self.depthScale.y))/2)
        self.distScanRange = 5
        logger.info("Camera,Instantiation,END")
    
    def read(self) -> RealFrame:
        rsframe = RealFrame(self.pipe.wait_for_frames())
        return rsframe
    
    def release(self):
        """
        Release active RealSense Camera
        """
        self.pipe.stop()
        logger.info("Camera,release,pipeline stopped")
    
    def getDepthFrameCoordinate(self, x, y):
        depthCenter = (
                int((x/Frame.color.w * Frame.depth.w*self.depthScale.x) + self.depthOffsetX),
                int((y/Frame.color.h * Frame.depth.h*self.depthScale.y) + self.depthOffsetY)
        )
        return depthCenter
    
    def getDepthFrameBox(self, box):
        """
        Convert box value from the main frame to the depth frame
        """
        x = int(((box[0] / Frame.color.w) * (Frame.depth.w*self.depthScale.x)) + self.depthOffsetX)
        y = int(((box[1] / Frame.color.h) * (Frame.depth.h*self.depthScale.y)) + self.depthOffsetY)
        w = int((box[2] / Frame.color.w) * (Frame.depth.w*self.depthScale.x))
        h = int((box[3] / Frame.color.h) * (Frame.depth.h*self.depthScale.y))
        return [x, y, w, h]
    
    def validateDepthFrameCoordinate(self, x, y):
        return self.depthOffsetX <= x <= Frame.depth.w-self.depthOffsetX and self.depthOffsetY <= y <= Frame.depth.h-self.depthOffsetY

    def getDistance(self, depthFrame, x, y):
        """
        Get distance from RealSense depth_frame in Meters
        """
        try:
            center = self.getDepthFrameCoordinate(x, y)
            if self.validateDepthFrameCoordinate(*center):
                cx = int(center[0]-self.distScanRange)
                cy = int(center[1]-self.distScanRange)
                minDist = 999999
                for ix in range(self.distScanRange*2):
                    for iy in range(self.distScanRange*2):
                        if 0 <= cx <= Frame.depth.w and 0 <= cy <= Frame.depth.h:
                            dist = depthFrame.get_distance(Frame.depth.w-cx+ix,cy+iy)
                            if 0 < dist < minDist: minDist = dist
                        cy += 1
                    cx += 1
                minDistCM = round(minDist*100,2)
                return minDistCM
        except Exception as e:
            logger.error(str(e))
        return 0
    
    def drawOnDepth(self, coloredDepthFrame, box):
        depthBox = self.getDepthFrameBox(box)
        coloredDepthFrame = cv2.rectangle(coloredDepthFrame, depthBox, (255,255,255), 2)
        return coloredDepthFrame
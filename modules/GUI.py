from .config import GUI as cfg, Tracker
from .logger import logger
import os, time
import cv2
import numpy as np


class GUIHandler():
    def __init__(self, windowName):
        self.initSession = True
        self.windowName = windowName
        self.mouseCenter = ()        
        self.pressed = False
        self.updateStat = False
        self.saveStat = False
        self.drawSaveCount = 0
        self.updateEntryStat = False
        self.updateExitStat = False
        self.entryPoint = ()
        self.exitPoint = ()
        self.drawBoundaryLineStat = False
        self.swapBoundary = Tracker.swap
        if self.checkAvailableConfig():
            self.loadConfig()
            self.updateStat = True
            self.drawBoundaryLineStat = True
    
    def loadConfig(self):
        self.entryPoint = (cfg.entryX, 0)
        self.exitPoint = (cfg.exitX, 0)

    def saveConfig(self):
        if self.updateEntryStat:
            cfg.entryX = self.entryPoint[0]
            self.updateEntryStat = False
        if self.updateExitStat:
            cfg.exitX = self.exitPoint[0]
            self.updateExitStat = False
        cfg.swapBoundary = self.swapBoundary
        self.saveStat = False

    def checkAvailableConfig(self):
        return cfg.entryX and cfg.exitX

    def refresh(self, frame, waitKey):
        windowStatus = self.checkKeypress(waitKey)
        cv2.setMouseCallback(self.windowName, self.handler)
        frame = self.drawBoundaryTransBox(frame)
        frame = self.drawAll(frame)
        frame = self.drawBoundary(frame)
        if self.saveStat:self.saveConfig()
        if self.initSession: 
            self.initSession = False
            self.updateStat = False
        cv2.imshow(self.windowName, frame)
        return windowStatus
    
    def checkKeypress(self, key):
        # logger.debug(f"GUIHandler,updateStat={self.updateStat}")
        if key > 0:            
            if key == ord("u"):
                self.updateStat = True
                self.drawBoundaryLineStat = True
            elif key == ord("b"):
                if not self.updateStat:
                    self.drawBoundaryLineStat = not self.drawBoundaryLineStat
            if self.updateStat:
                if key == ord("1"):
                    if not self.updateExitStat:                    
                        self.updateEntryStat = True
                elif key == ord("2"):
                    if not self.updateEntryStat:
                        self.updateExitStat = True
                elif key == ord("c"):
                    if self.updateEntryStat: self.entryPoint = ()
                    if self.updateExitStat: self.exitPoint = ()
                elif key == ord("s"):
                    if self.updateEntryStat or self.updateExitStat or cfg.swapBoundary != self.swapBoundary:
                        self.saveStat = True
                        self.drawSaveCount = 20                    
                elif key == ord("q"):
                    self.saveStat = False
                    self.drawSaveCount = 0
                    self.updateStat = False
                    self.updateEntryStat = False
                    self.updateExitStat = False
                elif key == ord("r"):
                    self.swapBoundary = not self.swapBoundary
            if key & 0xFF == 27:
                return False
        return True

    def handler(self, event, x, y, flags, params):
        self.mouseCenter = (x,y)
        if self.updateStat:
            if self.updateEntryStat:
                self.entryLineHandler(event, x, y)
            elif self.updateExitStat:
                self.exitLineHandler(event, x, y)
    
    def entryLineHandler(self, event, x, y):
        if not self.pressed:
            self.pressed = event == cv2.EVENT_LBUTTONDOWN
        else:
            if event == cv2.EVENT_LBUTTONUP:
                self.entryPoint = (x,y)
                self.pressed = False

    def exitLineHandler(self, event, x, y):
        if not self.pressed:
            self.pressed = event == cv2.EVENT_LBUTTONDOWN
        else:
            if event == cv2.EVENT_LBUTTONUP:
                self.exitPoint = (x,y)
                self.pressed = False
    
    def drawAll(self, frame):
        if self.updateStat:
            frame = self.drawUpdateSession(frame)
            frame = self.drawCursor(frame)
            frame = self.drawSaved(frame)
            frame = self.drawHelp(frame)
        return frame
    
    def drawBoundary(self, frame):
        if self.drawBoundaryLineStat:
            if self.entryPoint:
                frame = self.drawEntryLine(frame)
            if self.exitPoint:
                frame = self.drawExitLine(frame)
        return frame
    
    def drawBoundaryTransBox(self, frame):     
        if self.updateStat and self.drawBoundaryLineStat:
            black = np.zeros(frame.shape, np.uint8)
            if self.swapBoundary:
                trBoxEn = (self.entryPoint[0],0), (frame.shape[1], frame.shape[0])
                trBoxEx = (self.exitPoint[0],0), (0, frame.shape[0])
            else:
                trBoxEn = (self.entryPoint[0],0), (0, frame.shape[0])
                trBoxEx = (self.exitPoint[0],0), (frame.shape[1], frame.shape[0])
            cv2.rectangle(black, trBoxEn[0], trBoxEn[1], (255,255,10), -1)
            cv2.rectangle(black, trBoxEx[0], trBoxEx[1], (30,20,230), -1)
            frame = cv2.addWeighted(frame, 0.8, black, 0.5, 0)
        return frame

    def drawEntryLine(self, frame):
        if self.entryPoint:
            frame = cv2.line(frame, (self.entryPoint[0], 0), (self.entryPoint[0], frame.shape[0]), (255,255,10), 3)
        return frame
    
    def drawExitLine(self, frame):
        if self.exitPoint:
            frame = cv2.line(frame, (self.exitPoint[0], 0), (self.exitPoint[0], frame.shape[0]), (30,20,230), 3)
        return frame
    
    def drawUpdateSession(self, frame):
        origin = (frame.shape[1]//2, frame.shape[0]//10)
        offset = [300, 50]
        org11 = (origin[0]-offset[0], origin[1]-offset[1])
        org12 = (origin[0]+offset[0], origin[1]+offset[1])
        frame = cv2.rectangle(frame, org11, org12, (20,200,200), 2)
        frame = cv2.putText(frame, "UPDATE SESSION", (org11[0]+40, org12[1]-25), cv2.FONT_HERSHEY_SIMPLEX, 2, (20,200,200), 2)
        org2 = (origin[0]-offset[0], origin[1]+offset[1]+50)
        if self.updateEntryStat:
            frame = cv2.putText(frame, "UPDATE ENTRY LINE", org2, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,10), 2)
        elif self.updateExitStat:
            frame = cv2.putText(frame, "UPDATE EXIT LINE", org2, cv2.FONT_HERSHEY_SIMPLEX, 1, (30,20,230), 2)
        return frame

    def drawCursor(self, frame):
        if self.mouseCenter:
            frame = cv2.circle(frame, self.mouseCenter, 3, (5,5,255), -1)
            frame = cv2.circle(frame, self.mouseCenter, 8, (5,5,255), 2)
        return frame
    
    def drawSaved(self, frame):
        if self.drawSaveCount:
            self.drawSaveCount -= 1
            origin = ((frame.shape[1]//2)-200, (frame.shape[0]//2)-50)
            frame = cv2.putText(frame, "SAVED", origin, cv2.FONT_HERSHEY_SIMPLEX, 2, (5,250,20), 3)
        return frame

    def drawHelp(self, frame):
        s1 = "KEYS:"
        s2 = "  u -> enter update session"
        s3 = "  b -> enable/disable boundary show"
        s4 = "  1 -> set up entry line"
        s5 = "  2 -> set up exit line"
        s6 = "  s -> save boundary"
        s7 = "  r -> reverse/swap entry and exit"
        s8 = "  q -> exit update session"
        ss = [s1,s2,s3,s4,s5,s6,s7,s8]
        org = (int(frame.shape[1]*0.7), frame.shape[0]//15)
        frame = cv2.rectangle(frame, (org[0]-5, org[1]-25), (org[0]+350, org[1]+(15*len(ss))+5), (255,255,255), -1)
        frame = cv2.rectangle(frame, (org[0]-5, org[1]-25), (org[0]+350, org[1]+(15*len(ss))+5), (0,0,0), 2)
        for i,s in enumerate(ss):
            frame = cv2.putText(frame, s, (org[0], org[1]+(15*i)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
        return frame
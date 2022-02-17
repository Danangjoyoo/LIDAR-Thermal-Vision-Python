from . import camera, config, classifier, tracker, draw, flir, utils, GUI
from .logger import logger
import cv2, os, sys, time
import numpy as np
import pandas as pd
from worker import worker

kargv = utils.getKwargv()

@worker("ThermalExecutor")
def executeWithThermal():
    logger.info("Executor,MainProgram,useThermal=True,START")
    windowName = "eVision"
    fsize = config.Frame
    colorShape = [fsize.color.w, fsize.color.h]
    depthShape = [fsize.depth.w, fsize.depth.h]
    thermalShape = [fsize.thermal.w, fsize.thermal.h]

    logger.info("Executor,MainProgram,SettingUpCamera")
    rsCap = camera.Camera(colorShape, depthShape)
    flirCap = flir.FLIR(thermalShape[0], thermalShape[1])
    engine = classifier.FaceDetection(drawType=1, modelSelection=1, confidenceThresh=config.Mediapipe.detectionConfidence)
    guiHandler = GUI.GUIHandler(windowName)

    try:
        logger.info("Executor,MainProgram,Looping,START")
        nowTime = time.perf_counter()
        while 1:
            lastTime = nowTime
            nowTime = time.perf_counter()
            
            rsFrame = rsCap.read()
            tFrame = flirCap.read()

            detObjects = engine.detect(rsFrame.color)

            # rsFrame = draw.trackAndDraw_withTemp(rsFrame, tFrame, rsCap, flirCap, detObjects)
            rsFrame = draw.trackAndDraw_withTempAndBoundary(rsFrame, tFrame, rsCap, flirCap, detObjects, guiHandler)

            ## summary processing
            fps = 1/(nowTime-lastTime)
            rsFrame.color = cv2.putText(
                rsFrame.color, 
                f"FPS: {int(fps)}", 
                (config.Frame.color.w//25, config.Frame.color.h//15),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (5,5,255), 2)
            rsFrame.color = cv2.putText(
                rsFrame.color, f"Count: {tracker.TrackedObject.totalValidObject}", 
                (config.Frame.color.w//25, config.Frame.color.h-config.Frame.color.h//15),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (5,5,255), 2)

            ## final processing
            key = cv2.waitKey(1)
            if not guiHandler.refresh(rsFrame.color, key): break
            if kargv["depth_frame"]: cv2.imshow("depth",rsFrame.coloredDepth)
            if kargv["thermal_frame"]: cv2.imshow("thermal",tFrame.color)
    except Exception as e:
        raise e
    finally:
        cv2.destroyAllWindows()
        engine.close()
        flirCap.release()
        rsCap.release()
        logger.info("Executor,MainProgram,END")

@worker("NormalExecutor")
def execute():
    logger.info("Executor,MainProgram,useThermal=False,START")

    ## preparation
    windowName = "eVision"
    fsize = config.Frame
    colorShape = [fsize.color.w, fsize.color.h]
    depthShape = [fsize.depth.w, fsize.depth.h]
    rsCap = camera.Camera(colorShape, depthShape)
    engine = classifier.FaceDetection(drawType=1, modelSelection=1, confidenceThresh=config.Mediapipe.detectionConfidence)

    guiHandler = GUI.GUIHandler(windowName)

    try:
        logger.info("Executor,MainProgram,Looping,START")
        nowTime = time.perf_counter()
        while 1:
            lastTime = nowTime
            nowTime = time.perf_counter()
            
            ## core processing
            rsFrame = rsCap.read()
            detObjects = engine.detect(rsFrame.color)

            # rsFrame = draw.trackAndDraw(rsFrame, rsCap, detObjects)
            rsFrame = draw.trackAndDrawWithBoundary(rsFrame, rsCap, detObjects, guiHandler)

            ## summary processing
            fps = 1/(nowTime-lastTime)
            rsFrame.color = cv2.putText(
                rsFrame.color, 
                f"FPS: {int(fps)}", 
                (config.Frame.color.w//25, config.Frame.color.h//15),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (5,5,255), 2)
            rsFrame.color = cv2.putText(
                rsFrame.color, f"Count: {tracker.TrackedObject.totalValidObject}", 
                (config.Frame.color.w//25, config.Frame.color.h-config.Frame.color.h//15),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (5,5,255), 2)

            ## final processing
            key = cv2.waitKey(1)
            if not guiHandler.refresh(rsFrame.color, key): break
            if kargv["depth_frame"]: cv2.imshow("depth",rsFrame.coloredDepth)
    except Exception as e:
        raise e
    finally:
        cv2.destroyAllWindows()
        engine.close()
        rsCap.release()
        logger.info("Executor,MainProgram,END")   

def execute2():
    logger.info("Executor,MainProgram,useThermal=False,START")

    ## preparation
    windowName = "eVision"
    fsize = config.Frame
    colorShape = [fsize.color.w, fsize.color.h]
    depthShape = [fsize.depth.w, fsize.depth.h]
    rsCap = camera.Camera(colorShape, depthShape)
    engine = classifier.FaceDetection(drawType=1, modelSelection=1, confidenceThresh=config.Mediapipe.detectionConfidence)

    # guiHandler = GUI.GUIHandler(windowName)

    try:
        logger.info("Executor,MainProgram,Looping,START")
        nowTime = time.perf_counter()
        while 1:
            lastTime = nowTime
            nowTime = time.perf_counter()
            
            ## core processing
            rsFrame = rsCap.read()
            detObjects = engine.detect(rsFrame.color)

            rsFrame = draw.trackAndDraw(rsFrame, rsCap, detObjects)
            # rsFrame = draw.trackAndDrawWithBoundary(rsFrame, rsCap, detObjects, guiHandler)

            ## summary processing
            fps = 1/(nowTime-lastTime)
            rsFrame.color = cv2.putText(
                rsFrame.color, 
                f"FPS: {int(fps)}", 
                (config.Frame.color.w//25, config.Frame.color.h//15),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (5,5,255), 2)
            rsFrame.color = cv2.putText(
                rsFrame.color, f"Count: {tracker.TrackedObject.totalValidObject}", 
                (config.Frame.color.w//25, config.Frame.color.h-config.Frame.color.h//15),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (5,5,255), 2)

            ## final processing
            key = cv2.waitKey(1)
            # if not guiHandler.refresh(rsFrame.color, key): break
            cv2.imshow(windowName, rsFrame.color)
            if key > 0: break
            if kargv["depth_frame"]: cv2.imshow("depth",rsFrame.coloredDepth)
    except Exception as e:
        raise e
    finally:
        cv2.destroyAllWindows()
        engine.close()
        rsCap.release()
        logger.info("Executor,MainProgram,END")   

from modules.logger import logger
from modules.tracker import *
from modules import config, utils
import os, sys, time
import cv2

kargv = utils.getKwargv()


def trackAndDraw_withTemp(rsFrame, tFrame, rsCap, flirCap, detObjects):
    TrackedObject.refreshAll()
    for detObj in detObjects:
        trackedObj = TrackedObject.scanTrackedObject(detObj, flirCap)
        if not trackedObj.drawn:
            trackedObj.drawn = True
            box = detObj.box
            center = detObj.center

            # update temperature
            trackedObj.updateTemp(tFrame.frame16bit, box)

            # draw temp box
            if kargv["draw_thermal"]:
                tFrame.color = cv2.circle(tFrame.color, flirCap.cvtPointColor2Thermal(center), 5, (255,255,255), -1)
                tFrame.color = cv2.rectangle(tFrame.color, flirCap.cvtBoxColor2Thermal(box), (255,255,255), 2)

            # draw detection box
            if kargv["show_id"]:
                rsFrame.color = cv2.putText(rsFrame.color, f"ID: {trackedObj.id}", (box[0], box[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (5,255,20), 2)
            rsFrame.color = cv2.rectangle(rsFrame.color, box, (5,255,20), 2)

            # depth frame proc
            dist = rsCap.getDistance(rsFrame.depth, *center)

            # draw depth box
            if kargv["draw_depth"]:
                depthCenter = rsCap.getDepthFrameCoordinate(*center)
                rsFrame.coloredDepth = cv2.circle(rsFrame.coloredDepth, depthCenter, 5, (255,255,255), -1)
                rsFrame.coloredDepth = rsCap.drawOnDepth(rsFrame.coloredDepth, box)

            if dist:
                if kargv["show_distance"]:
                    # draw background
                    rsFrame.color = cv2.rectangle(
                        rsFrame.color,
                        (box[0], box[1]+box[3]),
                        (box[0]+180, box[1]+box[3]+40),
                        (255,255,255), -1
                    )
                else:
                    # draw background
                    rsFrame.color = cv2.rectangle(
                        rsFrame.color,
                        (box[0], box[1]+box[3]),
                        (box[0]+180, box[1]+box[3]+20),
                        (255,255,255), -1
                    )

                # draw temp C
                tempText = flirCap.calibrateTemp(trackedObj.temp, dist) if trackedObj.temp else "retrieving.."
                rsFrame.color = cv2.putText(
                    rsFrame.color,
                    "{:<5} : {} C".format("Temp", tempText),
                    (box[0]+2, box[1]+box[3]+15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
                
                if kargv["show_distance"]:
                    # draw distance cm
                    rsFrame.color = cv2.putText(
                        rsFrame.color,
                        "{:<5} : {} cm".format("dist", dist),
                        (box[0], box[1]+box[3]+30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

            else:
                # draw background
                rsFrame.color = cv2.rectangle(
                    rsFrame.color,
                    (box[0], box[1]+box[3]),
                    (box[0]+130, box[1]+box[3]+20),
                    (255,255,255), -1
                )

                # draw temp C
                tempText = trackedObj.temp if trackedObj.temp else "retrieving.."
                rsFrame.color = cv2.putText(
                    rsFrame.color,
                    "{:<5} : {} C".format("Temp", tempText),
                    (box[0]+2, box[1]+box[3]+15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
    return rsFrame


def trackAndDraw_withTempAndBoundary(rsFrame, tFrame, rsCap, flirCap, detObjects, guiHandler):
    TrackedObject.refreshAllWithBoundary(guiHandler.entryPoint[0], guiHandler.exitPoint[0])
    for detObj in detObjects:
        trackedObj = TrackedObject.scanTrackedObject(detObj, flirCap)
        if not trackedObj.drawn:
            trackedObj.drawn = True
            box = detObj.box
            center = detObj.center

            # update temperature
            trackedObj.updateTemp(tFrame.frame16bit, box)

            # draw temp box
            if kargv["draw_thermal"]:
                tFrame.color = cv2.circle(tFrame.color, flirCap.cvtPointColor2Thermal(center), 5, (255,255,255), -1)
                tFrame.color = cv2.rectangle(tFrame.color, flirCap.cvtBoxColor2Thermal(box), (255,255,255), 2)

            # depth frame proc
            dist = rsCap.getDistance(rsFrame.depth, *center)
            if config.Tracker.validDistanceCM:
                if dist > config.Tracker.validDistanceCM: continue

            # draw depth box
            if kargv["draw_depth"]:
                depthCenter = rsCap.getDepthFrameCoordinate(*center)
                rsFrame.coloredDepth = cv2.circle(rsFrame.coloredDepth, depthCenter, 5, (255,255,255), -1)
                rsFrame.coloredDepth = rsCap.drawOnDepth(rsFrame.coloredDepth, box)

            if dist:
                calTemp = trackedObj.getCalibratedTemp(dist)
                tempText = f"{calTemp} C" if calTemp else "retrieving.."
                lenTempText = 120 if calTemp else 185

                if kargv["show_distance"]:
                    # draw background
                    rsFrame.color = cv2.rectangle(
                        rsFrame.color,
                        (box[0], box[1]-80),
                        (box[0]+190, box[1]),
                        (255,255,255), -1)

                    # draw distance cm
                    rsFrame.color = cv2.putText(
                        rsFrame.color,
                        f"{dist} cm",
                        (box[0], box[1]-50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
                else:
                    # draw background
                    rsFrame.color = cv2.rectangle(
                        rsFrame.color,
                        (box[0], box[1]-40),
                        (box[0]+lenTempText, box[1]),
                        (255,255,255), -1)

                # draw temp C
                rsFrame.color = cv2.putText(
                    rsFrame.color,
                    tempText,
                    (box[0]+2, box[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)                

            else:
                # draw background
                rsFrame.color = cv2.rectangle(
                    rsFrame.color,
                    (box[0], box[1]-40),
                    (box[0]+120, box[1]),
                    (255,255,255), -1)

                # draw temp C
                # tempText = flirCap.calibrateTemp(trackedObj.temp, dist) if trackedObj.temp else "retrieving.."
                tempText = "retrieving.."
                rsFrame.color = cv2.putText(
                    rsFrame.color,
                    f"{tempText} C",
                    (box[0]+2, box[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

            # draw detection box
            if kargv["show_id"]:
                rsFrame.color = cv2.putText(rsFrame.color, f"ID: {trackedObj.id}", (box[0], box[1]+box[3]+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (5,255,20), 2)            
            rsFrame.color = cv2.rectangle(rsFrame.color, box, trackedObj.boxColor, 2)

    return rsFrame


def trackAndDraw(rsFrame, rsCap, detObjects):
    TrackedObject.refreshAll()
    for detObj in detObjects:
        trackedObj = TrackedObject.scanTrackedObject(detObj, None)
        if not trackedObj.drawn:
            trackedObj.drawn = True
            box = detObj.box
            center = detObj.center

            # draw detection box
            if kargv["show_id"]:
                rsFrame.color = cv2.putText(rsFrame.color, f"ID: {trackedObj.id}", (box[0], box[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (5,255,20), 2)
            rsFrame.color = cv2.rectangle(rsFrame.color, box, (5,255,20), 2)

            dist = rsCap.getDistance(rsFrame.depth, *center)

            # depth frame proc
            if kargv["draw_depth"]:
                depthCenter = rsCap.getDepthFrameCoordinate(*center)
                rsFrame.coloredDepth = cv2.circle(rsFrame.coloredDepth, depthCenter, 5, (255,255,255), -1)
                rsFrame.coloredDepth = rsCap.drawOnDepth(rsFrame.coloredDepth, box)

            if dist and kargv["show_distance"]:
                # draw background
                rsFrame.color = cv2.rectangle(
                    rsFrame.color,
                    (box[0], box[1]+box[3]),
                    (box[0]+180, box[1]+box[3]+20),
                    (255,255,255), -1
                )

                # draw distance cm
                rsFrame.color = cv2.putText(
                    rsFrame.color,
                    "{:<5} : {} cm".format("dist", dist),
                    (box[0], box[1]+box[3]+15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

    return rsFrame


def trackAndDrawWithBoundary(rsFrame, rsCap, detObjects, guiHandler):
    TrackedObject.refreshAllWithBoundary(guiHandler.entryPoint[0], guiHandler.exitPoint[0])
    for detObj in detObjects:
        trackedObj = TrackedObject.scanTrackedObject(detObj, None)
        if not trackedObj.drawn:
            trackedObj.drawn = True
            box = detObj.box
            center = detObj.center

            # draw detection box
            if kargv["show_id"]:
                rsFrame.color = cv2.putText(rsFrame.color, f"ID: {trackedObj.id}", (box[0], box[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (5,255,20), 2)
            rsFrame.color = cv2.rectangle(rsFrame.color, box, (5,255,20), 2)

            # depth frame proc
            dist = rsCap.getDistance(rsFrame.depth, *center)
            if config.Tracker.validDistanceCM:
                if dist > config.Tracker.validDistanceCM: continue

            if kargv["draw_depth"]:
                depthCenter = rsCap.getDepthFrameCoordinate(*center)
                rsFrame.coloredDepth = cv2.circle(rsFrame.coloredDepth, depthCenter, 5, (255,255,255), -1)
                rsFrame.coloredDepth = rsCap.drawOnDepth(rsFrame.coloredDepth, box)

            if dist and kargv["show_distance"]:
                # draw background
                rsFrame.color = cv2.rectangle(
                    rsFrame.color,
                    (box[0], box[1]+box[3]),
                    (box[0]+180, box[1]+box[3]+20),
                    (255,255,255), -1
                )

                # draw distance cm
                rsFrame.color = cv2.putText(
                    rsFrame.color,
                    "{:<5} : {} cm".format("dist", dist),
                    (box[0], box[1]+box[3]+15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

    return rsFrame
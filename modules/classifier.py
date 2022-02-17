from .config import Mediapipe as mpc
from .logger import logger
import os, sys, time
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection

class DetectedObject():
    """
    Detected Object Handler
    """
    def __init__(self, center, box):
        self.center = center
        self.box = box

class BaseClassifier():
    def __init__(self, engine, drawType):
        self.mpEngine = engine
        self.drawType = drawType
    
    def close(self):
        self.mpEngine.close()
        logger.info("Classifier,close,solution closed")

class FaceMesh(BaseClassifier):
    def __init__(self, drawType=0):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=mpc.maxObject,
            refine_landmarks=True,
            min_detection_confidence=mpc.detectionConfidence,
            min_tracking_confidence=mpc.trackingConfidence)
        BaseClassifier.__init__(self, self.face_mesh, drawType)

    def detectAndDraw(self, image):
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image)

        # Draw the face mesh annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        h, w, c = image.shape
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                if self.drawType==0:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_tesselation_style())
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_contours_style())
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_iris_connections_style())
                else:
                    for i, lm in enumerate(face_landmarks.landmark):
                        center = [int(lm.x*w), int(lm.y*h)]
                        image = cv2.circle(image, center, 2, (5,255,20), -1)
        image = cv2.flip(image, 1)
        return image

class FaceDetection(BaseClassifier):
    """
    Face Detection Engine using Mediapipe Solution
    """
    def __init__(self, drawType=0, modelSelection=0, confidenceThresh=0.5):
        self.face_detection = mp_face_detection.FaceDetection(
            model_selection=modelSelection, min_detection_confidence=0.5)
        BaseClassifier.__init__(self, self.face_detection, drawType)

    def detectAndDraw(self, image):
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(image)

        # Draw the face detection annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        h, w, c = image.shape
        if results.detections:
            for detection in results.detections:
                if self.drawType == 0:
                    mp_drawing.draw_detection(image, detection)
                else:
                    bbox = detection.location_data.relative_bounding_box
                    pt1 = [int(bbox.xmin*w), int(bbox.ymin*h)]
                    pt2 = pt1[0]+int(bbox.width*w), pt1[1]+int(bbox.height*h)
                    image = cv2.rectangle(image, pt1, pt2, (5,255,20), 2)
        
    def detect(self, image):
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(image)

        # Draw the face detection annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        h, w, c = image.shape
        objects = []
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box                                
                btopx = int(bbox.xmin*w)
                btopy = int(bbox.ymin*h)
                bw = int(bbox.width*w)
                bh = int(bbox.height*h)
                bx = int(btopx + (bw/2))
                by = int(btopy + (bh/2))
                bx2 = int(bx+mpc.centerOffset[0])
                by2 = int(by+mpc.centerOffset[1])
                bw2 = int(bw*mpc.boxScale[0])
                bh2 = int(bh*mpc.boxScale[1])
                btopx2 = bx2-(bw2//2)
                btopy2 = by2-(bh2//2)
                center = [bx2,by2]
                box = [btopx2,btopy2,bw2,bh2]
                objects.append(DetectedObject(center, box))
        return objects
import firebase_admin
from firebase_admin import credentials, firestore, exceptions
import config
import time
import env
import datetime
import cv2
import os
import shutil


class Firebase:
    def __init__(self, cert):
        """A Firebase handler for evision environment and configuration device.

        Args:
            cert (str): Certification key of firebase instance.
        """
        cred = credentials.Certificate(cert)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def __onSnapshot(self, col_snapshot, changes, read_time):
        for change in changes:
            data = change.document.to_dict()
            del data["searchable_name"]
            env.SHOW_MASKER_TYPE_PROBABILITY = data["showMaskerTypeProbability"]
            env.SHOW_MASKER_TYPE = data["showMaskerType"]
            env.ALERT_UNMASK = data["alertUnmask"]
            env.DEBUG_PI_TEMP = data["debug_pi_temp"]
            env.DEBUG_COORDINATE = data["debug_coordinate"]
            env.DEBUG_SKELETON = data["debug_skeleton"]
            env.DEBUG_CENTROID = data["debug_centroid"]
            env.SHOW_THERMAL_DATA = data["show_thermal_data"]
            env.MASK_DETECTION = True if "unmaskDetector" in data["fitur"] else False
            env.PEOPLE_COUNTER = True if "visitorCounter" in data["fitur"] else False
            env.COUNTER_MODE = data["counter_mode"]
            env.TEMPERATURE_HAND_DETECTION = data["temp_hand_detect"]
            env.TEMPERATURE_HEAD_DETECTION = data["temp_head_detect"]
            env.SHOW_TRACKING_LINES = data["show_tracking_lines"]
            env.SHOW_TOTAL_VISITOR = data["showTotalVisitor"]
            env.THERMAL_SCANNER = True if "thermal" in data["sensors"] else False
            env.THRESHOLD = float(data["threshold"])
            env.FOR_CLIENT = data["forClient"]
            env.SHOW_LOGO = data["showLogo"]

            env.DEBUG_CROP_BOX = data["debugCropBox"]
            # if env.DEBUG_CROP_BOX == True and data["debugCropBox"] == False:
            #     print("ok hide Thermal Head")
            #     cv2.destroyWindow("Thermal head")

            env.CROP_X1, env.CROP_Y1 = map(int, data["cropXy1"].strip("()").split(","))
            env.CROP_X2, env.CROP_Y2 = map(int, data["cropXy2"].strip("()").split(","))
            env.scaleFactorX = 1920 / (env.CROP_X2 - env.CROP_X1)
            env.scaleFactorY = 1080 / (env.CROP_Y2 - env.CROP_Y1)
            env.TARGET_VERSION = data["targetVersion"]
            env.COMPENSATE_TEMP = float(data["compensateTemp"])
            env.ALERT_SOUND_FEVER = data["alertFever"]
            env.MIN_WIDTH_FRONT_FACE = data["min_width_front_face"]
            env.MAX_WIDTH_FRONT_FACE = data["max_width_front_face"]
            env.MIN_WIDTH_SIDE_FACE = data["min_width_side_face"]
            env.MAX_WIDTH_SIDE_FACE = data["max_width_side_face"]
            print("[INFO] Connected to Firebase")

            self.__writeToFile(data)
            print("Pull New {}".format(data))

    def __writeToFile(self, data):
        f = open(os.path.join(os.getcwd(), "env_cache.py"), "w")
        f.write(f"SHOW_MASKER_TYPE = {data['showMaskerType']}\n")
        f.write(f"SHOW_MASKER_TYPE_PROBABILITY = {data['showMaskerTypeProbability']}\n")
        f.write(f"ALERT_UNMASK = {data['alertUnmask']}\n")
        f.write(f"DEBUG_PI_TEMP = {data['debug_pi_temp']}\n")
        f.write(f"DEBUG_COORDINATE = {data['debug_coordinate']}\n")
        f.write(f"DEBUG_SKELETON = {data['debug_skeleton']}\n")
        f.write(f"DEBUG_CENTROID = {data['debug_centroid']}\n")
        f.write(
            f"THERMAL_SCANNER = {True if 'thermal' in data['sensors'] else False}\n"
        )
        f.write(f"SHOW_THERMAL_DATA = {data['show_thermal_data']}\n")
        f.write(
            f"MASK_DETECTION = {True if 'unmaskDetector' in data['fitur'] else False}\n"
        )
        f.write(f"COUNTER_MODE = {data['counter_mode']}\n")
        f.write(
            f"PEOPLE_COUNTER = {True if 'visitorCounter' in data['fitur'] else False}\n"
        )
        f.write(f"TEMPERATURE_HAND_DETECTION = {data['temp_hand_detect']}\n")
        f.write(f"TEMPERATURE_HEAD_DETECTION = {data['temp_head_detect']}\n")
        f.write(f"SHOW_TRACKING_LINES = {data['show_tracking_lines']}\n")
        f.write(f"SHOW_TOTAL_VISITOR = {data['showTotalVisitor']}\n")
        f.write(f"THRESHOLD = {float(data['threshold'])}\n")
        f.write(f"FOR_CLIENT = '{data['forClient']}'\n")
        f.write(f"SHOW_LOGO = {data['showLogo']}\n")
        f.write("THERMAL_OFFSET_LOC = 5\n")
        f.write("MIRROR = True\n")
        f.write(f"DEBUG_CROP_BOX = {data['debugCropBox']}\n")
        f.write(f"CROP_X1 = {int(data['cropXy1'].strip('()').split(',')[0])}\n")
        f.write(f"CROP_Y1 = {int(data['cropXy1'].strip('()').split(',')[1])}\n")
        f.write(f"CROP_X2 = {int(data['cropXy2'].strip('()').split(',')[0])}\n")
        f.write(f"CROP_Y2 = {int(data['cropXy2'].strip('()').split(',')[1])}\n")
        f.write("TARGET_WIDTH = 640\n")
        f.write("TARGET_HEIGHT = 480\n")
        f.write(f"scaleFactorX = round(TARGET_WIDTH / (CROP_X2 - CROP_X1))\n")
        f.write(f"scaleFactorY = round(TARGET_HEIGHT / (CROP_Y2 - CROP_Y1))\n")
        f.write(f"TARGET_VERSION = '{data['targetVersion']}'\n")
        f.write(f"COMPENSATE_TEMP = {float(data['compensateTemp'])}\n")
        f.write(f"ALERT_SOUND_FEVER = {data['alertFever']}\n")
        f.write(f"MIN_WIDTH_FRONT_FACE = {data['min_width_front_face']}\n")
        f.write(f"MAX_WIDTH_FRONT_FACE = {data['max_width_front_face']}\n")
        f.write(f"MIN_WIDTH_SIDE_FACE = {data['min_width_side_face']}\n")
        f.write(f"MAX_WIDTH_SIDE_FACE = {data['max_width_side_face']}\n")
        f.close()
        print("[INFO] Written to env_cache.py")

    def trackPeopleTemperature(self, temperature):
        date = datetime.datetime.now()
        if not env.FOR_CLIENT:
            pass
        else:
            if temperature != None:
                try:
                    if temperature >= 36.4 and temperature <= 36.7:
                        self.db.collection("realtimeCounter").document(
                            env.FOR_CLIENT
                        ).collection(config.cameraid).document(
                            date.strftime("%Y%m%d")
                        ).set(
                            {
                                "date": date.strftime("%Y%m%d"),
                                "range1": firestore.Increment(1),
                                "totalVisitor": firestore.Increment(1),
                            },
                            merge=True,
                        )
                    elif temperature >= 36.8 and temperature <= 37.2:
                        self.db.collection("realtimeCounter").document(
                            env.FOR_CLIENT
                        ).collection(config.cameraid).document(
                            date.strftime("%Y%m%d")
                        ).set(
                            {
                                "date": date.strftime("%Y%m%d"),
                                "range2": firestore.Increment(1),
                                "totalVisitor": firestore.Increment(1),
                            },
                            merge=True,
                        )
                    elif temperature >= env.THRESHOLD:
                        # query counter up with feverPPL
                        self.db.collection("realtimeCounter").document(
                            env.FOR_CLIENT
                        ).collection(config.cameraid).document(
                            date.strftime("%Y%m%d")
                        ).set(
                            {
                                "date": date.strftime("%Y%m%d"),
                                "range3": firestore.Increment(1),
                                "totalVisitor": firestore.Increment(1),
                            },
                            merge=True,
                        )
                    else:
                        self.db.collection("realtimeCounter").document(
                            env.FOR_CLIENT
                        ).collection(config.cameraid).document(
                            date.strftime("%Y%m%d")
                        ).set(
                            {
                                "date": date.strftime("%Y%m%d"),
                                "range0": firestore.Increment(1),
                                "totalVisitor": firestore.Increment(1),
                            },
                            merge=True,
                        )
                except Exception:
                    print("[WARNING] Server maybe down or lost connections")
                    pass
            else:
                pass

    def listen(self):
        # [INFO] Read from cache file first
        try:
            f1 = os.path.join(os.getcwd(), "env_cache.py")
            f2 = os.path.join(os.getcwd(), "env.py")
            shutil.copy(f1, f2)
            print("[INFO] Read from env_cache.py")
        except FileNotFoundError:
            print("[WARNING] No env_cache.txt yet, use default value")

        # [INFO] Then if online, check if there are any updates from firestore
        try:
            data_rsp = self.db.collection("devices").document(config.cameraid)
            data_rsp.on_snapshot(self.__onSnapshot)
            time.sleep(5)
        except Exception as e:
            print(f"[WARNING] Connection error due to {e}")
        return self

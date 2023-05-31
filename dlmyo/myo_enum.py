# -*- coding: utf-8 -*-

from aenum import Enum


class UUID(Enum):
    GAP_SERVICE = "00001800-0000-1000-8000-00805f9b34fb"
    DEVICE_NAME = "00002a00-0000-1000-8000-00805f9b34fb"
    CONTROL_SERVICE = "d5060001-a904-deb9-4748-2c7f4a124842"
    FIRMWARE_INFO = "d5060101-a904-deb9-4748-2c7f4a124842"
    FIRMWARE_VERSION = "d5060201-a904-deb9-4748-2c7f4a124842"
    COMMAND = "d5060401-a904-deb9-4748-2c7f4a124842"
    IMU_SERVICE = "d5060002-a904-deb9-4748-2c7f4a124842"
    IMU_DATA = "d5060402-a904-deb9-4748-2c7f4a124842"
    CLASSIFIER_SERVICE = "d5060003-a904-deb9-4748-2c7f4a124842"
    CLASSIFIER_EVENT = "d5060103-a904-deb9-4748-2c7f4a124842"
    FV_SERVICE = "d5060004-a904-deb9-4748-2c7f4a124842"
    FV_DATA = "d5060104-a904-deb9-4748-2c7f4a124842"
    EMG_SERVICE = "d5060005-a904-deb9-4748-2c7f4a124842"
    EMG0_DATA = "d5060105-a904-deb9-4748-2c7f4a124842"
    EMG1_DATA = "d5060205-a904-deb9-4748-2c7f4a124842"
    EMG2_DATA = "d5060305-a904-deb9-4748-2c7f4a124842"
    EMG3_DATA = "d5060405-a904-deb9-4748-2c7f4a124842"

    def __str__(self):
        return str(self.value)  # pyright: ignore


class Arm(Enum):
    UNKNOWN = 0
    RIGHT = 1
    LEFT = 2
    UNSYNC = -1


class ClassifierEvent(Enum):
    SYNC = 1
    UNSYNC = 2
    POSE = 3
    UNLOCK = 4
    LOCK = 5
    SYNCFAIL = 6
    WARMUP = 7


class ClassifierMode(Enum):
    OFF = 0x00
    ON = 0x01


class ClassifierModelType(Enum):
    BUILTIN = 0
    CUSTOM = 1


class EMGMode(Enum):
    OFF = 0x00
    ON = 0x01
    SEND = 0x02
    SEND_RAW = 0x03


class Handle(Enum):
    IMU = 0x1C
    EMG = 0x27
    CLASSIFIER = 0x23


class HardwareRev(Enum):
    C = 1
    D = 2


class IMUMode(Enum):
    OFF = 0x00
    DATA = 0x01
    EVENTS = 0x02
    ALL = 0x03
    RAW = 0x04


class MotionEventType(Enum):
    TAP = 0


class Pose(Enum):
    REST = 0
    FIST = 1
    IN = 2
    OUT = 3
    SPREAD = 4
    TAP = 5
    UNSYNC = -1


class SKU(Enum):
    BLACK = 1
    WHITE = 2
    UNKNOWN = 0


class SyncResult(Enum):
    SYNC_FAILED_TOO_HARD = 1


class XDirection(Enum):
    UNKNOWN = 0
    WRIST = 1
    ELBOW = 2
    UNSYNC = -1

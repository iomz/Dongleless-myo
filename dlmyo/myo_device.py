# -*- coding: utf-8 -*-

from __future__ import print_function

import binascii
import logging
import struct
import time

from bluepy import btle

from .myo_enum import *
from .myo_services import Services
from .myo_state import *
from .quaternion import Quaternion


class Connection(btle.Peripheral):
    def __init__(self, mac):
        btle.Peripheral.__init__(self, mac)

        time.sleep(0.5)

        self.set_mode(EMGMode.OFF, IMUMode.DATA, ClassifierMode.ON)

        self.firmware = Firmware(self.readCharacteristic(0x17))
        # logging.debug("firmware version: %d.%d.%d.%d".format(struct.unpack("4h", self.firmware))

        self.name = self.readCharacteristic(0x03).decode("utf-8")
        logging.info(f"device name: {self.name}")

        # info = self.info()
        self.cmd(SleepMode().never())

        self.subscribe()

        self.resync()

    def battery(self):
        """Battery percentage"""
        return ord(self.readCharacteristic(0x11))

    def cmd(self, payload):
        """Send command to MYO (see Command class)"""
        self.writeCharacteristic(0x19, payload.data, True)

    def emg_mode(self, state=True):
        """Start to collect EMG data"""
        if not state:
            self.set_mode(EMGMode.OFF, IMUMode.DATA, ClassifierMode.ON)
        else:
            self.set_mode(EMGMode.ON, IMUMode.DATA, ClassifierMode.OFF)

    def info(self):
        info_dict = {}
        for service in self.getServices():  # btle.Peripheral
            uuid = binascii.b2a_hex(service.uuid.binVal).decode("utf-8")[4:8]
            service_name = Services.get(int(uuid, base=16), uuid)

            if service_name in ("1801", "0004", "0006"):  # unknown
                continue

            logging.info(str(service_name))

            # constract data for service
            data_dict = {}
            for char in service.getCharacteristics():
                c_uuid = binascii.b2a_hex(char.uuid.binVal).decode("utf-8")[4:8]
                num = int(c_uuid, base=16)
                name = Services.get(num, hex(num))
                if "EmgData" in name:
                    logging.info(name)
                    data_dict.update({name: ""})
                    continue
                if name in ("0x602", "0x104", "Command", "0x2a05"):  # TODO: make this more sense
                    logging.info(name)
                    data_dict.update({name: ""})
                    continue

                if char.supportsRead():
                    b = bytearray(char.read())
                    try:
                        if name in ("Info1", "Info2"):
                            b = list(b)
                        elif name == "FirmwareVersion":
                            b = Firmware(b)
                        elif name == "HardwareInfo":
                            b = HardwareInfo(b)
                        elif name == "BatteryLevel":
                            b = b[0]
                            b = int(b)
                        else:  # if anything else, stringify the bytearray
                            b = str(list(b))
                            logging.debug(f"{name}: {b}")
                    except Exception as e:
                        logging.debug(f"{name}: {b} {e}")
                    logging.info(f"{name} {b}")
                    data_dict.update({name: b})
                    continue

                # TODO
                # not char.supportsRead()
                try:
                    b = bytearray(char.read())
                    if name in ("0x104", "ClassifierEvent"):  # TODO
                        b = list(b)
                    elif name == "IMUData":
                        b = IMU(b)
                    elif name == "MotionEvent":
                        b = MotionEvent(b)
                    else:
                        b = str(list(b))
                except:
                    logging.debug(f"{name}: {char.props}")
                    data_dict.update({name: char})
                    continue
                data_dict.update({name: b})
                # end char
            info_dict.update({service_name: data_dict})
            # end service
        return info_dict

    def resync(self):
        """Reset classifier"""
        self.set_mode(EMGMode.OFF, IMUMode.DATA, ClassifierMode.OFF)
        self.set_mode(EMGMode.OFF, IMUMode.DATA, ClassifierMode.ON)

    def set_mode(self, emg, imu, classifier):
        """Set mode for EMG, IMU, classifier"""
        self.cmd(SetMode(emg, imu, classifier))

    def set_leds(self, *args):
        """Set leds color
        [logoR, logoG, logoB], [lineR, lineG, lineB] or
        [logoR, logoG, logoB, lineR, lineG, lineB]"""

        if len(args) == 1:
            args = args[0]

        if len(args) == 2:
            payload = LED(args[0], args[1])
        elif len(args) == 6:
            payload = LED(args[0:3], args[3:6])
        else:
            raise Exception("Unknown payload for LEDs")
        self.writeCharacteristic(0x19, payload.data, True)

    def subscribe(self):
        """Subscribe to all notifications"""
        # Subscribe to imu notifications
        self.writeCharacteristic(Handle.IMU.value + 1, b"\x01\x00", True)  # pyright: ignore
        # Subscribe to classifier
        self.writeCharacteristic(Handle.CLASSIFIER.value + 1, b"\x02\x00", True)  # pyright: ignore
        # Subscribe to emg notifications
        self.writeCharacteristic(Handle.EMG.value + 1, b"\x01\x00", True)  # pyright: ignore

    def vibrate(self, length, strength=None):
        """Vibrate for x ms"""
        self.cmd(Vibration(length, strength))


class MyoDevice(btle.DefaultDelegate):
    def __init__(self, mac=None):
        btle.DefaultDelegate.__init__(self)
        # init Connection (btle.Peripheral)
        self.connection = Connection(mac=get_myo(mac))  # connect to a myo device
        # init MyoState
        self.state = MyoState(self.connection)
        self.state.arm = Arm.UNSYNC
        self.state.pose = Pose.UNSYNC
        self.state.x_direction = XDirection.UNSYNC

        self.connection.setDelegate(self)  # TODO: doc here
        self.connection.vibrate(1)  # TODO: doc here

    def handleNotification(self, cHandle, data):
        """
        Events = (
            "rest",
            "fist",
            "wave_in",
            "wave_out",
            "wave_left",
            "wave_right",
            "fingers_spread",
            "double_tap",
            "unknown",
            "arm_synced",
            "arm_unsynced",
            "orientation_data",
            "gyroscope_data",
            "accelerometer_data",
            "imu_data",
            "emg_data",
        )
        """
        try:
            handle_enum = Handle(cHandle)
        except:
            raise Exception(f"Unknown data handle + {str(cHandle)}")

        if handle_enum == Handle.CLASSIFIER:
            # sometimes gets the poses mixed up, if this happens, try wearing it in a different orientation.
            data = struct.unpack(">6b", data)
            try:
                ev_type = ClassifierEvent(data[0])
            except:
                raise Exception("Unknown classifier event: " + str(data[0]))
            if ev_type == ev_type.POSE:
                self.state.pose = pose(data[1])  # pyright: ignore
                if self.state.pose == Pose.UNSYNC:
                    self.state.synced = False
                    self.state.arm = Arm.UNSYNC
                    self.state.pose = Pose.UNSYNC
                    self.state.x_direction = XDirection.UNSYNC
                    self.state.startq = Quaternion(0, 0, 0, 1)
                else:
                    self.state.napq = self.state.imu.quat.copy()
                    self.on_pose(self.state)

            elif ev_type == ev_type.SYNC:
                self.state.synced = True
                # rewrite handles
                self.state.arm = arm(data[1])  # pyright: ignore
                self.state.x_direction = x_direction(data[2])  # pyright: ignore
                self.state.startq = self.state.imu.quat.copy()
                self.on_sync(self.state)

            elif ev_type == ev_type.UNSYNC:
                self.state.synced = False
                self.state.arm = Arm.UNSYNC
                self.state.x_direction = XDirection.UNSYNC
                self.state.pose = Pose.UNSYNC
                self.state.startq = Quaternion(0, 0, 0, 1)
                self.on_unsync(self.state)

            elif ev_type == ev_type.UNLOCK:
                self.on_unlock(self.state)

            elif ev_type == ev_type.LOCK:
                self.on_lock(self.state)

            elif ev_type == ev_type.SYNCFAIL:
                self.state.synced = False
                self.on_sync_failed(self.state)

            elif ev_type == ev_type.WARMUP:
                self.on_warmup(self.state)

        elif handle_enum == Handle.IMU:
            self.state.imu = IMU(data)
            self.on_imu(self.state)

        elif handle_enum == Handle.EMG:
            self.state.emg = EMG(data)
            self.on_emg(self.state)

        else:
            logging.error(f"Unknown data handle {cHandle}")

    def run(self):
        while True:
            self.connection.waitForNotifications(3)  # TODO: why `3`?

    def on_imu(self, state):  # callback
        logging.info(state.imu)
        pass

    def on_emg(self, state):  # callback
        logging.info(state.imu)
        pass

    def on_pose(self, state):  # callback
        logging.info(state.pose.name)

    def on_sync(self, state):  # callback
        logging.info(f"Arm synced: {state.synced}")

    def on_unsync(self, state):  # callback
        self.connection.writeCharacteristic(0x24, b"\x01\x00", True)
        self.connection.resync()
        logging.info(f"Arm synced: {state.synced}")

    def on_sync_failed(self, state):  # callback
        logging.info(f"Sync failed: {state}")

    def on_lock(self, state):  # callback
        logging.info(f"Lock: {state}")

    def on_unlock(self, state):  # callback
        logging.info(f"Unlock: {state}")

    def on_warmup(self, state):  # callback
        logging.info(f"Warmup complete: {state}")


def get_myo(mac=None) -> str:
    # when mac is given
    if mac != None:
        while True:
            for s in btle.Scanner(0).scan(1):
                if s.addr == mac:
                    return str(mac).upper()

    # otherwise, find a myo device
    while True:
        for s in btle.Scanner(0).scan(1):
            logging.info(f"scan device: {s.addr}")
            scan_data = s.getScanData()
            for num, name, data in scan_data:
                if num == 6 and data == "d5060001-a904-deb9-4748-2c7f4a124842":
                    logging.debug(f"{num} {name} {data}")
                    return str(s.addr).upper()

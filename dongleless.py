from __future__ import print_function

import binascii
import logging
import struct
import time

from bluepy import btle

import myo_dicts as md
from quaternion import Quaternion

# Author:
#    Max Leefer
# Contributor:
#   Siarhei Yorsh (MyrikLD)
# Source:
#    https://github.com/mamo91/Dongleless-myo
# Free to modify and use as you wish, so long as my name remains in this file.
# Special thanks to the support at Thalmic labs for their help, and to IanHarvey for bluepy


# Notes
# If the Myo is unsynced while the program is running, you will need to plug it in and let it fall asleep before poses will work again.
# Mixes up fist and wave in when worn on left arm with led toward elbow

# logging.basicConfig(filename='myo.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


class MyoState:
	def __init__(self, connector):
		self.connection = connector

		self.arm = md.arm.UNKNOWN
		self.pose = md.pose.REST
		self.x_direction = md.x_direction.ELBOW
		self.synced = False
		self.startq = Quaternion(0, 0, 0, 1)
		self.napq = Quaternion(0, 0, 0, 1)
		self.imu = md.IMU()
		self.emg = md.EMG()

	@property
	def otn(self):
		if self.pose not in ["rest", "unknown"]:
			return ~self.imu.quat * self.napq
		else:
			return self.imu.quat

	def __str__(self):
		if self.pose not in ["rest", "unknown"]:
			a = ~self.imu.quat * self.napq
			return str(self.pose) + " " + str(a.rpy)
		else:
			a = ~self.imu.quat * self.startq
			return str(a.rpy)


class Connection(btle.Peripheral):
	def __init__(self, mac):
		btle.Peripheral.__init__(self, mac)

		time.sleep(0.5)

		self.setMode(md.emg_mode.OFF, md.imu_mode.DATA, md.classifier_mode.ON)

		self.firmware = md.firmware(self.readCharacteristic(0x17))
		# print('firmware version: %d.%d.%d.%d' % struct.unpack('4h', fw))

		self.name = self.readCharacteristic(0x03).decode("utf-8")
		logging.info('device name: %s' % self.name)

		# info = self.info()
		self.cmd(md.SleepMode().never())

		self.subscribe()

		self.resync()

	def subscribe(self):
		""" Subscribe to all notifications """
		self.writeCharacteristic(md.handle.IMU.value + 1, b'\x01\x00', True)  # Subscribe to imu notifications
		self.writeCharacteristic(md.handle.CLASSIFIER.value + 1, b'\x02\x00', True)  # Subscribe to classifier
		self.writeCharacteristic(md.handle.EMG.value + 1, b'\x01\x00', True)  # Subscribe to emg notifications

	def battery(self):
		""" Battery % """
		return ord(self.readCharacteristic(0x11))

	def resync(self):
		""" Reset classifier """
		self.setMode(md.emg_mode.OFF, md.imu_mode.DATA, md.classifier_mode.OFF)
		self.setMode(md.emg_mode.OFF, md.imu_mode.DATA, md.classifier_mode.ON)

	def cmd(self, pay):
		""" Send command to MYO (see cmd class)"""
		self.writeCharacteristic(0x19, pay.data, True)

	def setMode(self, emg, imu, classifier):
		""" Set mode for EMG, IMU, classifier"""
		self.cmd(md.SetMode(emg, imu, classifier))

	def emg_mode(self, state=True):
		""" Start to collect EMG data """
		if not state:
			self.setMode(md.emg_mode.OFF, md.imu_mode.DATA, md.classifier_mode.ON)
		else:
			self.setMode(md.emg_mode.ON, md.imu_mode.DATA, md.classifier_mode.OFF)

	def vibrate(self, length, strength=None):
		""" Vibrate for x ms """
		self.cmd(md.Vibration(length, strength))

	def setLeds(self, *args):
		""" Set leds color
		[logoR, logoG, logoB], [lineR, lineG, lineB] or
		[logoR, logoG, logoB, lineR, lineG, lineB]"""

		if len(args) == 1:
			args = args[0]

		if len(args) == 2:
			pay = md.Led(args[0], args[1])
		elif len(args) == 6:
			pay = md.Led(args[0:3], args[3:6])
		else:
			raise Exception('Unknown data')
		self.writeCharacteristic(0x19, pay.data, True)

	def info(self):
		out = dict()

		services = self.getServices()

		for i in services:
			s = binascii.b2a_hex(i.uuid.binVal).decode('utf-8')[4:8]
			num = int(s, base=16)
			sname = md.services.get(num, s)

			if sname in ('1801', '0004', '0006'):  # unknown
				continue

			print(str(sname))

			ch = i.getCharacteristics()

			dat = dict()

			for c in ch:
				s = binascii.b2a_hex(c.uuid.binVal).decode('utf-8')[4:8]
				num = int(s, base=16)
				name = md.services.get(num, hex(num))
				if 'EmgData' in name:
					logging.info('\t%s' % (name))
					dat.update({name: ''})
					continue
				if name in ('0x602', '0x104', 'Command', '0x2a05'):
					logging.info('\t%s' % (name))
					dat.update({name: ''})
					continue

				if c.supportsRead():
					b = bytearray(c.read())
					try:
						if name in ('Info1', 'Info2'):
							b = list(b)
							logging.info('\t%s: %s' % (name, b))
							dat.update({name: b})
							continue
						elif name == 'FirmwareVersion':
							b = md.firmware(b)
							logging.info('\t%s: %s' % (name, b))
							dat.update({name: b})
							continue
						elif name == 'HardwareInfo':
							b = md.hardwareInfo(b)
							logging.info('\t%s: %s' % (name, b))
							dat.update({name: b})
							continue
						elif name == 'BatteryLevel':
							b = b[0]
							logging.info('\t%s: %s' % (name, b))
							dat.update({name: int(b)})
							continue
						else:
							logging.info('\t%s: %s' % (name, b))
							dat.update({name: str(b)})
					except Exception as e:
						logging.info('\t%s: %s' % (name, list(b)))
						dat.update({name: list(b)})
				else:
					try:
						b = bytearray(c.read())
						if name in ('0x104', 'ClassifierEvent'):
							b = list(b)
							logging.info('\t%s: %s' % (name, b))
							dat.update({name: b})
							continue
						if name == 'IMUData':
							b = md.IMU(b)
							logging.info('\t%s: %s' % (name, b))
							dat.update({name: b})
							continue
						if name == 'MotionEvent':
							b = md.motionEvent(b)
							logging.info('\t%s: %s' % (name, b))
							dat.update({name: b})
							continue

						logging.info('\t%s: %s' % (name, b))
						dat.update({name: list(b)})
					except:
						logging.info('\t%s: %s' % (name, c.props))
						dat.update({name: c})

			out.update({sname: dat})
		return out


class MyoDevice(btle.DefaultDelegate):
	def __init__(self, mac=None):
		btle.DefaultDelegate.__init__(self)
		self.connection = Connection(mac=getMyo(mac))

		self.connection.setDelegate(self)

		self.myo = MyoState(self.connection)

		self.connection.vibrate(1)

		self.myo.arm = md.arm(-1)
		self.myo.pose = md.pose(-1)
		self.myo.x_direction = md.x_direction(-1)

	def handleNotification(self, cHandle, data):
		try:
			handle = md.handle(cHandle)
		except:
			raise Exception('Unknown data handle +' % str(cHandle))

		if handle == handle.CLASSIFIER:
			# sometimes gets the poses mixed up, if this happens, try wearing it in a different orientation.
			data = struct.unpack('>6b', data)
			try:
				ev_type = md.classifierEvent(data[0])
			except:
				raise Exception('Unknown classifier event: ' + str(data[0]))
			if ev_type == ev_type.POSE:
				self.myo.pose = md.pose(data[1])
				if self.myo.pose == md.pose.UNSYNC:
					self.myo.synced = False
					self.myo.arm = md.arm(-1)
					self.myo.pose = md.pose(-1)
					self.myo.x_direction = md.x_direction(-1)
					self.myo.startq = Quaternion(0, 0, 0, 1)
				else:
					self.myo.napq = self.myo.imu.quat.copy()
					self.on_pose(self.myo)

			else:
				if ev_type == ev_type.SYNC:
					self.myo.synced = True

					# rewrite handles
					self.myo.arm = md.arm(data[1])
					self.myo.x_direction = md.x_direction(data[2])
					self.myo.startq = self.myo.imu.quat.copy()

					self.on_sync(self.myo)

				elif ev_type == ev_type.UNSYNC:
					self.myo.synced = False
					self.myo.arm = md.arm(-1)
					self.myo.x_direction = md.x_direction(-1)
					self.myo.pose = md.pose(-1)
					self.myo.startq = Quaternion(0, 0, 0, 1)

					self.on_unsync(self.myo)

				elif ev_type == ev_type.UNLOCK:
					self.on_unlock(self.myo)

				elif ev_type == ev_type.LOCK:
					self.on_lock(self.myo)

				elif ev_type == ev_type.SYNCFAIL:
					self.myo.synced = False
					self.on_sync_failed(self.myo)

				elif ev_type == ev_type.WARMUP:
					self.on_warmup(self.myo)

		elif handle == handle.IMU:
			self.myo.imu = md.IMU(data)
			self.on_imu(self.myo)

		elif handle == handle.EMG:
			self.myo.emg = md.EMG(data)
			self.on_emg(self.myo)

		else:
			logging.error("Unknown data handle %s" % cHandle)

	def run(self):
		while 1:
			self.connection.waitForNotifications(3)

	def on_imu(self, myo):
		pass

	def on_emg(self, myo):
		pass

	def on_pose(self, myo):
		logging.info(myo.pose)

	def on_sync(self, myo):
		logging.info("Arm synced")

	def on_unsync(self, myo):
		self.connection.writeCharacteristic(0x24, b'\x01\x00', True)
		self.connection.resync()
		logging.info("Arm unsynced")

	def on_lock(self, myo):
		logging.info('Lock')

	def on_unlock(self, myo):
		logging.info('Unlock')

	def on_sync_failed(self, myo):
		logging.info('Sync failed')

	def on_warmup(self, myo):
		logging.info('Warmup complite')


# take a list of the events.
events = ("rest", "fist", "wave_in", "wave_out", "wave_left", "wave_right",
          "fingers_spread", "double_tap", "unknown", "arm_synced", "arm_unsynced",
          "orientation_data", "gyroscope_data", "accelerometer_data", "imu_data", "emg_data")


def getMyo(mac=None):
	cnt = 0

	if mac != None:
		while True:
			for i in btle.Scanner(0).scan(1):
				if i.addr == mac:
					return str(mac).upper()
			cnt += 1
			logging.info('Try #%s', cnt)

	while True:
		scan_result = btle.Scanner(0).scan(1)
		for i in scan_result:
			logging.info('scan device: %s', i.addr)
			scan_data = i.getScanData()
			for num, name, data in scan_data:
				if num == 6 and data == 'd5060001-a904-deb9-4748-2c7f4a124842':
					return str(i.addr).upper()
		cnt += 1
		logging.info('Try #%s', cnt)


def run():
	while True:
		try:
			logging.info("Initializing bluepy connection")
			myo = MyoDevice()
			myo.on_pose = lambda x: print(x.pose.name)
			myo.on_emg = lambda x: print(x.emg)

			myo.connection.setLeds([0, 0, 0, 0, 0, 0])
			time.sleep(1)
			myo.connection.setLeds([255, 0, 0, 255, 0, 0])
			myo.connection.vibrate(1)
			time.sleep(1)
			myo.connection.setLeds([0, 255, 0], [0, 255, 0])
			myo.connection.vibrate(1)
			time.sleep(1)
			myo.connection.setLeds([0, 0, 255], [0, 0, 255])
			myo.connection.vibrate(1)
			time.sleep(1)

			logging.info("Emg mode ON")
			myo.connection.emg_mode()
			time.sleep(5)
			myo.connection.emg_mode(False)
			logging.info("Emg mode OFF")

			logging.info("Initialization complete.")
			while True:
				try:
					myo.run()
				except btle.BTLEException as e:
					logging.info(str(e))
					logging.info("Disconnected")
		except KeyboardInterrupt:
			logging.debug("KeyboardInterrupt")
			break


if __name__ == '__main__':
	run()

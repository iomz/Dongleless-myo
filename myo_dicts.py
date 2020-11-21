import struct

from enum import Enum

from quaternion import Quaternion
from vector import Vector


class Enum(Enum):
	def __int__(self):
		return self.value

	def __float__(self):
		return self.value


services = {
	0x1800: "InfoService",
	0x2a00: "Name",
	0x2a01: "Info1",
	0x2a04: "Info2",

	0x180f: "BatteryService",
	0x2a19: "BatteryLevel",

	0x0001: "ControlService",  # < Myo info service
	0x0101: "HardwareInfo",  # < Serial number for this Myo and various parameters which
	# < are specific to this firmware. Read-only attribute.
	# < See myohw_fw_info_t.
	0x0201: "FirmwareVersion",  # < Current firmware version. Read-only characteristic.
	# < See myohw_fw_version_t.
	0x0401: "Command",  # < Issue commands to the Myo. Write-only characteristic.
	# < See myohw_command_t.

	0x0002: "ImuDataService",  # < IMU service
	0x0402: "IMUData",  # < See myohw_imu_data_t. Notify-only characteristic. /*
	0x0502: "MotionEvent",  # < Motion event data. Indicate-only characteristic. /*

	0x0003: "ClassifierService",  # < Classifier event service.
	0x0103: "ClassifierEvent",  # < Classifier event data. Indicate-only characteristic. See myohw_pose_t. /***

	0x0005: "EmgDataService",  # < Raw EMG data service.
	0x0105: "EmgData1",  # < Raw EMG data. Notify-only characteristic.
	0x0205: "EmgData2",  # < Raw EMG data. Notify-only characteristic.
	0x0305: "EmgData3",  # < Raw EMG data. Notify-only characteristic.
	0x0405: "EmgData4",  # < Raw EMG data. Notify-only characteristic.

	0x180a: "CompanyService",
	0x2a29: "CompanyName"
}


class handle(Enum):
	IMU = 0x1C
	EMG = 0x27
	CLASSIFIER = 0x23


class pose(Enum):
	REST = 0
	FIST = 1
	IN = 2
	OUT = 3
	SPREAD = 4
	TAP = 5
	UNSYNC = -1


class sku(Enum):
	BLACK = 1
	WHITE = 2
	UNKNOWN = 0


class hardware_rev(Enum):
	C = 1
	D = 2


class cmd(object):
	cmd = 0x00

	@property
	def value(self):
		return []

	@property
	def data(self):
		return bytearray([self.cmd, len(self)]) + self.bytearray()

	def bytearray(self):
		return bytearray([i for i in self.value])

	def __len__(self):
		return len(self.value)

	def __str__(self):
		return str(type(self).__name__) + ': ' + str(self.value)


class SetMode(cmd):
	cmd = 0x01

	def __init__(self, data, imu=None, classifier=None):
		if hasattr(data, '__iter__'):
			self.emg = emg_mode(data[0])
			self.imu = imu_mode(data[1])
			self.classifier = classifier_mode(data[2])
		else:
			try:
				self.emg = emg_mode(data)
			except Exception as e:
				raise Exception('You need to install lib Enum34, not Enum')
			self.imu = imu_mode(imu)
			self.classifier = classifier_mode(classifier)

	@property
	def value(self):
		return self.emg.value, self.imu.value, self.classifier.value


class emg_mode(Enum):
	OFF = 0x00
	ON = 0x01
	SEND = 0x02
	SEND_RAW = 0x03


class imu_mode(Enum):
	OFF = 0x00
	DATA = 0x01
	EVENTS = 0x02
	ALL = 0x03
	RAW = 0x04


class classifier_mode(Enum):
	OFF = 0x00
	ON = 0x01


class DeepSleep(cmd):
	cmd = 0x04

	def __init__(self):
		self.data = list()

	@property
	def value(self):
		return self.data


class Vibration(cmd):
	cmd = 0x03

	def __init__(self, data, strength=None):
		if type(data) == int:
			if strength is None:
				if data not in range(1, 4):
					raise Exception('Wrong vibration time')
				self.cmd = 0x03
			else:
				self.cmd = 0x07
			self.duration = data
			self.strength = strength
		elif len(data) == 2:
			self.cmd = 0x07
			self.duration = data[0]
			self.strength = data[1]
		else:
			raise Exception('Wrong data')

	@property
	def value(self):
		if self.cmd == 0x03:
			return list([self.duration])
		elif self.cmd == 0x07:
			return list([self.duration >> 0xFF, self.duration & 0xFF, self.strength])
		else:
			raise Exception('Wrong cmd')


class Led(cmd):
	cmd = 0x06

	def __init__(self, logo, line):
		"""[logoR, logoG, logoB], [lineR, lineG, lineB]"""
		if len(logo) != 3 or len(line) != 3:
			raise Exception('Led data: [r, g, b], [r, g, b]')

		self.logo = logo
		self.line = line

	@property
	def value(self):
		return list(self.logo) + list(self.line)


class SleepMode(cmd):
	cmd = 0x09

	def normal(self):
		self.mode = 0
		return self

	def never(self):
		self.mode = 1
		return self

	def __init__(self, mode=0x00):
		"""0 - normal, 1 - never sleep"""
		if mode not in [0, 1]:
			raise Exception('SleepMode: 0 - normal, 1 - never sleep')

		self.mode = mode

	@property
	def value(self):
		return list([self.mode])


class Unlock(cmd):
	data = 0x00

	cmd = 0x0A

	def lock(self):
		self.data = 0x00
		return self

	def timed(self):
		self.data = 0x01
		return self

	def hold(self):
		self.data = 0x02
		return self

	def __init__(self, data=0x02):
		self.data = data

	@property
	def value(self):
		return list([self.data])


class UserAction(cmd):
	data = 0x00

	cmd = 0x0B

	def __init__(self, data=0x00):
		self.data = data

	@property
	def value(self):
		return 0x00


class classifier_model_type(Enum):
	BUILTIN = 0
	CUSTOM = 1


class motion_event_type(Enum):
	TAP = 0


class motionEvent():
	def __init__(self, data):
		data = struct.unpack('3b', data)
		self.type = motion_event_type(data[0])
		self.dir = data[1]
		self.count = data[2]

	def __str__(self):
		return str(self.type) + ' to ' + str(self.dir) + ' x' + str(self.count)


class IMU:
	class Scale(Enum):
		ORIENTATION = 16384.
		ACCELEROMETER = 2048.
		GYROSCOPE = 16.

	def __init__(self, data=None):
		if data is not None:
			data = struct.unpack('<hhhhhhhhhh', data)
			self.accel = Vector(*[i / float(self.Scale.ACCELEROMETER) for i in data[4:7]])
			self.gyro = Vector(*[i / float(self.Scale.GYROSCOPE) for i in data[7:]])
			self.quat = Quaternion([i / float(self.Scale.ORIENTATION) for i in data[:4]])
		else:
			self.accel = Vector()
			self.gyro = Vector()
			self.quat = Quaternion()

	def __str__(self):
		return str(self.quat)


class EMG:
	def __init__(self, data=None):
		if data is not None:
			data = struct.unpack('<8HB', data)  # an extra byte for some reason
			self.sample1 = data[:8]
			self.sample2 = data[9:]
		else:
			self.sample1 = list((0, 0, 0, 0))
			self.sample2 = list((0, 0, 0, 0))

	def __str__(self):
		return 'EMG'+str(self.sample1 + self.sample2)


class classifierEvent(Enum):
	SYNC = 1
	UNSYNC = 2
	POSE = 3
	UNLOCK = 4
	LOCK = 5
	SYNCFAIL = 6
	WARMUP = 7


class arm(Enum):
	UNKNOWN = 0
	RIGHT = 1
	LEFT = 2
	UNSYNC = -1


class x_direction(Enum):
	UNKNOWN = 0
	WRIST = 1
	ELBOW = 2
	UNSYNC = -1


class sync_result(Enum):
	SYNC_FAILED_TOO_HARD = 1


class firmware:
	def __init__(self, data):
		data = struct.unpack('4h', data)
		self.major = data[0]
		self.minor = data[1]
		self.patch = data[2]
		self.hardware_rev = hardware_rev(data[3])

	def __str__(self):
		s = str()
		s += str(self.major) + '.'
		s += str(self.minor) + '.'
		s += str(self.patch) + '.'
		s += str(self.hardware_rev.name)
		return s


class hardwareInfo:
	def __init__(self, data):
		data = list(data)

		ser = list(data[:6])
		ser.reverse()
		ser = [hex(i)[-2:] for i in ser]
		self.serial_number = ':'.join(ser).upper()

		self.unlock_pose = pose(data[6])
		self.active_classifier_type = data[7]
		self.active_classifier_index = data[8]
		self.has_custom_classifier = data[9]
		self.stream_indicating = data[10]
		self.sku = sku(data[11])

	def __str__(self):
		return str(self.serial_number)


class Character:
	name = None

	def __init__(self, uuid):
		uuds = [i.value for i in UUID]
		if uuid in uuds:
			self.name = UUID(uuid).name
		self.uuid = uuid


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
		return str(self.value)

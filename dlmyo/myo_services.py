# -*- coding: utf-8 -*-

Services = {
    0x1800: "InfoService",
    0x2A00: "Name",
    0x2A01: "Info1",
    0x2A04: "Info2",
    0x180F: "BatteryService",
    0x2A19: "BatteryLevel",
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
    0x180A: "CompanyService",
    0x2A29: "CompanyName",
}

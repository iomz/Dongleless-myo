# Dongleless Myo

For if you don't have your dongle but just need to use myo anyway, with a different dongle or you computer's built in bluetooth.

## Setup

Go through the setup for bluez and [bluepy](https://github.com/IanHarvey/bluepy), and run the bluepy test program to make sure it works.
(This step can be a bit of a pain).
Make sure the bluepy files are somewhere python can see.

Download project and put it somewhere convenient to import where it can import bluepy.

## Limitations

- Tested only on Linux OS
- Can't provide emg and pose data at the same time.

## Usage

To use, simply import dongleless.py from your project directory or somewhere on your path, and call dongleless.run with a dictionary from event names to functions which should be called to respond to them. A sample is included. Any event not in the dictionary will simply do nothing.

The myo argument to the functions represents the myo, but currently the only function it has is vibrate() which takes an int argument from 0-3 representing the vibration length.

## Troubleshooting

### Notes

If the Myo is unsynced while the program is running, you will need to plug it in and let it fall asleep before poses will work again.

Mixes up fist and wave in when worn on left arm with led toward elbow.

### Failed to execute mgmt cmd 'le on'

Use commands:

```bash
sudo setcap cap_net_raw+e  <PATH>/bluepy-helper
sudo setcap cap_net_admin+eip  <PATH>/bluepy-helper
```

### Failed to execute mgmt cmd 'scanend'

try to reboot ble:

```
sudo hciconfig hci0 down && sudo hciconfig hci0 up
```

or

```
sudo rfkill block 0 && sudo rfkill unblock 0
```

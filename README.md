# Dongleless Myo

For if you don't have your dongle but just need to use myo anyway, with a different dongle or you computer's built in bluetooth.


## Setup
Go through the setup for bluez and [bluepy](https://github.com/IanHarvey/bluepy), and run the bluepy test program to make sure it works. (This step can be a bit of a pain). Make sure the bluepy files are somewhere python can see.

Download project and put it somewhere convenient to import where it can import bluepy.


## Limitations
* Tested only on Linux OS

* Can't provide emg and pose data at the same time. 


## Usage
To use, simply import dongleless.py from your project directory or somewhere on your path, and call dongleless.run with a dictionary from event names to functions which should be called to respond to them. A sample is included. Any event not in the dictionary will simply do nothing.

The myo argument to the functions represents the myo, but currently the only function it has is vibrate() which takes an int argument from 0-3 representing the vibration length.

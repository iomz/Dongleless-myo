This project was originally created by [@mamo91](https://github.com/mamo91/Dongleless-myo), enhanced by [@MyrikLD](https://github.com/MyrikLD/Dongleless-myo), and I reimplemented it with Bleak: [dl-myo](https://github.com/iomz/dl-myo)

# donglelessl-myo (Dongleless Myo)

If you are fed up with the dongle and still need to use Myo anyway here's the right stuff to grab.

## Setup

Install bluez and [bluepy](https://github.com/IanHarvey/bluepy), and run the bluepy test program to make sure it works.

## Limitations

- Tested only on Linux OS
- Can't provide EMG and pose data at the same time.

## Usage

The Myo argument to the functions represents the myo, but currently the only function it has is vibrate() which takes an int argument from 0-3 representing the vibration length.

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

Try restarting the ble interface:

```
sudo hciconfig hci0 down && sudo hciconfig hci0 up
```

or

```
sudo rfkill block 0 && sudo rfkill unblock 0
```

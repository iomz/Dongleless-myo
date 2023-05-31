#!/usr/bin/env python3
"""dl-myo example ws_host.py"""

import argparse
import asyncio
import json
import logging
import time

from bluepy import btle
from websockets.server import serve

from dlmyo import MyoDevice

# logging.basicConfig(filename="myo.log", level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


class MyoServer(object):
    def __init__(self):
        logging.info("initializing Myo connection")
        self.myo = MyoDevice()
        # myo.on_pose = lambda x: print(x.pose.name)
        # myo.on_emg = lambda x: print(x.emg)

    def warmup(self):
        self.myo.connection.set_leds([0, 0, 0, 0, 0, 0])
        time.sleep(1)
        self.myo.connection.set_leds([255, 0, 0, 255, 0, 0])
        self.myo.connection.vibrate(1)
        time.sleep(1)
        self.myo.connection.set_leds([0, 255, 0], [0, 255, 0])
        self.myo.connection.vibrate(1)
        time.sleep(1)
        self.myo.connection.set_leds([0, 0, 255], [0, 0, 255])
        self.myo.connection.vibrate(1)
        time.sleep(1)
        logging.info("warmup complete.")

    def start(self):
        logging.info("EMG mode ON")
        self.myo.connection.emg_mode()
        try:
            self.myo.run()
        except btle.BTLEException as e:
            logging.info(str(e))
            logging.info("Disconnected")

    def stop(self):
        self.myo.connection.emg_mode(False)
        logging.info("EMG mode OFF")


async def register(websocket):
    global CONNECTIONS, MS
    if MS is None:
        return
    try:
        # Register client
        CONNECTIONS.add(websocket)
        # Manage state changes
        async for message in websocket:
            event = json.loads(message)
            if event["action"] == "scan":
                await websocket.send("scan")
                # websockets.broadcast(CONNECTIONS, "scan")
            elif event["action"] == "disconnect":
                await websocket.send("disconnect")
            elif event["action"] == "connect":
                await websocket.send("connect")
            elif event["action"] == "start":
                MS.start()
                await websocket.send("start")
                print("start")
            elif event["action"] == "warmup":
                MS.warmup()
                await websocket.send("warmup")
            elif event["action"] == "stop":
                MS.stop()
                await websocket.send("stop")
                print("stop")
            else:
                await websocket.send(f"Unsupported event: {event}")
                logging.error(f"Unsupported event: {event}")
        await websocket.wait_closed()
    finally:
        # Unregister user
        CONNECTIONS.remove(websocket)


CONNECTIONS = set()
MS = None


async def main():
    global MS
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="connect to a Myo band and stream via websockets",
    )
    parser.add_argument("--address", "-a", help="the host IP address for msgpack server", default="127.0.0.1")
    parser.add_argument("--port", "-p", help="the port for msgpack listener", default=8765)

    args = parser.parse_args()

    logging.info(f"connecting to a Myo ...")
    MS = MyoServer()

    logging.info(f"listening {args.address}:{args.port} ...")
    async with serve(register, args.address, args.port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())

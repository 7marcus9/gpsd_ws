#!/usr/bin/env python3
import asyncio
import websockets
import gpsd
from time import sleep

print("Waiting for GPS")
gpsd.connect()
waitForGps = True
while waitForGps:
	try:
		packet = gpsd.get_current()
		if packet.mode >= 2:
			waitForGps = False
	except e:
		print(e)
print(packet.position())

print("Connecting to WS Server")

async def wsLoop():
	async with websockets.connect('ws://localhost:8765') as websocket:
		await websocket.send('{"type": "debug", "msg": "Python GPSD Connected"}')
		print("Connected")
		while websocket.open:
			await websocket.send('{{"type": "position", "lat": {0}, "lon": {1}, "head": 0}}'.format(*packet.position()))
			sleep(1)

asyncio.get_event_loop().run_until_complete(wsLoop())

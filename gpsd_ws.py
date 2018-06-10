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
	except Exception as e:
		print(e)
		sleep(1)
print(packet.position())

print("Connecting to WS Server")

async def wsLoop():
	async with websockets.connect('ws://localhost:8765') as websocket:
		await websocket.send('{"type": "debug", "msg": "Python GPSD Connected"}')
		print("Connected")
		while websocket.open:
			try:
				packet = gpsd.get_current()
				if packet.mode > 2:
					print(packet.movement())
					await websocket.send('{{"type": "position", "lat": {0}, "lon": {1}, "head": {2}}}'.format(*packet.position(), packet.movement()['track']))
				else:
					await websocket.send('{{"type": "position", "lat": {0}, "lon": {1}, "head": 0}}'.format(*packet.position()))
			except Exception as e:
				print(e)
				await websocket.send('{"type": "debug", "msg": "Python GPSD Error"}')
			sleep(1)

asyncio.get_event_loop().run_until_complete(wsLoop())

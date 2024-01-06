import asyncio
import websockets
#websocket client document
#https://websockets.readthedocs.io/en/11.0.3/reference/asyncio/client.html
CLIENTS = set()

async def handler(websocket):
	CLIENTS.add(websocket)
	async for message in websocket:
		print("接收到Client送來的："+message)
		await broadcast(message)
	# message = await websocket.recv() # Somehow this func only react to the onconnect message
	# print(message)
	try:
		await websocket.wait_closed()
	finally:
		CLIENTS.remove(websocket)

async def broadcast(message):
	for websocket in CLIENTS.copy():
		try:
			await websocket.send(message)
		except websockets.ConnectionClosed as e:
			print(e)

async def broadcast_messages():
	times=1
	while True:
		await asyncio.sleep(2)# wait 2 sec for every message
		message = "This is the "+str(times)+" times server send a message to device... "  # your application logic goes here
		times+=1
		print(message)
		await broadcast(message)
# async def handler(websocket):
#     while True:
#         message = await websocket.recv()
#         print(message)
async def main():
	async with websockets.serve(handler, "localhost", 1107):
		await broadcast_messages()  # runs forever
		

if __name__ == "__main__":
	asyncio.run(main())
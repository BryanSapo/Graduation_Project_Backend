import asyncio
from websockets.sync.client import connect
import websockets
url="ws://localhost:1108/hello"
print(websockets.__version__)
# def hello():
#     with connect("ws://localhost:1107") as websocket:
#         websocket.send("Hello world!")
#         message = websocket.recv()
#         print(f"Received: {message}")

async def lis():
    async for websocket in websockets.connect(url):
        try:
            async for message in websocket:
                print(message)
        except websockets.ConnectionClosed:
            continue
asyncio.run(lis())
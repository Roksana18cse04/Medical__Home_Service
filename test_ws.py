import asyncio
import websockets

async def test_ws():
    url = "ws://127.0.0.1:8000/patient/dashboard/audio_stream?token=YOUR_JWT"
    async with websockets.connect(url) as ws:
        await ws.send(b"Hello audio data!")
        msg = await ws.recv()
        print(msg)

asyncio.run(test_ws())

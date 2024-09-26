import asyncio
import websockets
import cv2

connected_clients = set()

async def register(websocket):
    connected_clients.add(websocket)

async def unregister(websocket):
    connected_clients.remove(websocket)

async def video_stream():
    # Open the camera
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Encode frame as JPEG
            encoded, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()
            # Send to all connected clients
            if connected_clients:
                # Make a copy of connected clients to avoid modification during iteration
                clients = connected_clients.copy()
                await asyncio.gather(*[send_frame(client, data) for client in clients])
            # Control frame rate (adjust sleep time as needed)
            await asyncio.sleep(0.03)  # Approximately 30 fps
    finally:
        cap.release()

async def send_frame(client, data):
    try:
        await client.send(data)
    except websockets.ConnectionClosed:
        await unregister(client)

async def handler(websocket, path):
    # Register client
    await register(websocket)
    try:
        # Keep the connection open
        await websocket.wait_closed()
    finally:
        await unregister(websocket)

async def main():
    # Start the WebSocket server
    async with websockets.serve(handler, '0.0.0.0', 8765):
        # Start sending frames
        await video_stream()

# Run the server
asyncio.run(main())

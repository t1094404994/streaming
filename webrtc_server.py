import asyncio
import json
import os

import cv2
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import aiohttp_cors

pcs = set()

class CameraVideoStreamTrack(VideoStreamTrack):
    """
    A video stream track that returns frames from a camera.
    """
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)  # Change the index if you have multiple cameras

    async def recv(self):
        frame = await self.next_timestamp()
        ret, img = self.cap.read()
        if not ret:
            raise Exception('Failed to read frame from camera')

        # Convert the image to VideoFrame
        from av import VideoFrame
        video_frame = VideoFrame.from_ndarray(img, format='bgr24')
        video_frame.pts = frame.pts
        video_frame.time_base = frame.time_base
        return video_frame

async def index(request):
    content = open('index.html', 'r').read()
    return web.Response(content_type='text/html', text=content)

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        print('ICE connection state is %s' % pc.iceConnectionState)
        if pc.iceConnectionState in ['failed', 'closed']:
            await pc.close()
            pcs.discard(pc)

    # Add the camera track
    pc.addTrack(CameraVideoStreamTrack())

    # Handle the offer and create an answer
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Return the answer to the client
    return web.Response(
        content_type='application/json',
        text=json.dumps({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        })
    )

async def on_shutdown(app):
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)

if __name__ == '__main__':
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get('/', index)
    app.router.add_post('/offer', offer)
    # Set up CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    
    # Configure CORS on all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    web.run_app(app, host='0.0.0.0', port=8080)

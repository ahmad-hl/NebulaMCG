#!/usr/bin/env python

import asyncio, websockets
from aiortc import RTCIceCandidate, MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import *
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder

async def hello():
    # Open webcam on Linux.
    # player = MediaPlayer('/dev/video0', format='v4l2', options={
    #     'video_size': '1920x1080'
    # })
    player = MediaPlayer('../WebRTC/foo.mp4')
    pc = RTCPeerConnection()
    pc.addTrack(player.video)

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    offer_json_obj = {'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type}
    print("server <<< {}".format(offer_json_obj))

    async with websockets.connect('ws://localhost:8765') as websocket:
        await websocket.send(json.dumps(offer_json_obj))

        server_answer_json = await websocket.recv()
        print(" server >>> {}".format(server_answer_json))

        answer = json.loads(server_answer_json)
        answer_sdp = RTCSessionDescription(answer["sdp"], answer["type"])
        if isinstance(answer_sdp, RTCSessionDescription):
            await pc.setRemoteDescription(answer_sdp)

asyncio.get_event_loop().run_until_complete(hello())
#!/usr/bin/env python
import asyncio, json
import websockets
from aiortc import RTCIceCandidate, MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder


async def negotiate(websocket, path):
    # Open webcam on Linux.
    player = MediaPlayer('/dev/video0', format='v4l2', options={
        'video_size': '1280x720'
    })
    # player = MediaPlayer('foo.mp4')
    pc = RTCPeerConnection()
    pc.addTrack(player.video)

    client_offer_request = await websocket.recv()
    offer = json.loads(client_offer_request)
    print("{} <<< client".format(offer))
    offer_sdp = RTCSessionDescription(offer["sdp"], offer["type"])
    if isinstance(offer_sdp, RTCSessionDescription):
        await pc.setRemoteDescription(offer_sdp)

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    answer_json_obj = {'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type}
    await websocket.send(json.dumps(answer_json_obj))
    print("{} >>> client".format(answer_json_obj))


start_server = websockets.serve(negotiate, '0.0.0.0', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
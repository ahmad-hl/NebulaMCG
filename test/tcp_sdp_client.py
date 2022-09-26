import socket
import argparse
import asyncio, json
from aiortc import RTCIceCandidate, MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
import asyncio

async def send_offer_rec_answer(servsocket):
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

    servsocket.sendall(json.dumps(offer_json_obj).encode("utf-8"))

    server_answer_json = servsocket.recv(4048)
    print(" server >>> {}".format(server_answer_json))

    answer = json.loads(server_answer_json)
    answer_sdp = RTCSessionDescription(answer["sdp"], answer["type"])
    if isinstance(answer_sdp, RTCSessionDescription):
        await pc.setRemoteDescription(answer_sdp)

    return pc

#init TCP socket to the client
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9999))

asyncio.get_event_loop().run_until_complete(send_offer_rec_answer(sock))
# asyncio.get_event_loop().run_forever()




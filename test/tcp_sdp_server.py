import socket
import argparse
import asyncio, json
from aiortc import RTCIceCandidate, MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder

async def rec_offer_send_answer(sendersocket):
    # Open webcam on Linux.
    player = MediaPlayer('/dev/video0', format='v4l2', options={
        'video_size': '1280x720'
    })
    # player = MediaPlayer('foo.mp4')
    pc = RTCPeerConnection()
    pc.addTrack(player.video)

    client_offer_request =  sendersocket.recv(4096)
    offer = json.loads(client_offer_request.decode("utf-8"))
    print("{} <<< client".format(offer))
    offer_sdp = RTCSessionDescription(offer["sdp"], offer["type"])
    if isinstance(offer_sdp, RTCSessionDescription):
        await pc.setRemoteDescription(offer_sdp)

    answer = await pc.createAnswer()
    await  pc.setLocalDescription(answer)

    answer_json_obj = {'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type}
    sendersocket.sendall(json.dumps(answer_json_obj).encode("utf-8"))
    print("{} >>> client".format(answer_json_obj))

    return pc

#init TCP socket to the client
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('', 9999))
serversocket.listen(5)

(sendersocket, address) = serversocket.accept()
asyncio.get_event_loop().run_until_complete(rec_offer_send_answer(sendersocket))
asyncio.get_event_loop().run_forever()
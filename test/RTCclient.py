import argparse
import asyncio
import logging
import math

import cv2, os
import numpy as np
from av import VideoFrame
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling
from aiortc import RTCIceCandidate, MediaStreamTrack, RTCPeerConnection, RTCSessionDescription

ROOT = os.path.dirname(__file__)

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track):
        super().__init__()  # don't forget this!
        self.track = track
        self.frame_no = 0


    async def recv(self):
        frame = await self.track.recv()
        try:
            # print(" frame type {} , frame {}".format(type(frame), frame))
            img = frame.to_ndarray(format="bgr24")
            rows, cols, _ = img.shape
            image = np.array(img)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray( image, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            print("recv: Video Frame Conversion {} received".format(self.frame_no))
            self.frame_no += 1

            # cv2.imwrite("frame%d.jpg" % self.frame_no, img)  # save frame as JPEG file
            cv2.imshow("frame",image)
            cv2.waitKey(1)
            return new_frame

        except Exception as ex:
            print(ex)
            pass

        self.frame_no += 1

        return frame

async def run(pc,player, recorder, signaling):

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            print("Audio Track %s received", track.kind)
        elif track.kind == "video":
            print("RUN: Video Track %s received".format(track.kind))
            local_track = VideoTransformTrack(track)
            pc.addTrack(local_track)
            if recorder != None:
                recorder.addTrack(local_track)

        @track.on("ended")
        async def on_ended():
            print("Track %s ended", track.kind)
            if recorder != None:
                await recorder.stop()

    # connect signaling
    await signaling.connect()

    # consume signaling
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            if recorder != None:
                await recorder.start()
            # send answer
            if obj.type == "offer":
                # pc.addTrack(VideoTransformTrack())
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)

        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
            print("ICE {} is established in Client".format(obj))
        elif obj is BYE:
            print("Exiting")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video stream from the command line")
    parser.add_argument("role", choices=["offer", "answer"])
    parser.add_argument("--play-from", help="Read the media from a file and sent it.")
    parser.add_argument("--record-to", help="Write received media to a file.")
    parser.add_argument("--verbose", "-v", action="count")
    add_signaling_arguments(parser)
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # create signaling and peer connection
    signaling = create_signaling(args)
    pc = RTCPeerConnection()

    # create media source
    if args.play_from:
        player = MediaPlayer(args.play_from)
    else:
        player = None
        # Open webcam on Linux.
        # player = MediaPlayer('/dev/video0', format='v4l2', options={
        #     'video_size': '640x480'
        # })

    # create media sink
    if args.record_to:
        recorder = MediaRecorder(args.record_to)
    else:
        recorder = None #MediaBlackhole()

    # run event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run(
                pc=pc,
                player=player,
                recorder=recorder,
                signaling=signaling
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        # cleanup
        loop.run_until_complete(signaling.close())
        loop.run_until_complete(pc.close())
        try:
            if recorder != None:
                loop.run_until_complete(recorder.stop())
            # loop.run_until_complete(player.stop())
        except:
            pass

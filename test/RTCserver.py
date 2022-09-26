import argparse
import asyncio
import logging
import math, time
import cv2
import numpy
from av import VideoFrame

from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling
from vidgear.gears.asyncio.helper import reducer
from vidgear.gears import ScreenGear
from aiortc import VideoStreamTrack


# create your own Bare-Minimum Custom Media Server
class Custom_RTCServer(VideoStreamTrack):
    """
    Custom Media Server using OpenCV, an inherit-class
    to aiortc's VideoStreamTrack.
    """

    def __init__(self, source=None):

        # don't forget this line!
        super().__init__()

        # initialize global params
        options = {"top": 0, "left": 0, "width": 1920, "height": 1080, "resolution":(1920,1080), "cap_prop_fps": 30} #1280 x 720, 1920 x 1080
        self.stream = ScreenGear(logging=True, **options).start()
        # self.stream = cv2.VideoCapture(source)
        # open video stream with default parameters
        self.frame_no = 0
        self.start_ts = time.time()
        self.fps = 0

    async def recv(self):
        """
        A coroutine function that yields `av.frame.Frame`.
        """
        # don't forget this function!!!

        # get next timestamp
        pts, time_base = await self.next_timestamp()
        self.frame_no += 1
        self.fps += 1
            # read video frame
        frame = self.stream.read()

        # check for frame if Nonetype
        if frame is None:
            self.terminate()

        if time.time() - self.start_ts > 1:
            print("FPS {} Frame {} at {} pts {}".format(self.fps, self.frame_no, time.time()*1000, pts))
            self.fps = 0
            self.start_ts = time.time()

        # reducer frames size if you want more performance otherwise comment this line
        frame = await reducer(frame, percentage=50)  # reduce frame by 30%

        # contruct `av.frame.Frame` from `numpy.nd.array`
        av_frame = VideoFrame.from_ndarray(frame,  format="bgr24")
        av_frame.pts = pts
        av_frame.time_base = time_base


        # return `av.frame.Frame`
        return av_frame

    def terminate(self):
        """
        Gracefully terminates VideoGear stream
        """
        # don't forget this function!!!

        # terminate
        if not (self.stream is None):
            self.stream.release()
            self.stream = None


async def run(pc, player, screenshare, recorder, signaling):
    def add_tracks():
        # if player and player.video:
        #     pc.addTrack(player.video)
        pc.addTrack(screenshare)

    @pc.on("track")
    def on_track(track):
        print("Receiving %s" % track.kind)

    # connect signaling
    await signaling.connect()

    # send offer
    add_tracks()
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)

    # consume signaling
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)

        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
            print("ICE {} is established ".format(obj))
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
        #     'video_size': '1920x1080'
        # })
    screenshareRTC = Custom_RTCServer()

        # create media sink
    if args.record_to:
        recorder = MediaRecorder(args.record_to)
    else:
        recorder = MediaBlackhole()

    # run event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run(
                pc=pc,
                player=player,
                screenshare=screenshareRTC,
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
            loop.run_until_complete(recorder.stop())
            if screenshareRTC:
                loop.run_until_complete(screenshareRTC.terminate())
            loop.run_until_complete(player.stop())
        except:
            pass
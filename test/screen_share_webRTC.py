# import necessary libs
import time

import uvicorn, asyncio, cv2
from av import VideoFrame
from vidgear.gears import ScreenGear
from aiortc import VideoStreamTrack
from vidgear.gears.asyncio import WebGear_RTC
from vidgear.gears.asyncio.helper import reducer

# initialize WebGear_RTC app without any source
web = WebGear_RTC(logging=True)

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


# assign your custom media server to config with adequate source (for e.g. foo.mp4)
web.config["server"] = Custom_RTCServer(source=0)

# assigning it
# run this app on Uvicorn server at address http://localhost:8000/
uvicorn.run(web(), host="0.0.0.0", port=8000)

# close app safely
web.shutdown()
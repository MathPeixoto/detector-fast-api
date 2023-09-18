import time

import cv2

from src.service.image_process import ImageDetector
import tempfile


class VideoDetector(ImageDetector):

    def __init__(self):
        super().__init__()
        self.writer = None
        self.frame = None

    def run(self, video):
        f = 0

        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video)

        self.video = cv2.VideoCapture(tfile.name)

        total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

        while True:
            ret, frame = self.video.read()
            self.frame = frame

            if not ret:
                break

            start = time.time()
            self.frame = super().run(frame)
            end = time.time()

            f += 1

            self.write_video()

            print('Frame number {0} took {1:.5f} seconds'.format(f, end - start))
            print('Frame number {0} / {1}'.format(f, total_frames))

        self.video.release()
        self.writer.release()

    def write_video(self):
        if self.writer is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')

            self.writer = cv2.VideoWriter('videos/result-traffic-cars.mp4', fourcc, 30,
                                     (self.frame.shape[1], self.frame.shape[0]), True)
        self.writer.write(self.frame)

    def load_image(self):
        if self.width is None or self.height is None:
            self.image_bgr = self.frame[:, :, :3]
            self.height, self.width = self.frame.shape[:2]
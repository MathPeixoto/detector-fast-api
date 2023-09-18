import time

import cv2

from src.service.image_process import ImageDetector
import tempfile


class VideoDetector(ImageDetector):

    def __init__(self, filename):
        super().__init__()
        self.writer = None
        self.frame = None
        self.filename = filename

    def run(self, video):
        f = 0

        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video)
        self.video = cv2.VideoCapture(tfile.name)

        total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

        start = time.time()
        while True:
            ret, frame = self.video.read()
            self.frame = frame

            if not ret:
                break

            processed_frame = super().run(frame)

            f += 1

            self.write_video(processed_frame)

            print(f'Frame number {f} / {total_frames}')

        end = time.time()

        print(f'Processing took {end - start:.5f} seconds')

        self.video.release()
        self.writer.release()

    def write_video(self, processed_frame):
        if self.writer is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.writer = cv2.VideoWriter('videos/' + self.filename, fourcc, 30,
                                     (processed_frame.shape[1], processed_frame.shape[0]), True)
        self.writer.write(processed_frame)

    def load_image(self):
        self.image_bgr = self.frame[:, :, :3]

        if self.width is None or self.height is None:
            self.height, self.width = self.frame.shape[:2]

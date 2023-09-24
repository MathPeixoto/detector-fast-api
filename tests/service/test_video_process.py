import tempfile
import unittest
from unittest.mock import patch, MagicMock, ANY

import numpy as np

from src.service.video_process import VideoDetector  # Change import path as needed


class TestVideoDetector(unittest.TestCase):

    def setUp(self):
        self.detector = VideoDetector("sample_video.mp4")

    @patch('cv2.VideoCapture')
    @patch('time.time')
    def test_run(self, mock_time, mock_video_capture):
        # Given
        mock_time.side_effect = [0, 1]
        mock_video = MagicMock()
        mock_video.read.side_effect = [(True, np.zeros((5, 5, 3), np.uint8)), (False, None)]
        mock_video.get.return_value = 1
        mock_video_capture.return_value = mock_video

        video_data = b"mock_video_data_here"
        self.detector.write_video = MagicMock()
        self.detector.load_image = MagicMock()
        self.detector.create_blob = MagicMock()
        self.detector.blob = np.zeros((1, 3, 224, 224), dtype=np.float32)
        self.detector.get_bounding_boxes = MagicMock()
        self.detector.non_maximum_suppression = MagicMock()
        self.detector.draw_boxes = MagicMock()
        self.detector.detector.forward_pass = MagicMock()

        # When
        with tempfile.NamedTemporaryFile(delete=False) as tfile:
            tfile.write(video_data)
            self.detector.run(video_data)

        # Then
        mock_video_capture.assert_called_with(ANY)
        self.detector.write_video.assert_called()
        self.assertEqual(mock_video.release.call_count, 1)
        self.assertEqual(mock_time.call_count, 2)

    @patch('cv2.VideoWriter')
    def test_write_video(self, mock_video_writer):
        # Given
        processed_frame = np.zeros((5, 5, 3), np.uint8)

        # When
        self.detector.write_video(processed_frame)

        # Then
        mock_video_writer.assert_called()
        self.detector.writer.write.assert_called_with(processed_frame)

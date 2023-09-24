import unittest
from io import BytesIO
from unittest.mock import mock_open, patch, Mock, MagicMock

import numpy as np

from src.service.image_process import ImageDetector


class TestImageDetector(unittest.TestCase):

    def setUp(self):
        self.mock_yolo = Mock()

        # Mock the `open` function used in `load_labels`
        m_open = mock_open(read_data='label1\nlabel2\n')
        self.patcher = patch('builtins.open', m_open)
        self.mock_open = self.patcher.start()

        self.detector = ImageDetector(detector=self.mock_yolo)

    def tearDown(self):
        self.patcher.stop()

    def test_init_sets_default_values(self):
        self.assertEqual(self.detector.probability_minimum, 0.7)
        self.assertEqual(self.detector.threshold, 0.4)
        self.assertEqual(self.mock_yolo, self.detector.detector)

    def test_load_labels(self):
        self.detector.load_labels()
        self.assertEqual(self.detector.labels, ["label1", "label2"])

    def test_load_image(self):
        with patch("cv2.imdecode") as mock_imdecode, \
                patch("src.service.yolo_v4.YOLOObjectDetection"):
            mock_imdecode.return_value = np.zeros((400, 400, 3), dtype=np.uint8)

            self.detector.image = b"some binary data"
            self.detector.load_image()

            self.assertEqual(self.detector.height, 400)
            self.assertEqual(self.detector.width, 400)

    def test_create_blob(self):
        self.detector.image_bgr = np.zeros((640, 640, 3), dtype=np.uint8)
        with patch('cv2.dnn.blobFromImage') as mock_blob:
            mock_blob.return_value = 'mock_blob'
            self.detector.create_blob()
            mock_blob.assert_called_once()
            self.assertEqual(self.detector.blob, 'mock_blob')

    def test_process_detected_objects(self):
        detected_objects = np.array([0, 0, 0, 0, 0, 0.5, 0.8])  # Assuming two classes
        self.detector.width = 640
        self.detector.height = 480
        self.detector.probability_minimum = 0.6
        self.detector.process_detected_objects(detected_objects)
        self.assertEqual(len(self.detector.bounding_boxes), 1)

    def test_calculate_box_coordinates(self):
        detected_objects = np.array([0.5, 0.5, 0.5, 0.5])  # Normalized coordinates
        self.detector.width = 640
        self.detector.height = 480
        coordinates = self.detector.calculate_box_coordinates(detected_objects)
        self.assertEqual(coordinates, [160, 120, 320, 240])

    def test_append_to_lists(self):
        self.detector.append_to_lists([160, 120, 320, 240], 0.8, 1)
        self.assertEqual(self.detector.bounding_boxes, [[160, 120, 320, 240]])
        self.assertEqual(self.detector.confidences, [0.8])
        self.assertEqual(self.detector.class_numbers, [1])

    @patch('cv2.dnn.NMSBoxes')
    def test_non_maximum_suppression(self, mock_nms):
        mock_nms.return_value = 'some_results'

        # Given
        self.detector.bounding_boxes = [[1, 2, 3, 4]]
        self.detector.confidences = [0.9]
        self.detector.probability_minimum = 0.5
        self.detector.threshold = 0.4

        # When
        self.detector.non_maximum_suppression()

        # Then
        mock_nms.assert_called_with([[1, 2, 3, 4]], [0.9], 0.5, 0.4)

        self.assertEqual('some_results', self.detector.results)

    @patch('cv2.rectangle')
    @patch('cv2.putText')
    def test_draw_single_box(self, mock_put_text, mock_rectangle):
        # Given
        index = 0
        self.detector.bounding_boxes = [[1, 2, 3, 4]]
        self.detector.colors = np.array([[255, 0, 0]])
        self.detector.class_numbers = [0]
        self.detector.labels = ['label']
        self.detector.confidences = [0.9]
        self.detector.image_bgr = np.zeros((10, 10, 3), np.uint8)

        # When
        self.detector.draw_single_box(index)

        # Then
        mock_rectangle.assert_called_once()
        mock_put_text.assert_called_once()

    @patch.object(ImageDetector, 'draw_single_box')
    def test_draw_boxes(self, mock_draw_single_box):
        # Given
        self.detector.results = np.array([[0], [1]])

        # When
        self.detector.draw_boxes()

        # Then
        self.assertEqual(mock_draw_single_box.call_count, 2)

    def test_run(self):
        # Given
        mock_image = 'image_data_here'
        mock_blob = 'mock_blob_here'  # Create a mock blob

        self.detector.load_image = MagicMock()
        self.detector.create_blob = MagicMock()
        self.detector.get_bounding_boxes = MagicMock()
        self.detector.non_maximum_suppression = MagicMock()
        self.detector.draw_boxes = MagicMock(return_value='boxes')

        # Manually set blob since create_blob() is mocked
        self.detector.blob = mock_blob

        # When
        result = self.detector.run(mock_image)

        # Then
        self.assertEqual(result, 'boxes')

    @patch('cv2.imencode')
    def test_nparray_to_bytes(self, mock_imencode):
        # Given
        np_array = np.array([[255, 255, 255], [0, 0, 0]], dtype='uint8')
        buffer = np.array([1, 2, 3, 4], dtype='uint8')  # Changed to a NumPy array
        mock_imencode.return_value = (True, buffer)

        # When
        result = self.detector.nparray_to_bytes(np_array)

        # Then
        assert isinstance(result, BytesIO)  # Assuming you want to check that the result is a BytesIO object

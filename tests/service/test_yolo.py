import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from src.service.yolo_v4 import YOLOObjectDetection  # Replace 'your_module' with the actual module name


class TestYOLOObjectDetection(unittest.TestCase):

    @patch('cv2.dnn.readNetFromDarknet')
    def test_load_network(self, mock_readNetFromDarknet):
        mock_net = MagicMock()
        mock_net.getLayerNames.return_value = ['layer1', 'layer2']
        mock_net.getUnconnectedOutLayers.return_value = [1, 2]
        mock_readNetFromDarknet.return_value = mock_net

        detector = YOLOObjectDetection()

        self.assertEqual(detector.config_path, 'resources/yolov4.cfg')
        self.assertEqual(detector.weights_path, 'resources/yolov4.weights')
        mock_readNetFromDarknet.assert_called_with('resources/yolov4.cfg', 'resources/yolov4.weights')
        self.assertEqual(detector.layers_names_all, ['layer1', 'layer2'])
        self.assertEqual(detector.layers_names_output, ['layer1', 'layer2'])

    @patch.object(YOLOObjectDetection, 'load_network')
    @patch('cv2.dnn.readNetFromDarknet')
    def test_forward_pass(self, mock_readNetFromDarknet, mock_load_network):
        mock_net = MagicMock()
        mock_output = "mock_output"
        mock_net.forward.return_value = mock_output
        mock_readNetFromDarknet.return_value = mock_net

        blob = np.zeros((1, 3, 416, 416), dtype=np.float32)

        detector = YOLOObjectDetection()
        detector.network = mock_net
        detector.layers_names_output = ['layer1', 'layer2']

        output = detector.forward_pass(blob)

        mock_net.setInput.assert_called_with(blob)
        mock_net.forward.assert_called_with(['layer1', 'layer2'])
        self.assertEqual(output, mock_output)

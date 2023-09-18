from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import cv2
import numpy as np

from src.service.yolo_v4 import YOLOObjectDetection


class ImageDetector:
    def __init__(self, detector=YOLOObjectDetection()):
        self.class_numbers = []
        self.confidences = []
        self.bounding_boxes = []
        self.image = None
        self.height = None
        self.width = None
        self.image_bgr = None

        self.labels_path = 'resources/coco.names'
        self.probability_minimum = 0.7
        self.threshold = 0.4

        self.detector = detector

        self.load_labels()

    def load_labels(self):
        with open(self.labels_path, 'r') as f:
            self.labels = [line.strip() for line in f]
        self.colors = np.random.randint(0, 255, size=(len(self.labels), 3), dtype='uint8')

    def load_image(self):
        np_array = np.frombuffer(self.image, np.uint8)
        self.image_bgr = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        self.height, self.width = self.image_bgr.shape[:2]

    def create_blob(self):
        self.blob = cv2.dnn.blobFromImage(self.image_bgr, 1 / 255.0, (640, 640), swapRB=True, crop=False)

    def get_bounding_boxes(self, output_from_network):
        with ThreadPoolExecutor() as executor:
            for result in output_from_network:
                executor.map(self.process_detected_objects, result)

    def process_detected_objects(self, detected_objects):
        scores = detected_objects[5:]
        class_current = np.argmax(scores)
        confidence_current = scores[class_current]

        if confidence_current > self.probability_minimum:
            box_coordinates = self.calculate_box_coordinates(detected_objects)
            self.append_to_lists(box_coordinates, confidence_current, class_current)

    def calculate_box_coordinates(self, detected_objects):
        box_current = detected_objects[0:4] * np.array([self.width, self.height, self.width, self.height])
        x_center, y_center, box_width, box_height = box_current
        x_min = int(x_center - (box_width / 2))
        y_min = int(y_center - (box_height / 2))
        return [x_min, y_min, int(box_width), int(box_height)]

    def append_to_lists(self, box_coordinates, confidence, class_number):
        self.bounding_boxes.append(box_coordinates)
        self.confidences.append(float(confidence))
        self.class_numbers.append(class_number)

    def non_maximum_suppression(self):
        self.results = cv2.dnn.NMSBoxes(self.bounding_boxes, self.confidences, self.probability_minimum, self.threshold)

    def draw_single_box(self, index):
        x_min, y_min, box_width, box_height = self.bounding_boxes[index]
        color = self.colors[self.class_numbers[index]].tolist()

        top_left = (x_min, y_min)
        bottom_right = (x_min + box_width, y_min + box_height)
        cv2.rectangle(self.image_bgr, top_left, bottom_right, color, 2)

        text = '{}: {:.2f}'.format(self.labels[int(self.class_numbers[index])], self.confidences[index])
        cv2.putText(self.image_bgr, text, (x_min, y_min - 5), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 1)

    def draw_boxes(self):
        if self.results is not None:
            for i in self.results.flatten():
                self.draw_single_box(i)
        return self.image_bgr

    def show_image(self):
        cv2.namedWindow('Detections', cv2.WINDOW_NORMAL)
        cv2.imshow('Detections', self.image_bgr)
        cv2.waitKey(0)
        cv2.destroyWindow('Detections')

    def run(self, image):
        self.class_numbers.clear()
        self.confidences.clear()
        self.bounding_boxes.clear()

        self.image = image
        self.load_image()
        self.create_blob()

        output_from_network = self.detector.forward_pass(self.blob)

        self.get_bounding_boxes(output_from_network)
        self.non_maximum_suppression()
        boxes = self.draw_boxes()
        return boxes

    def nparray_to_bytes(self, nparray):
        is_success, buffer = cv2.imencode(".png", nparray)
        if is_success:
            print("Image converted successfully into the Byte Array")
            
            io_buffer = BytesIO(buffer)
            return io_buffer
        else:
            print("Error converting image into the Byte Array")
            return None

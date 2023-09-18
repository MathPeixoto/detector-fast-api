import cv2


class YOLOObjectDetection:
    def __init__(self):
        self.config_path = 'resources/yolov4.cfg'
        self.weights_path = 'resources/yolov4.weights'
        self.load_network()

    def load_network(self):
        self.network = cv2.dnn.readNetFromDarknet(self.config_path, self.weights_path)
        self.layers_names_all = self.network.getLayerNames()
        self.layers_names_output = [self.layers_names_all[i - 1] for i in self.network.getUnconnectedOutLayers()]

    def forward_pass(self, blob):
        self.network.setInput(blob)
        return self.network.forward(self.layers_names_output)

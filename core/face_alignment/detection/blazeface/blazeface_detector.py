import os
import cv2
import torch
#from torch.utils.model_zoo import load_url

from ..core import FaceDetector

from .net_blazeface import BlazeFace
from .detect import *

import requests
import io


def load_numpy_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    data = np.load(io.BytesIO(response.content))  # Works!
    return data

"""
models_urls = {
    'blazeface_weights': 'https://github.com/hollance/BlazeFace-PyTorch/blob/master/blazeface.pth?raw=true',
    'blazeface_anchors': 'https://github.com/hollance/BlazeFace-PyTorch/blob/master/anchors.npy?raw=true'
}
"""
models_paths = {
    'blazeface_weights': 'core/face_alignment/checkpoints/blazeface.pth',
    'blazeface_anchors': 'core/face_alignment/checkpoints/anchors.npy'
}


class BlazeFaceDetector(FaceDetector):
    def __init__(self, device, path_to_detector=None, path_to_anchor=None, verbose=False):
        super(BlazeFaceDetector, self).__init__(device, verbose)

        # Initialise the face detector
        if path_to_detector is None:
            #model_weights = load_url(models_urls['blazeface_weights'])
            #model_anchors = load_numpy_from_url(models_urls['blazeface_anchors'])
            model_weights = load_url(models_paths['blazeface_weights'])
            model_anchors = load_numpy_from_url(models_paths['blazeface_anchors'])
        else:
            model_weights = torch.load(path_to_detector)
            model_anchors = np.load(path_to_anchor)

        self.face_detector = BlazeFace()
        self.face_detector.load_state_dict(model_weights)
        self.face_detector.load_anchors_from_npy(model_anchors, device)

        # Optionally change the thresholds:
        self.face_detector.min_score_thresh = 0.5
        self.face_detector.min_suppression_threshold = 0.3

        self.face_detector.to(device)
        self.face_detector.eval()

    def detect_from_image(self, tensor_or_path):
        image = self.tensor_or_path_to_ndarray(tensor_or_path)

        bboxlist = detect(self.face_detector, image, device=self.device)[0]

        return bboxlist

    def detect_from_batch(self, tensor):
        bboxlists = batch_detect(self.face_detector, tensor, device=self.device)
        return bboxlists

    @property
    def reference_scale(self):
        return 195

    @property
    def reference_x_shift(self):
        return 0

    @property
    def reference_y_shift(self):
        return 0

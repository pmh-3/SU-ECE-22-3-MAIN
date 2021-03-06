import os
import cv2
import logging
import numpy as np
from AbstractBaseClass.KeypointsGenerator import KeypointsGenerator
from ConcreteClass.MaskImage import MaskImage
from ConcreteClass.SiftKeypoints import SiftKeypoints


class SiftKeypointsGenerator(KeypointsGenerator):

    def __init__(self, config, maskGenerator=None):
        logging.info("Initializing keypoint generator")
        self.config = config
        self.maskGenerator = maskGenerator
        
        nfeatures = 3
        nOctaveLayers = 8
        contrastThreshold = 0.04
        edgeThreshold = 10
        sigma = .04

        self.sift = cv2.SIFT.create(
            nfeatures, #Default: 0
            nOctaveLayers, #* Default: 3
            contrastThreshold, #* Default: 0.04
            edgeThreshold, #* Default: 10
            sigma # Default: 1.6
        )

        print("!!!!!!!!!!!!!!!!!!!")
        print(nfeatures + nOctaveLayers + contrastThreshold + edgeThreshold + sigma)

        '''
        # SURF is pattented and is within the contribute packages
        # install opencv-contrib-python==4.4.0.44 in requirements.txt to use
        # this setting needs to be changed possibly with cmake flags: [OPENCV_ENABLE_NONFREE:BOOL=ON]
        # TODO: figure out how to change flags... Manual install of open cv? Via terminal?
        self.sift = cv2.xfeatures2d.SURF_create()
        self.create_kps_dir_if_not_exist()
        '''

    def create_kps_dir_if_not_exist(self):
        logging.info("Creating Sift directory")
        sift_dir = self.config.get("Keypoints.directory")
        if not os.path.exists(sift_dir):
            os.makedirs(sift_dir)

    def generate_and_save_keypoints_if_not_exist(self, imageObj):
        logging.info("Generating sift keypoints if not exist")
        kps_path = SiftKeypoints.generate_keypoints_path(self.config, imageObj.filename)
        if not os.path.isfile(kps_path):
            self.generate_and_save_keypoints(imageObj, kps_path)
        return kps_path

    def generate_and_save_keypoints(self, imageObj, kps_path=None):
        logging.info("Generating sift keypoints")
        if kps_path is None:
            kps_path = SiftKeypoints.generate_keypoints_path(self.config, imageObj.filename)
        maskObj = self.get_mask_if_mask_generator_exists(imageObj)
        keypoints, descriptors = self.compute_kps_and_desc(imageObj, maskObj)
        SiftKeypoints.save_keypoints_to_file(kps_path, keypoints, descriptors)
        return kps_path

    def get_mask_if_mask_generator_exists(self, imageObj):
        logging.info("Getting mask in the keypoint generator.")
        if self.maskGenerator is not None:
            mask_path = self.maskGenerator.generate_mask_if_not_exist(imageObj)
        else:
            mask = np.uint8(np.ones(imageObj.image.shape[:2])*255)
            mask_path = MaskImage.generate_mask_path(self.config, imageObj.filename)
            MaskImage.save_mask_to_file(mask_path, mask)
        return MaskImage(mask_path)

    def compute_kps_and_desc(self, imageObj, maskObj=None):
        logging.info("Generating keypoints")
        if maskObj is None:
            maskObj = MaskImage()
            maskObj.create_empty_mask(imageObj.image.shape[:2])
        keypoints, descriptors = self.sift.detectAndCompute(imageObj.image, maskObj.mask)
        return keypoints, descriptors

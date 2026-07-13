import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

class PoseExtractor:
    """Extracts human pose and segmentation masks using MediaPipe."""
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True
        )

    def extract(self, image: Image.Image):
        """
        Processes a PIL Image and returns the segmentation mask (agnostic mask).
        """
        img_np = np.array(image.convert("RGB"))
        results = self.pose.process(img_np)
        
        if not results.pose_landmarks or not results.segmentation_mask:
            raise ValueError("Could not detect a person in the image.")
            
        mask = results.segmentation_mask
        
        # Create an agnostic mask (white for the body, black for background)
        # In a real VTON, you'd refine this to only mask the torso/clothing area
        condition = np.stack((mask,) * 3, axis=-1) > 0.1
        bg_image = np.zeros(img_np.shape, dtype=np.uint8)
        
        # Where condition is true (person), make it white (this is the area to preserve/inpaint)
        agnostic_mask = np.where(condition, 255, bg_image).astype(np.uint8)
        
        return Image.fromarray(agnostic_mask).convert("L")

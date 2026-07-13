from PIL import Image
from src.features.pose_extractor import PoseExtractor
from src.models.diffusion_vton import DiffusionVTON
import logging

logger = logging.getLogger(__name__)

class TryOnPipeline:
    """End-to-End Orchestrator for Virtual Try-On."""
    def __init__(self, device="cpu"):
        self.pose_extractor = PoseExtractor()
        self.vton_model = DiffusionVTON(device=device)
        
    def process(self, person_image: Image.Image, garment_image: Image.Image) -> Image.Image:
        """
        1. Extract Pose and Agnostic Mask
        2. Run Diffusion Model
        """
        logger.info("Extracting Pose and Mask...")
        mask = self.pose_extractor.extract(person_image)
        
        logger.info("Running Diffusion Virtual Try-On...")
        result_image = self.vton_model.generate(person_image, garment_image, mask)
        
        logger.info("Try-On Complete.")
        return result_image

"""
Module 2: Medical Imaging Enhancement
Uses GenAI and Azure OpenAI to enhance medical image quality
"""

import os
import numpy as np
import cv2
from pathlib import Path
from typing import Optional, Tuple
import logging
import yaml
from dotenv import load_dotenv
from openai import AzureOpenAI
import base64
from io import BytesIO
from PIL import Image
import torch
import torch.nn as nn

load_dotenv()
logger = logging.getLogger(__name__)


class AzureImageEnhancer:
    """Use Azure OpenAI for medical image enhancement and analysis"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        self.vision_deployment = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT", "gpt-4-vision")
        self.gpt4_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    
    def encode_image(self, image: np.ndarray) -> str:
        """Encode image to base64 for API"""
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image.astype('uint8'))
        
        # Encode to base64
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
    
    def analyze_medical_image(self, image: np.ndarray, modality: str = "xray") -> str:
        """
        Analyze medical image using Azure OpenAI Vision
        Returns description and potential findings
        """
        try:
            img_base64 = self.encode_image(image)
            
            response = self.client.chat.completions.create(
                model=self.vision_deployment,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert radiologist analyzing a {modality} image. "
                                   "Provide detailed observations about image quality and visible structures."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analyze this {modality} medical image. Describe the image quality, "
                                        "visible anatomical structures, and any notable features."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return None
    
    def generate_enhancement_suggestions(self, image_analysis: str) -> str:
        """Generate suggestions for image enhancement based on analysis"""
        try:
            response = self.client.chat.completions.create(
                model=self.gpt4_deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in medical image processing. "
                                   "Suggest specific enhancement techniques."
                    },
                    {
                        "role": "user",
                        "content": f"Based on this image analysis:\n{image_analysis}\n\n"
                                   "Suggest specific image enhancement techniques (denoising, "
                                   "contrast adjustment, sharpening) that would improve diagnostic value."
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return None


class TraditionalImageEnhancer:
    """Traditional image enhancement techniques"""
    
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    def denoise(self, image: np.ndarray, method: str = "nlm") -> np.ndarray:
        """
        Apply denoising to medical image
        
        Methods:
        - nlm: Non-Local Means Denoising
        - gaussian: Gaussian Blur
        - bilateral: Bilateral Filter
        """
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Ensure uint8 format
        if image.dtype != np.uint8:
            image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
        
        if method == "nlm":
            return cv2.fastNlMeansDenoising(image, None, h=10, templateWindowSize=7, searchWindowSize=21)
        elif method == "gaussian":
            return cv2.GaussianBlur(image, (5, 5), 0)
        elif method == "bilateral":
            return cv2.bilateralFilter(image, 9, 75, 75)
        else:
            logger.warning(f"Unknown denoising method: {method}")
            return image
    
    def enhance_contrast(self, image: np.ndarray, method: str = "clahe") -> np.ndarray:
        """
        Enhance contrast of medical image
        
        Methods:
        - clahe: Contrast Limited Adaptive Histogram Equalization
        - histogram_eq: Global Histogram Equalization
        - adaptive: Adaptive Histogram Equalization
        """
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        if image.dtype != np.uint8:
            image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
        
        if method == "clahe":
            return self.clahe.apply(image)
        elif method == "histogram_eq":
            return cv2.equalizeHist(image)
        elif method == "adaptive":
            return cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(image)
        else:
            logger.warning(f"Unknown contrast method: {method}")
            return image
    
    def sharpen(self, image: np.ndarray) -> np.ndarray:
        """Apply sharpening filter"""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)
    
    def super_resolution(self, image: np.ndarray, scale_factor: int = 2) -> np.ndarray:
        """
        Simple super-resolution using interpolation
        For production, use deep learning models
        """
        height, width = image.shape[:2]
        new_size = (width * scale_factor, height * scale_factor)
        return cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)
    
    def edge_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Enhance edges for better structure visibility"""
        # Sobel edge detection
        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.sqrt(sobelx**2 + sobely**2)
        edges = ((edges - edges.min()) / (edges.max() - edges.min()) * 255).astype(np.uint8)
        
        # Combine with original
        enhanced = cv2.addWeighted(image, 0.7, edges, 0.3, 0)
        return enhanced


class DiffusionImageEnhancer:
    """
    Deep learning-based image enhancement using diffusion models
    This is a placeholder for actual diffusion model implementation
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
    
    def load_model(self):
        """Load pre-trained diffusion model"""
        # Placeholder - would load actual diffusion model
        logger.info("Diffusion model loading (placeholder)")
        # In production, use models like:
        # - Stable Diffusion for image enhancement
        # - Custom trained models on medical images
        pass
    
    def enhance(self, image: np.ndarray, prompt: str = None) -> np.ndarray:
        """
        Enhance image using diffusion model
        
        Args:
            image: Input medical image
            prompt: Text prompt for guided enhancement
        """
        # Placeholder implementation
        # In production, this would:
        # 1. Preprocess image for model input
        # 2. Run through diffusion model
        # 3. Apply denoising/enhancement
        # 4. Post-process output
        
        logger.info("Applying diffusion-based enhancement (placeholder)")
        return image


class MedicalImageEnhancementPipeline:
    """Complete enhancement pipeline for medical images"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.azure_enhancer = AzureImageEnhancer(config_path)
        self.traditional_enhancer = TraditionalImageEnhancer()
        self.diffusion_enhancer = DiffusionImageEnhancer()
    
    def enhance_image(
        self, 
        image: np.ndarray,
        modality: str = "xray",
        analyze_first: bool = True,
        apply_super_resolution: bool = False
    ) -> Tuple[np.ndarray, Optional[str]]:
        """
        Complete enhancement pipeline
        
        Returns:
            enhanced_image: Enhanced image
            analysis: Image analysis report (if analyze_first=True)
        """
        analysis = None
        
        # Step 1: Analyze image (optional)
        if analyze_first:
            logger.info("Analyzing image with Azure OpenAI...")
            analysis = self.azure_enhancer.analyze_medical_image(image, modality)
            logger.info(f"Analysis: {analysis}")
        
        # Step 2: Denoise
        logger.info("Applying denoising...")
        enhanced = self.traditional_enhancer.denoise(image)
        
        # Step 3: Enhance contrast
        logger.info("Enhancing contrast...")
        enhanced = self.traditional_enhancer.enhance_contrast(enhanced)
        
        # Step 4: Sharpen
        logger.info("Sharpening image...")
        enhanced = self.traditional_enhancer.sharpen(enhanced)
        
        # Step 5: Super-resolution (optional)
        if apply_super_resolution:
            scale_factor = self.config['image_enhancement']['super_resolution']['scale_factor']
            logger.info(f"Applying super-resolution (scale: {scale_factor}x)...")
            enhanced = self.traditional_enhancer.super_resolution(enhanced, scale_factor)
        
        return enhanced, analysis
    
    def batch_enhance(
        self,
        input_dir: Path,
        output_dir: Path,
        modality: str = "xray"
    ):
        """Enhance all images in a directory"""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        image_files = list(input_dir.glob("*.png")) + list(input_dir.glob("*.jpg"))
        
        logger.info(f"Found {len(image_files)} images to enhance")
        
        for img_path in image_files:
            logger.info(f"Processing {img_path.name}...")
            
            # Load image
            image = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            
            # Enhance
            enhanced, _ = self.enhance_image(image, modality, analyze_first=False)
            
            # Save
            output_path = output_dir / f"enhanced_{img_path.name}"
            cv2.imwrite(str(output_path), enhanced)
            logger.info(f"Saved to {output_path}")


def main():
    """Main enhancement pipeline"""
    logger.info("Medical Image Enhancement Pipeline")
    
    # Initialize pipeline
    pipeline = MedicalImageEnhancementPipeline()
    
    # Example: Enhance a single image
    # image_path = "data/raw/sample_xray.png"
    # if Path(image_path).exists():
    #     image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    #     enhanced, analysis = pipeline.enhance_image(image, modality="xray")
    #     cv2.imwrite("data/processed/enhanced_xray.png", enhanced)
    
    logger.info("Enhancement pipeline ready. Add images to data/raw/ and run batch_enhance()")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

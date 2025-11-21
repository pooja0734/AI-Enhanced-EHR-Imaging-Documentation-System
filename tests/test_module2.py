"""
Unit tests for Module 2: Image Enhancement
"""

import pytest
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / 'src' / 'module2_image_enhancement'))

from enhance_images import TraditionalImageEnhancer


class TestTraditionalImageEnhancer:
    """Test cases for TraditionalImageEnhancer"""
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample medical image"""
        return np.random.randint(0, 255, (512, 512), dtype=np.uint8)
    
    def test_denoise_nlm(self, sample_image):
        """Test Non-Local Means denoising"""
        enhancer = TraditionalImageEnhancer()
        denoised = enhancer.denoise(sample_image, method="nlm")
        
        assert denoised.shape == sample_image.shape
        assert denoised.dtype == np.uint8
    
    def test_denoise_gaussian(self, sample_image):
        """Test Gaussian denoising"""
        enhancer = TraditionalImageEnhancer()
        denoised = enhancer.denoise(sample_image, method="gaussian")
        
        assert denoised.shape == sample_image.shape
    
    def test_enhance_contrast_clahe(self, sample_image):
        """Test CLAHE contrast enhancement"""
        enhancer = TraditionalImageEnhancer()
        enhanced = enhancer.enhance_contrast(sample_image, method="clahe")
        
        assert enhanced.shape == sample_image.shape
        assert enhanced.dtype == np.uint8
    
    def test_enhance_contrast_histogram_eq(self, sample_image):
        """Test histogram equalization"""
        enhancer = TraditionalImageEnhancer()
        enhanced = enhancer.enhance_contrast(sample_image, method="histogram_eq")
        
        assert enhanced.shape == sample_image.shape
    
    def test_sharpen(self, sample_image):
        """Test image sharpening"""
        enhancer = TraditionalImageEnhancer()
        sharpened = enhancer.sharpen(sample_image)
        
        assert sharpened.shape == sample_image.shape
    
    def test_super_resolution(self, sample_image):
        """Test super-resolution"""
        enhancer = TraditionalImageEnhancer()
        upscaled = enhancer.super_resolution(sample_image, scale_factor=2)
        
        expected_shape = (sample_image.shape[0] * 2, sample_image.shape[1] * 2)
        assert upscaled.shape == expected_shape
    
    def test_edge_enhancement(self, sample_image):
        """Test edge enhancement"""
        enhancer = TraditionalImageEnhancer()
        edge_enhanced = enhancer.edge_enhancement(sample_image)
        
        assert edge_enhanced.shape == sample_image.shape


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

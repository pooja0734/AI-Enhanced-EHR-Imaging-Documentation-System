"""
Module 1: Data Collection and Preprocessing
Handles collection, cleaning, and standardization of medical imaging and EHR data
"""

import os
import numpy as np
import pandas as pd
import pydicom
import nibabel as nib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from PIL import Image
import cv2
from sklearn.model_selection import train_test_split
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalImageLoader:
    """Load and preprocess medical images from various formats"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.supported_formats = self.config['data_processing']['supported_image_formats']
        
    def load_dicom(self, file_path: str) -> np.ndarray:
        """Load DICOM medical image"""
        try:
            dicom = pydicom.dcmread(file_path)
            image = dicom.pixel_array
            
            # Apply windowing if available
            if hasattr(dicom, 'WindowCenter') and hasattr(dicom, 'WindowWidth'):
                center = dicom.WindowCenter
                width = dicom.WindowWidth
                image = self._apply_windowing(image, center, width)
            
            return image
        except Exception as e:
            logger.error(f"Error loading DICOM file {file_path}: {e}")
            return None
    
    def load_nifti(self, file_path: str) -> np.ndarray:
        """Load NIfTI medical image"""
        try:
            nifti = nib.load(file_path)
            image = nifti.get_fdata()
            return image
        except Exception as e:
            logger.error(f"Error loading NIfTI file {file_path}: {e}")
            return None
    
    def load_standard_image(self, file_path: str) -> np.ndarray:
        """Load standard image formats (PNG, JPG)"""
        try:
            image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            return image
        except Exception as e:
            logger.error(f"Error loading image file {file_path}: {e}")
            return None
    
    def load_image(self, file_path: str) -> Optional[np.ndarray]:
        """Auto-detect and load medical image"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.dcm':
            return self.load_dicom(file_path)
        elif ext in ['.nii', '.gz']:
            return self.load_nifti(file_path)
        elif ext in ['.png', '.jpg', '.jpeg']:
            return self.load_standard_image(file_path)
        else:
            logger.warning(f"Unsupported file format: {ext}")
            return None
    
    @staticmethod
    def _apply_windowing(image: np.ndarray, center: float, width: float) -> np.ndarray:
        """Apply window/level adjustment to medical image"""
        img_min = center - width // 2
        img_max = center + width // 2
        image = np.clip(image, img_min, img_max)
        image = ((image - img_min) / (img_max - img_min) * 255).astype(np.uint8)
        return image


class DataPreprocessor:
    """Preprocess and normalize medical imaging data"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.image_size = tuple(self.config['data_processing']['image_size']['default'])
        self.norm_method = self.config['preprocessing']['normalization']['method']
    
    def normalize(self, image: np.ndarray, method: str = None) -> np.ndarray:
        """Normalize image using specified method"""
        if method is None:
            method = self.norm_method
        
        if method == 'z_score':
            mean = np.mean(image)
            std = np.std(image)
            return (image - mean) / (std + 1e-8)
        elif method == 'min_max':
            min_val = np.min(image)
            max_val = np.max(image)
            return (image - min_val) / (max_val - min_val + 1e-8)
        else:
            logger.warning(f"Unknown normalization method: {method}")
            return image
    
    def resize(self, image: np.ndarray, size: Tuple[int, int] = None) -> np.ndarray:
        """Resize image to target size"""
        if size is None:
            size = self.image_size
        return cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    
    def denoise(self, image: np.ndarray) -> np.ndarray:
        """Apply basic denoising"""
        return cv2.fastNlMeansDenoising(image.astype(np.uint8))
    
    def augment(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply data augmentation"""
        augmented = [image]
        
        if self.config['preprocessing']['augmentation']['enabled']:
            # Rotation
            rotation_range = self.config['preprocessing']['augmentation']['rotation_range']
            for angle in [-rotation_range, rotation_range]:
                rotated = self._rotate_image(image, angle)
                augmented.append(rotated)
            
            # Horizontal flip
            if self.config['preprocessing']['augmentation']['horizontal_flip']:
                augmented.append(cv2.flip(image, 1))
        
        return augmented
    
    @staticmethod
    def _rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by given angle"""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, rotation_matrix, (width, height))
    
    def preprocess(self, image: np.ndarray, 
                   normalize: bool = True,
                   resize: bool = True,
                   denoise: bool = False) -> np.ndarray:
        """Complete preprocessing pipeline"""
        if resize:
            image = self.resize(image)
        if denoise:
            image = self.denoise(image)
        if normalize:
            image = self.normalize(image)
        return image


class EHRDataProcessor:
    """Process electronic health record data"""
    
    def __init__(self):
        self.clinical_note_fields = [
            'patient_id', 'date', 'chief_complaint', 
            'history', 'examination', 'diagnosis', 'plan'
        ]
    
    def load_ehr_data(self, file_path: str) -> pd.DataFrame:
        """Load EHR data from CSV or JSON"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.csv':
            return pd.read_csv(file_path)
        elif ext == '.json':
            return pd.read_json(file_path)
        else:
            logger.error(f"Unsupported EHR file format: {ext}")
            return None
    
    def clean_clinical_notes(self, notes: pd.Series) -> pd.Series:
        """Clean and standardize clinical notes"""
        # Remove extra whitespace
        notes = notes.str.strip()
        notes = notes.str.replace(r'\s+', ' ', regex=True)
        
        # Remove special characters but keep medical notation
        notes = notes.str.replace(r'[^\w\s\-\/\.]', '', regex=True)
        
        return notes
    
    def extract_icd10_codes(self, diagnosis: str) -> List[str]:
        """Extract ICD-10 codes from diagnosis text (placeholder)"""
        # This would use NLP and medical coding libraries
        # Placeholder implementation
        return []
    
    def anonymize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Anonymize patient data for HIPAA compliance"""
        # Remove or hash PHI (Protected Health Information)
        if 'patient_name' in df.columns:
            df = df.drop('patient_name', axis=1)
        
        if 'patient_id' in df.columns:
            df['patient_id'] = df['patient_id'].apply(
                lambda x: hash(str(x)) % 1000000
            )
        
        # Remove dates or convert to age
        if 'date_of_birth' in df.columns:
            df['age'] = pd.to_datetime('today').year - pd.to_datetime(df['date_of_birth']).dt.year
            df = df.drop('date_of_birth', axis=1)
        
        return df


class DatasetBuilder:
    """Build training datasets from preprocessed data"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def create_train_val_test_split(
        self, 
        X: np.ndarray, 
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data into train, validation, and test sets"""
        val_split = self.config['preprocessing']['validation_split']
        test_split = self.config['preprocessing']['test_split']
        
        # First split: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_split, random_state=42
        )
        
        # Second split: separate validation from training
        val_size_adjusted = val_split / (1 - test_split)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted, random_state=42
        )
        
        logger.info(f"Dataset split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def save_dataset(self, data: Dict, output_path: str):
        """Save processed dataset"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(output_path, **data)
        logger.info(f"Dataset saved to {output_path}")


def main():
    """Main preprocessing pipeline"""
    logger.info("Starting data preprocessing pipeline...")
    
    # Initialize components
    image_loader = MedicalImageLoader()
    preprocessor = DataPreprocessor()
    ehr_processor = EHRDataProcessor()
    dataset_builder = DatasetBuilder()
    
    # Example usage
    raw_data_path = Path(os.getenv('RAW_DATA_PATH', 'data/raw'))
    processed_data_path = Path(os.getenv('PROCESSED_DATA_PATH', 'data/processed'))
    
    logger.info(f"Loading data from {raw_data_path}")
    logger.info(f"Processed data will be saved to {processed_data_path}")
    
    # Note: Actual implementation would load and process real medical data
    logger.info("Preprocessing pipeline ready. Add your medical imaging data to data/raw/")


if __name__ == "__main__":
    main()

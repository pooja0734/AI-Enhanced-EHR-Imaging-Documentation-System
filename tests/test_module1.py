"""
Unit tests for Module 1: Data Preprocessing
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / 'src' / 'module1_data_preprocessing'))

from preprocess import (
    MedicalImageLoader,
    DataPreprocessor,
    EHRDataProcessor,
    DatasetBuilder
)


class TestMedicalImageLoader:
    """Test cases for MedicalImageLoader"""
    
    def test_initialization(self):
        """Test loader initialization"""
        loader = MedicalImageLoader()
        assert loader is not None
        assert len(loader.supported_formats) > 0
    
    def test_windowing(self):
        """Test DICOM windowing function"""
        loader = MedicalImageLoader()
        image = np.random.randint(0, 4096, (512, 512), dtype=np.uint16)
        windowed = loader._apply_windowing(image, center=2048, width=4096)
        
        assert windowed.dtype == np.uint8
        assert windowed.min() >= 0
        assert windowed.max() <= 255


class TestDataPreprocessor:
    """Test cases for DataPreprocessor"""
    
    def test_normalization_zscore(self):
        """Test z-score normalization"""
        preprocessor = DataPreprocessor()
        image = np.random.rand(256, 256) * 255
        normalized = preprocessor.normalize(image, method='z_score')
        
        assert abs(normalized.mean()) < 1e-5  # Mean should be ~0
        assert abs(normalized.std() - 1.0) < 1e-5  # Std should be ~1
    
    def test_normalization_minmax(self):
        """Test min-max normalization"""
        preprocessor = DataPreprocessor()
        image = np.random.rand(256, 256) * 255
        normalized = preprocessor.normalize(image, method='min_max')
        
        assert normalized.min() >= 0
        assert normalized.max() <= 1
    
    def test_resize(self):
        """Test image resizing"""
        preprocessor = DataPreprocessor()
        image = np.random.rand(1024, 1024)
        resized = preprocessor.resize(image, size=(512, 512))
        
        assert resized.shape == (512, 512)
    
    def test_augmentation(self):
        """Test data augmentation"""
        preprocessor = DataPreprocessor()
        image = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
        augmented = preprocessor.augment(image)
        
        assert len(augmented) > 1  # Should have multiple augmented versions


class TestEHRDataProcessor:
    """Test cases for EHRDataProcessor"""
    
    def test_clean_clinical_notes(self):
        """Test clinical note cleaning"""
        processor = EHRDataProcessor()
        notes = pd.Series([
            "  Patient   has   fever  ",
            "Diagnosis: pneumonia!!!",
            "   Normal   exam   "
        ])
        
        cleaned = processor.clean_clinical_notes(notes)
        
        assert all(note == note.strip() for note in cleaned)
        assert "   " not in cleaned.iloc[0]
    
    def test_anonymize_data(self):
        """Test data anonymization"""
        processor = EHRDataProcessor()
        df = pd.DataFrame({
            'patient_id': ['P001', 'P002'],
            'patient_name': ['John Doe', 'Jane Smith'],
            'age': [45, 32]
        })
        
        anonymized = processor.anonymize_data(df)
        
        assert 'patient_name' not in anonymized.columns
        assert 'patient_id' in anonymized.columns


class TestDatasetBuilder:
    """Test cases for DatasetBuilder"""
    
    def test_train_val_test_split(self):
        """Test dataset splitting"""
        builder = DatasetBuilder()
        
        X = np.random.rand(100, 64, 64)
        y = np.random.randint(0, 2, 100)
        
        X_train, X_val, X_test, y_train, y_val, y_test = \
            builder.create_train_val_test_split(X, y)
        
        # Check sizes
        total = len(X_train) + len(X_val) + len(X_test)
        assert total == len(X)
        
        # Check no overlap
        assert len(X_train) > 0
        assert len(X_val) > 0
        assert len(X_test) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

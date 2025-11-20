"""
Module 4: Integration and Deployment
Deploy and integrate EHR AI system into clinical workflows
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import numpy as np
import cv2
from datetime import datetime

# Import other modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from module2_image_enhancement.enhance_images import MedicalImageEnhancementPipeline
from module3_documentation_automation.generate_notes import ClinicalDocumentationWorkflow

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered EHR System API",
    description="API for medical image enhancement and clinical documentation automation",
    version="1.0.0"
)

# Initialize AI components
image_enhancement_pipeline = None
documentation_workflow = None


# Pydantic models for API requests
class PatientInfo(BaseModel):
    patient_id: str
    age: int
    gender: str
    visit_date: str


class ClinicalObservations(BaseModel):
    subjective: str
    blood_pressure: Optional[str] = None
    heart_rate: Optional[str] = None
    temperature: Optional[str] = None
    respiratory_rate: Optional[str] = None
    physical_exam: Optional[str] = None


class VisitData(BaseModel):
    patient_info: PatientInfo
    observations: ClinicalObservations
    assessment: Optional[str] = None
    diagnosis: str


class ICD10Request(BaseModel):
    diagnosis: str
    clinical_context: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize AI models on startup"""
    global image_enhancement_pipeline, documentation_workflow
    
    logger.info("Initializing AI-Powered EHR System...")
    
    try:
        image_enhancement_pipeline = MedicalImageEnhancementPipeline()
        documentation_workflow = ClinicalDocumentationWorkflow()
        logger.info("All AI components initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing components: {e}")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI-Powered EHR System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "image_enhancement": "/api/v1/enhance-image",
            "clinical_notes": "/api/v1/generate-note",
            "icd10_coding": "/api/v1/suggest-icd10"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "image_enhancement": image_enhancement_pipeline is not None,
            "documentation": documentation_workflow is not None
        }
    }


@app.post("/api/v1/enhance-image")
async def enhance_medical_image(
    file: UploadFile = File(...),
    modality: str = "xray",
    analyze: bool = True,
    super_resolution: bool = False
):
    """
    Enhance a medical image
    
    Args:
        file: Medical image file (PNG, JPG, or DICOM)
        modality: Image modality (xray, ct, mri, ultrasound, dxa)
        analyze: Whether to analyze image with AI
        super_resolution: Apply super-resolution enhancement
    """
    try:
        # Read uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Enhance image
        enhanced_image, analysis = image_enhancement_pipeline.enhance_image(
            image,
            modality=modality,
            analyze_first=analyze,
            apply_super_resolution=super_resolution
        )
        
        # Encode enhanced image
        _, buffer = cv2.imencode('.png', enhanced_image)
        enhanced_bytes = buffer.tobytes()
        
        import base64
        enhanced_b64 = base64.b64encode(enhanced_bytes).decode()
        
        return JSONResponse({
            "status": "success",
            "modality": modality,
            "analysis": analysis if analyze else None,
            "enhanced_image": enhanced_b64,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error enhancing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate-note")
async def generate_clinical_note(visit_data: VisitData):
    """
    Generate clinical documentation for a patient visit
    
    Args:
        visit_data: Patient information, observations, and diagnosis
    """
    try:
        # Convert Pydantic models to dicts
        patient_info = visit_data.patient_info.dict()
        observations = visit_data.observations.dict()
        
        visit_dict = {
            'observations': observations,
            'assessment': visit_data.assessment,
            'diagnosis': visit_data.diagnosis
        }
        
        # Generate documentation
        documentation = documentation_workflow.process_patient_visit(
            patient_info=patient_info,
            visit_data=visit_dict
        )
        
        return JSONResponse({
            "status": "success",
            "documentation": documentation,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating clinical note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/suggest-icd10")
async def suggest_icd10_codes(request: ICD10Request):
    """
    Suggest ICD-10 codes for a diagnosis
    
    Args:
        request: Diagnosis and optional clinical context
    """
    try:
        suggestions = documentation_workflow.icd10_coder.suggest_icd10_codes(
            diagnosis=request.diagnosis,
            clinical_context=request.clinical_context
        )
        
        return JSONResponse({
            "status": "success",
            "diagnosis": request.diagnosis,
            "suggested_codes": suggestions,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error suggesting ICD-10 codes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch-process")
async def batch_process_visits(visits: list[VisitData]):
    """
    Batch process multiple patient visits
    
    Args:
        visits: List of patient visit data
    """
    try:
        results = []
        
        for visit_data in visits:
            patient_info = visit_data.patient_info.dict()
            observations = visit_data.observations.dict()
            
            visit_dict = {
                'observations': observations,
                'assessment': visit_data.assessment,
                'diagnosis': visit_data.diagnosis
            }
            
            documentation = documentation_workflow.process_patient_visit(
                patient_info=patient_info,
                visit_data=visit_dict
            )
            
            results.append(documentation)
        
        return JSONResponse({
            "status": "success",
            "processed_count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class EHRSystemDeployment:
    """Deployment and integration utilities"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def start_api_server(self, host: str = None, port: int = None):
        """Start the FastAPI server"""
        if host is None:
            host = self.config['deployment']['api']['host']
        if port is None:
            port = self.config['deployment']['api']['port']
        
        workers = self.config['deployment']['api']['workers']
        
        logger.info(f"Starting EHR AI System API server on {host}:{port}")
        logger.info(f"Workers: {workers}")
        
        uvicorn.run(
            "deploy:app",
            host=host,
            port=port,
            workers=workers,
            log_level="info"
        )
    
    def test_deployment(self):
        """Test deployment readiness"""
        import requests
        
        base_url = f"http://localhost:{self.config['deployment']['api']['port']}"
        
        try:
            # Test health endpoint
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                logger.info("✓ Health check passed")
            else:
                logger.error("✗ Health check failed")
            
            # Test root endpoint
            response = requests.get(f"{base_url}/")
            if response.status_code == 200:
                logger.info("✓ Root endpoint accessible")
            else:
                logger.error("✗ Root endpoint failed")
            
            logger.info("Deployment test completed")
        
        except Exception as e:
            logger.error(f"Deployment test failed: {e}")
    
    def generate_deployment_report(self, output_path: str = "docs/deployment_report.md"):
        """Generate deployment documentation"""
        report = f"""# EHR AI System Deployment Report

## Deployment Date
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Configuration

### API Configuration
- Host: {self.config['deployment']['api']['host']}
- Port: {self.config['deployment']['api']['port']}
- Workers: {self.config['deployment']['api']['workers']}
- Timeout: {self.config['deployment']['api']['timeout']}s

### Components Deployed
1. ✓ Medical Image Enhancement Pipeline
2. ✓ Clinical Documentation Generator
3. ✓ ICD-10 Coding Automation
4. ✓ REST API Interface

### Security Features
- Encryption: {'Enabled' if self.config['security']['encryption_enabled'] else 'Disabled'}
- HIPAA Compliance: {'Yes' if self.config['security']['hipaa_compliant'] else 'No'}
- Audit Logging: {'Enabled' if self.config['security']['audit_logging'] else 'Disabled'}

### Monitoring
- Prometheus: {'Enabled' if self.config['deployment']['monitoring']['enable_prometheus'] else 'Disabled'}
- Log Level: {self.config['deployment']['monitoring']['log_level']}
- Performance Tracking: {'Enabled' if self.config['deployment']['monitoring']['performance_tracking'] else 'Disabled'}

## API Endpoints

### Image Enhancement
```
POST /api/v1/enhance-image
```
Enhance medical images with AI

### Clinical Documentation
```
POST /api/v1/generate-note
```
Generate clinical notes from structured data

### ICD-10 Coding
```
POST /api/v1/suggest-icd10
```
Automatically suggest ICD-10 codes

### Batch Processing
```
POST /api/v1/batch-process
```
Process multiple visits in batch

## Next Steps
1. Configure Azure OpenAI credentials in `.env`
2. Test all endpoints
3. Integrate with hospital EHR system
4. Conduct user training sessions
5. Monitor performance and errors

## Support
For issues or questions, contact the development team.
"""
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Deployment report generated: {output_file}")


def main():
    """Main deployment entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EHR AI System Deployment")
    parser.add_argument('--action', choices=['start', 'test', 'report'], default='start',
                        help='Deployment action')
    parser.add_argument('--host', default='0.0.0.0', help='API host')
    parser.add_argument('--port', type=int, default=8000, help='API port')
    
    args = parser.parse_args()
    
    deployment = EHRSystemDeployment()
    
    if args.action == 'start':
        deployment.start_api_server(host=args.host, port=args.port)
    elif args.action == 'test':
        deployment.test_deployment()
    elif args.action == 'report':
        deployment.generate_deployment_report()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

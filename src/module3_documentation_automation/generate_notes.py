"""
Module 3: Clinical Note Generation & ICD-10 Coding Automation
Automates clinical documentation using Azure OpenAI
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import yaml
from dotenv import load_dotenv
from openai import AzureOpenAI
import pandas as pd

load_dotenv()
logger = logging.getLogger(__name__)


class ClinicalNoteGenerator:
    """Generate clinical notes using Azure OpenAI"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.supported_note_types = self.config['clinical_documentation']['supported_note_types']
    
    def generate_progress_note(
        self,
        patient_info: Dict,
        observations: Dict,
        assessment: str = None
    ) -> str:
        """
        Generate a progress note from structured patient data
        
        Args:
            patient_info: Dict with patient demographics
            observations: Dict with clinical observations
            assessment: Provider's assessment
        """
        try:
            # Build prompt
            prompt = self._build_progress_note_prompt(patient_info, observations, assessment)
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced physician assistant. Generate clear, "
                                   "professional clinical progress notes following standard medical documentation format. "
                                   "Use proper medical terminology and structure (SOAP format: Subjective, Objective, Assessment, Plan)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent medical documentation
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating progress note: {e}")
            return None
    
    def generate_discharge_summary(
        self,
        admission_data: Dict,
        hospital_course: str,
        discharge_instructions: str
    ) -> str:
        """Generate discharge summary"""
        try:
            prompt = f"""
Generate a comprehensive discharge summary with the following information:

ADMISSION DATA:
- Date of Admission: {admission_data.get('admission_date', 'N/A')}
- Chief Complaint: {admission_data.get('chief_complaint', 'N/A')}
- Admitting Diagnosis: {admission_data.get('admitting_diagnosis', 'N/A')}

HOSPITAL COURSE:
{hospital_course}

DISCHARGE INSTRUCTIONS:
{discharge_instructions}

Please structure the discharge summary with standard sections:
1. Patient Demographics
2. Admission/Discharge Dates
3. Admitting Diagnosis
4. Hospital Course
5. Discharge Diagnosis
6. Discharge Medications
7. Follow-up Instructions
8. Patient Education
"""
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a hospital physician creating discharge summaries. "
                                   "Generate comprehensive, clear discharge summaries following "
                                   "standard medical documentation practices."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating discharge summary: {e}")
            return None
    
    def generate_radiology_report(
        self,
        study_type: str,
        findings: str,
        comparison: str = None
    ) -> str:
        """Generate radiology report"""
        try:
            prompt = f"""
Generate a radiology report for the following study:

STUDY TYPE: {study_type}

FINDINGS:
{findings}
"""
            if comparison:
                prompt += f"\nCOMPARISON:\n{comparison}"
            
            prompt += """

Please structure the report with standard radiology sections:
1. CLINICAL HISTORY
2. TECHNIQUE
3. COMPARISON (if applicable)
4. FINDINGS
5. IMPRESSION
"""
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced radiologist. Generate clear, precise "
                                   "radiology reports following standard formatting and terminology."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating radiology report: {e}")
            return None
    
    def _build_progress_note_prompt(
        self,
        patient_info: Dict,
        observations: Dict,
        assessment: str
    ) -> str:
        """Build prompt for progress note generation"""
        prompt = f"""
Generate a clinical progress note with the following information:

PATIENT INFORMATION:
- Age: {patient_info.get('age', 'N/A')}
- Gender: {patient_info.get('gender', 'N/A')}
- Date: {patient_info.get('visit_date', datetime.now().strftime('%Y-%m-%d'))}

SUBJECTIVE (Chief Complaint and History):
{observations.get('subjective', 'Patient reports ongoing symptoms.')}

OBJECTIVE (Vital Signs and Physical Exam):
- Blood Pressure: {observations.get('blood_pressure', 'N/A')}
- Heart Rate: {observations.get('heart_rate', 'N/A')}
- Temperature: {observations.get('temperature', 'N/A')}
- Respiratory Rate: {observations.get('respiratory_rate', 'N/A')}
- Physical Exam: {observations.get('physical_exam', 'N/A')}

ASSESSMENT:
{assessment if assessment else 'Stable condition, continue current management.'}

Please generate a complete progress note in SOAP format.
"""
        return prompt


class ICD10CodingAutomation:
    """Automate ICD-10 coding using Azure OpenAI"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.confidence_threshold = self.config['clinical_documentation']['icd10_coding']['confidence_threshold']
        self.max_suggestions = self.config['clinical_documentation']['icd10_coding']['max_suggestions']
        
        # Load ICD-10 reference data
        self.icd10_codes = self._load_icd10_reference()
    
    def _load_icd10_reference(self) -> Dict:
        """Load ICD-10 code reference (placeholder)"""
        # In production, load from comprehensive ICD-10 database
        return {
            "J18.9": "Pneumonia, unspecified organism",
            "I10": "Essential (primary) hypertension",
            "E11.9": "Type 2 diabetes mellitus without complications",
            "M25.50": "Pain in unspecified joint",
            "R51": "Headache",
            "R50.9": "Fever, unspecified",
            "S52.50": "Unspecified fracture of lower end of radius",
            "J44.9": "Chronic obstructive pulmonary disease, unspecified",
            "N18.9": "Chronic kidney disease, unspecified",
            "F41.9": "Anxiety disorder, unspecified"
        }
    
    def suggest_icd10_codes(
        self,
        diagnosis: str,
        clinical_context: str = None
    ) -> List[Dict]:
        """
        Suggest ICD-10 codes based on diagnosis
        
        Returns:
            List of dicts with 'code', 'description', and 'confidence'
        """
        try:
            # Build context-aware prompt
            prompt = f"""
Based on the following diagnosis, suggest the most appropriate ICD-10 codes.

DIAGNOSIS: {diagnosis}
"""
            if clinical_context:
                prompt += f"\nCLINICAL CONTEXT:\n{clinical_context}"
            
            prompt += f"""

Provide up to {self.max_suggestions} ICD-10 codes with descriptions.
Format your response as a JSON array with this structure:
[
  {{"code": "XXX.XX", "description": "Description", "confidence": 0.95}},
  ...
]

Only suggest codes you are confident about (confidence > {self.confidence_threshold}).
"""
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a certified medical coder expert in ICD-10 coding. "
                                   "Provide accurate ICD-10 codes based on clinical diagnoses. "
                                   "Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Very low temperature for coding accuracy
                max_tokens=500
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                return suggestions
            else:
                logger.warning("Could not parse ICD-10 suggestions from response")
                return []
        
        except Exception as e:
            logger.error(f"Error suggesting ICD-10 codes: {e}")
            return []
    
    def validate_icd10_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate if an ICD-10 code is properly formatted
        
        Returns:
            (is_valid, description)
        """
        # Check format (simplified)
        import re
        pattern = r'^[A-Z][0-9]{2}\.?[0-9]{0,4}$'
        
        if not re.match(pattern, code):
            return False, "Invalid ICD-10 code format"
        
        # Check against reference (in production, use full database)
        if code in self.icd10_codes:
            return True, self.icd10_codes[code]
        
        return True, "Code format valid (not in local reference)"
    
    def batch_code_diagnoses(self, diagnoses_file: str) -> pd.DataFrame:
        """
        Batch process diagnoses for ICD-10 coding
        
        Args:
            diagnoses_file: CSV file with 'patient_id' and 'diagnosis' columns
        """
        df = pd.read_csv(diagnoses_file)
        
        results = []
        for idx, row in df.iterrows():
            logger.info(f"Processing {idx + 1}/{len(df)}: {row['diagnosis']}")
            
            suggestions = self.suggest_icd10_codes(
                row['diagnosis'],
                row.get('clinical_context', None)
            )
            
            results.append({
                'patient_id': row.get('patient_id', f'P{idx:05d}'),
                'diagnosis': row['diagnosis'],
                'suggested_codes': json.dumps(suggestions),
                'top_code': suggestions[0]['code'] if suggestions else None,
                'confidence': suggestions[0]['confidence'] if suggestions else 0.0
            })
        
        return pd.DataFrame(results)


class ClinicalDocumentationWorkflow:
    """Complete clinical documentation workflow"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.note_generator = ClinicalNoteGenerator(config_path)
        self.icd10_coder = ICD10CodingAutomation(config_path)
    
    def process_patient_visit(
        self,
        patient_info: Dict,
        visit_data: Dict
    ) -> Dict:
        """
        Complete workflow for a patient visit
        
        Returns:
            Dict with generated note and ICD-10 codes
        """
        logger.info(f"Processing visit for patient {patient_info.get('patient_id', 'Unknown')}")
        
        # Generate progress note
        progress_note = self.note_generator.generate_progress_note(
            patient_info=patient_info,
            observations=visit_data.get('observations', {}),
            assessment=visit_data.get('assessment', None)
        )
        
        # Generate ICD-10 codes
        diagnosis = visit_data.get('diagnosis', '')
        icd10_codes = self.icd10_coder.suggest_icd10_codes(
            diagnosis=diagnosis,
            clinical_context=progress_note
        )
        
        return {
            'patient_id': patient_info.get('patient_id'),
            'visit_date': patient_info.get('visit_date'),
            'progress_note': progress_note,
            'diagnosis': diagnosis,
            'icd10_codes': icd10_codes,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_documentation(self, documentation: Dict, output_dir: str = "data/output"):
        """Save generated documentation"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        patient_id = documentation['patient_id']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = output_path / f"clinical_doc_{patient_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(documentation, f, indent=2)
        
        logger.info(f"Documentation saved to {filename}")


def main():
    """Main clinical documentation pipeline"""
    logger.info("Clinical Documentation Automation System")
    
    # Initialize workflow
    workflow = ClinicalDocumentationWorkflow()
    
    # Example patient visit
    example_patient = {
        'patient_id': 'P00001',
        'age': 45,
        'gender': 'M',
        'visit_date': '2025-10-15'
    }
    
    example_visit = {
        'observations': {
            'subjective': 'Patient reports persistent cough for 2 weeks, fever, and fatigue.',
            'blood_pressure': '130/85',
            'heart_rate': '88',
            'temperature': '38.2°C',
            'respiratory_rate': '20',
            'physical_exam': 'Lungs: decreased breath sounds in right lower lobe, mild crackles.'
        },
        'assessment': 'Likely community-acquired pneumonia',
        'diagnosis': 'Community-acquired pneumonia'
    }
    
    # Process visit
    # documentation = workflow.process_patient_visit(example_patient, example_visit)
    # workflow.save_documentation(documentation)
    
    logger.info("Clinical documentation system ready")
    logger.info("Use process_patient_visit() to generate notes and ICD-10 codes")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

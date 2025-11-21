from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# -----------------------
# FASTAPI APP
# -----------------------
app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Pydantic Models
# -----------------------
class ClinicalNoteRequest(BaseModel):
    note_type: str
    patient_info: dict | None = None
    findings: dict | None = None
    admission_data: dict | None = None
    image_findings: str | None = None
    modality: str | None = None


class ICD10Request(BaseModel):
    clinical_text: str
    top_k: int = 5


# -----------------------
# Clinical Notes Generator
# -----------------------
@app.post("/clinical-notes")
def generate_clinical_notes(data: ClinicalNoteRequest):
    if data.note_type == "soap":
        note = f"""
SOAP NOTE
---------
Subjective: {data.findings.get('subjective', 'N/A')}
Objective: {data.findings.get('objective', 'N/A')}
Assessment: {data.findings.get('assessment', 'N/A')}
Plan: {data.findings.get('plan', 'N/A')}
"""
    elif data.note_type == "discharge":
        note = f"""
DISCHARGE SUMMARY
-----------------
Patient: {data.patient_info.get('name', 'N/A')}
Diagnosis: {data.admission_data.get('diagnosis', 'N/A')}
Treatment: {data.admission_data.get('treatment', 'N/A')}
Instructions: {data.admission_data.get('instructions', 'N/A')}
"""
    elif data.note_type == "radiology":
        note = f"""
RADIOLOGY REPORT
----------------
Modality: {data.modality}
Findings: {data.image_findings}
Impression: Possible abnormality detected.
"""
    else:
        return {"error": "Invalid note type"}

    return {"note": note}


# -----------------------
# Simple ICD-10 Coding API
# -----------------------
@app.post("/icd10-coding")
def suggest_icd_codes(data: ICD10Request):
    text = data.clinical_text.lower()

    mock_icd = []

    if "fever" in text:
        mock_icd.append({"code": "R50.9", "description": "Fever, unspecified"})
    if "cough" in text:
        mock_icd.append({"code": "R05", "description": "Cough"})
    if "diabetes" in text:
        mock_icd.append({"code": "E11", "description": "Type 2 Diabetes Mellitus"})

    if not mock_icd:
        mock_icd.append({"code": "Z00.00", "description": "General medical examination"})

    return {"codes": mock_icd[: data.top_k]}


# -----------------------
# Test root endpoint
# -----------------------
@app.get("/")
def root():
    return {"message": "Backend running successfully!"}

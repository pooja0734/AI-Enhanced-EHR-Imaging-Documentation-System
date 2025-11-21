from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

from services.clinical_notes import (
    generate_soap,
    generate_discharge,
    generate_radiology_report
)
from services.icd10 import suggest_codes
from services.image_enhancement import enhance

app = Flask(__name__)
CORS(app)

PATIENT_FILE = "patients.json"


def read_patients():
    if not os.path.exists(PATIENT_FILE):
        return []
    with open(PATIENT_FILE, "r") as f:
        return json.load(f)


def write_patients(data):
    with open(PATIENT_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------- API ROUTES --------------------------

@app.post("/clinical-notes")
def clinical_notes():
    data = request.json
    note_type = data.get("note_type")

    if note_type == "soap":
        return jsonify(generate_soap(data.get("patient_info"), data.get("findings")))
    if note_type == "discharge":
        return jsonify(generate_discharge(data.get("patient_info"), data.get("admission_data")))
    if note_type == "radiology":
        return jsonify(generate_radiology_report(data.get("image_findings"), data.get("modality")))

    return jsonify({"error": "Invalid note type"}), 400


@app.post("/icd10-coding")
def icd10():
    data = request.json
    return jsonify(suggest_codes(data.get("clinical_text", "")))


@app.post("/image-enhancement")
def image_enhancement():
    data = request.json
    return jsonify(enhance(data.get("image_base64"), data.get("modality")))


@app.get("/patients")
def get_patients():
    return jsonify(read_patients())


@app.get("/patients/<int:pid>")
def get_patient(pid):
    patients = read_patients()
    for p in patients:
        if p["id"] == pid:
            return jsonify(p)
    return jsonify({"error": "Patient not found"}), 404


@app.post("/patients")
def create_patient():
    data = request.json
    patients = read_patients()
    
    data["id"] = len(patients) + 1
    patients.append(data)
    write_patients(patients)

    return jsonify({"message": "Patient created", "patient": data})


@app.put("/patients/<int:pid>")
def update_patient(pid):
    data = request.json
    patients = read_patients()

    for i, p in enumerate(patients):
        if p["id"] == pid:
            patients[i].update(data)
            write_patients(patients)
            return jsonify({"message": "Patient updated", "patient": patients[i]})

    return jsonify({"error": "Patient not found"}), 404


# ---------------------------------------------------------

app.run(port=5000, debug=True)

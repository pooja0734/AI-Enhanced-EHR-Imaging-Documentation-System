#!/usr/bin/env python3
"""
icd10_clinical_note_generator.py

Module 3: Clinical Note Generation & ICD-10 Coding Automation
-------------------------------------------------------------
What this script does (complete, offline-capable demo):
- Reads structured patient data from a CSV file (one row per patient).
- Reads a plain-text observations file (optional) that contains free-text clinician notes per patient id.
- Generates a concise clinical note (History, Examination, Impression, Plan) using a template-based approach.
- Suggests ICD-10 codes by matching observation keywords against a built-in ICD-10 keyword map and using fuzzy matching.
- Saves results to an output CSV with columns: patient_id, generated_note, suggested_icd10_codes, icd_confidence
- Produces a summary report (report.md) in the output folder.

Requirements:
- Python 3.8+
- pip install pandas fuzzywuzzy python-Levenshtein

Usage example:
1) Prepare input CSV (patients.csv) with columns: patient_id, name, age, sex, chief_complaint, vitals (optional), lab_summary (optional)
2) (Optional) Prepare observations.txt that contains blocks like:
   PATIENT_ID: 12345
   Observation: Patient has cough, fever and shortness of breath. Chest x-ray shows consolidation.
   ---
3) Run:
   python icd10_clinical_note_generator.py --patients patients.csv --observations observations.txt --output_dir ./cn_output
"""

import os
import argparse
import pandas as pd
import re
from collections import defaultdict

try:
    from fuzzywuzzy import process
except Exception:
    process = None

# ---------- Small ICD-10 keyword -> code map (illustrative, NOT exhaustive) ----------
ICD_KEYWORD_MAP = {
    "hypertension": ("I10", "Essential (primary) hypertension"),
    "type 2 diabetes": ("E11", "Type 2 diabetes mellitus"),
    "diabetes mellitus": ("E14", "Unspecified diabetes mellitus"),
    "pneumonia": ("J18", "Pneumonia, unspecified organism"),
    "acute bronchitis": ("J20", "Acute bronchitis"),
    "asthma": ("J45", "Asthma"),
    "chest pain": ("R07.9", "Chest pain, unspecified"),
    "myocardial infarction": ("I21", "Acute myocardial infarction"),
    "heart failure": ("I50", "Heart failure"),
    "fever": ("R50.9", "Fever, unspecified"),
    "cough": ("R05", "Cough"),
    "shortness of breath": ("R06.02", "Shortness of breath"),
    "covid": ("U07.1", "COVID-19"),
    "stroke": ("I63", "Cerebral infarction (ischemic stroke)"),
    "urinary tract infection": ("N39.0", "Urinary tract infection, site not specified"),
    "headache": ("R51", "Headache"),
    "migraine": ("G43", "Migraine"),
    "otitis media": ("H66", "Suppurative and unspecified otitis media"),
    "appendicitis": ("K35", "Acute appendicitis")
}

ICD_KEYWORDS = list(ICD_KEYWORD_MAP.keys())

# ---------- Helper functions ----------

def load_patients(csv_path):
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    if 'patient_id' not in df.columns:
        raise ValueError("patients CSV must contain a 'patient_id' column.")
    return df

def load_observations(txt_path):
    if not txt_path or not os.path.exists(txt_path):
        return {}
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'\\n-{3,}\\n|\\n(?=PATIENT_ID:)', content.strip(), flags=re.IGNORECASE)
    obs = {}
    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        pid = None
        text_lines = []
        for ln in lines:
            m = re.match(r'PATIENT_ID\\s*:\\s*(\\S+)', ln, re.IGNORECASE)
            if m:
                pid = m.group(1).strip()
                continue
            m2 = re.match(r'Observation\\s*:\\s*(.*)', ln, re.IGNORECASE)
            if m2:
                text_lines.append(m2.group(1).strip())
                continue
            text_lines.append(ln)
        if pid:
            obs[pid] = " ".join(text_lines)
    return obs

def suggest_icd10_codes(observation_text, top_n=3):
    if not observation_text:
        return []
    text = observation_text.lower()
    found = {}
    # exact keyword matches
    for kw in ICD_KEYWORDS:
        if kw in text:
            code, desc = ICD_KEYWORD_MAP[kw]
            found[code] = max(found.get(code, 0), 100)
    # fuzzy matching if library available
    if process is not None:
        results = process.extract(text, ICD_KEYWORDS, limit=top_n)
        for match_kw, score in results:
            if score < 60:
                continue
            code, desc = ICD_KEYWORD_MAP[match_kw]
            found[code] = max(found.get(code, 0), score)
    # build unique sorted list
    unique = {}
    for kw in ICD_KEYWORDS:
        code, desc = ICD_KEYWORD_MAP[kw]
        if code in found and code not in unique:
            unique[code] = (desc, found[code])
    out = [(code, desc, unique[code][1]) for code, desc in unique.items()]
    out = sorted(out, key=lambda x: x[2], reverse=True)[:top_n]
    return out

def generate_clinical_note(row, observation_text):
    name = row.get('name','').strip()
    pid = row.get('patient_id','').strip()
    age = row.get('age','').strip()
    sex = row.get('sex','').strip()
    cc = row.get('chief_complaint','').strip()
    vitals = row.get('vitals','').strip()
    labs = row.get('lab_summary','').strip()

    lines = []
    lines.append(f"Patient: {name} (ID: {pid}), Age: {age}, Sex: {sex}")
    lines.append("")
    history = cc or observation_text or "No specific complaint recorded."
    lines.append("History of Present Illness:")
    lines.append(history)
    lines.append("")
    lines.append("Examination / Vitals:")
    lines.append(vitals if vitals else "Vitals not provided.")
    lines.append("")
    lines.append("Relevant Labs / Imaging:")
    lines.append(labs if labs else "None provided.")
    lines.append("")
    impression = observation_text or cc or "Clinical impression not available."
    lines.append("Impression:")
    lines.append(impression)
    lines.append("")
    lines.append("Plan:")
    lines.append("1. Diagnostic confirmation as needed (labs/imaging).")
    lines.append("2. Start guideline-directed therapy based on impression.")
    lines.append("3. Follow-up as clinically indicated.")
    return "\\n".join(lines)

def main(patients_csv, observations_txt, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    patients = load_patients(patients_csv)
    observations = load_observations(observations_txt) if observations_txt else {}
    rows_out = []
    for _, row in patients.iterrows():
        pid = str(row['patient_id'])
        obs_text = observations.get(pid, "")
        if 'doctor_notes' in patients.columns and not obs_text:
            obs_text = str(row.get('doctor_notes',''))
        generated_note = generate_clinical_note(row, obs_text)
        icd_suggestions = suggest_icd10_codes(obs_text if obs_text else row.get('chief_complaint',''))
        codes = "; ".join([f"{c} ({d})[{s:.0f}]" for c,d,s in icd_suggestions])
        avg_conf = round(sum([s for _,_,s in icd_suggestions])/len(icd_suggestions),1) if icd_suggestions else 0.0
        rows_out.append({
            'patient_id': pid,
            'name': row.get('name',''),
            'generated_note': generated_note,
            'suggested_icd10_codes': codes,
            'icd_confidence': avg_conf
        })
    out_df = pd.DataFrame(rows_out)
    csv_out = os.path.join(output_dir, 'clinical_notes_icd_suggestions.csv')
    out_df.to_csv(csv_out, index=False)
    report_path = os.path.join(output_dir, 'report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Clinical Note Generation & ICD-10 Coding Report\\n\\n")
        f.write(f"Processed {len(out_df)} patients.\\n\\n")
        f.write("Columns saved to clinical_notes_icd_suggestions.csv\\n\\n")
        f.write("Sample entries:\\n\\n")
        for i, r in out_df.head(3).iterrows():
            f.write(f"## Patient {r['patient_id']} - {r['name']}\\n")
            f.write("Suggested ICD-10 codes: " + (r['suggested_icd10_codes'] or "None") + "\\n\\n")
            f.write("Generated note:\\n\\n")
            f.write("```\n" + r['generated_note'] + "\n```\n\\n")
    print("Done. Outputs:")
    print(" -", csv_out)
    print(" -", report_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clinical Note Generation & ICD-10 Coding Automation Demo")
    parser.add_argument('--patients', type=str, required=True, help='CSV file with patient rows (must include patient_id column)')
    parser.add_argument('--observations', type=str, required=False, default='', help='Optional observations text file (see README)')
    parser.add_argument('--output_dir', type=str, default='./cn_output', help='Folder to save generated notes and suggestions')
    args = parser.parse_args()
    main(args.patients, args.observations, args.output_dir)

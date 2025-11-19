import os
import csv
import random
import shutil
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

BASE_DIR = os.path.abspath("medical_prep_output")
DATA_DIR = os.path.join(BASE_DIR, "dataset")
IMAGING_DIR = os.path.join(DATA_DIR, "images")
EHR_FILE = os.path.join(BASE_DIR, "ehr.csv")
NOTES_FILE = os.path.join(BASE_DIR, "notes.csv")
LABELS_FILE = os.path.join(BASE_DIR, "labels.csv")
REPORT_FILE = os.path.join(BASE_DIR, "report.html")
ZIP_FILE = os.path.join(BASE_DIR, "medical_dataset.zip")

for path in [BASE_DIR, DATA_DIR, IMAGING_DIR]:
    os.makedirs(path, exist_ok=True)

def create_dummy_image_data():
    modalities = ["Xray", "MRI", "CT", "Ultrasound", "DXA"]
    data_records = []
    for i in range(1, 11):
        modality = random.choice(modalities)
        image_path = os.path.join(IMAGING_DIR, f"{modality}_{i}.npy")
        np.save(image_path, np.random.rand(64, 64))
        data_records.append([i, modality, image_path])
    df = pd.DataFrame(data_records, columns=["patient_id", "modality", "image_path"])
    df.to_csv(LABELS_FILE, index=False)
    return df

def create_dummy_ehr_data():
    ehr_data = []
    notes_data = []
    icd_codes = ["I10", "E11", "J45", "K21", "M54"]
    for i in range(1, 11):
        ehr_data.append([
            i,
            random.randint(25, 80),
            random.choice(["M", "F"]),
            random.choice(icd_codes),
            round(random.uniform(36.0, 39.5), 1),
            round(random.uniform(70.0, 100.0), 1),
        ])
        notes_data.append([
            i,
            random.choice([
                "Patient stable. Continue treatment.",
                "Needs further MRI scan.",
                "High blood pressure observed.",
                "Recommend physiotherapy.",
                "Blood sugar level within range."
            ])
        ])
    with open(EHR_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["patient_id", "age", "gender", "icd10_code", "temperature", "weight"])
        writer.writerows(ehr_data)
    with open(NOTES_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["patient_id", "notes"])
        writer.writerows(notes_data)

create_dummy_ehr_data()
image_df = create_dummy_image_data()

ehr_df = pd.read_csv(EHR_FILE)
ehr_df = ehr_df.dropna()
ehr_df["icd10_code"] = ehr_df["icd10_code"].str.strip()
ehr_df.to_csv(EHR_FILE, index=False)

plt.figure(figsize=(5, 4))
ehr_df["age"].hist(bins=5)
plt.title("Age Distribution of Patients")
plt.xlabel("Age")
plt.ylabel("Count")
plot_path = os.path.join(BASE_DIR, "age_distribution.png")
plt.savefig(plot_path)
plt.close()

with open(REPORT_FILE, "w") as f:
    f.write("<h1>Medical Data Preparation Report</h1>")
    f.write(f"<p><b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    f.write("<h2>Sample EHR Data</h2>")
    f.write(ehr_df.head().to_html(index=False))
    f.write("<h2>Sample Image Labels</h2>")
    f.write(image_df.head().to_html(index=False))
    f.write(f"<h2>Visualization</h2><img src='{plot_path}' width='400'><br>")
    f.write("<h2>Dataset Links</h2>")
    f.write("<ul>")
    f.write(f"<li><a href='{EHR_FILE}'>EHR CSV</a></li>")
    f.write(f"<li><a href='{NOTES_FILE}'>Notes CSV</a></li>")
    f.write(f"<li><a href='{LABELS_FILE}'>Labels CSV</a></li>")
    f.write("</ul>")

with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zipf:
    for foldername, _, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            if filename != os.path.basename(ZIP_FILE):
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, BASE_DIR)
                zipf.write(file_path, arcname)

print("Medical data preparation completed successfully!")
print(f"Output directory: {BASE_DIR}")
print(f"Open this report in browser: {REPORT_FILE}")

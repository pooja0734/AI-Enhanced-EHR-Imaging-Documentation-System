# 🏥 EHR AI System
> AI-Powered Imaging & Intelligent Clinical Documentation Platform


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 62.1+](https://img.shields.io/badge/python-62.1+-blue.svg)](https://www.python.org/downloads/)
[![javascript 36.4](https://img.shields.io/badge/javascript-36.4-yellow.svg)](https://javascript.org)
[![HTML 0.3](https://img.shields.io/badge/HTML-0.3-orange.svg)](https://HTML.tiangolo.com)
[![CSS 1.2](https://img.shields.io/badge/CSS-1.2-purple.svg)](https://CSS.org)

📌 Project Overview

This project integrates AI, automation, and healthcare data workflows to build an enhanced Electronic Health Record (EHR) system that supports:

🧠 AI-generated clinical notes

📘 Automated ICD-10 coding

🖼️ Medical imaging enhancement (X-ray, CT, General)

📂 EHR dataset creation & preprocessing

⚙️ Backend APIs for hospital/EHR integration

📊 Agile documentation for software development process

It is designed for academic submissions, healthcare AI prototypes, and production-ready research demos.

🎯 Core Features

🔹 1. AI Clinical Note & ICD-10 Automation

Powered by EHR_3.py
Generates structured SOAP-style clinical notes
Maps symptoms → ICD-10 codes using keyword + fuzzy matching
Produces confidence scores
Saves results in CSV + Markdown format

🔹 2. Medical Imaging Enhancement Pipeline

Handled by EHR_2.py
Supports:
X-ray
CT
General medical images
Enhancement includes:
Noise removal
Sharpening
SSIM & PSNR quality scoring
Auto-saving enhanced images

🔹 3. EHR Data Generator & Report Creator

EHR_1.py generates:
Synthetic patient EHR dataset
Notes CSV
Imaging labels
Visualizations (age distribution)
HTML report summarizing data

🔹 4. Integration & Deployment Documentation

EHR_4.py generates:
Milestone 4: Integration & Deployment
PDF + markdown documentation
Explains APIs, security, HIPAA alignment, monitoring & rollout

🔹 5. Backend API (Node.js + Express)

Inside the /backend folder:
REST APIs for patient records
CRUD operations
Middleware (body-parser, routing, security basics)
Serves as a layer to integrate AI modules into a clinical workflow

🔹 6. Agile Documentation Folder

Includes:
Sprint backlog
Product backlog
Standup logs
Retrospection
Unit tests
Defect tracker
Perfect for college or organizational software development lifecycle (SDLC) submissions.

📁 Project Structure

AI-Enhanced-EHR-Imaging-Documentation-System/

│
├── EHR_1.py                           # EHR Dataset Generator + Reports

├── EHR_2.py                           # Medical Image Enhancement Pipeline

├── EHR_3.py                           # Clinical Notes + ICD-10 Coding

├── EHR_4.py                           # Integration & Deployment Docs (PDF/MD)

├── backend/                           # Node.js Express backend API

│   ├── routes/

│   ├── models/

│   ├── controllers/

│   └── server.js

├── agile documentation/               # All Agile SDLC Excel Sheets

├── README.md                          # Documentation (replace with this file)

└── LICENSE


🛠️ Installation & Setup

1️⃣ Install Python Dependencies

Create a virtual environment (optional):
pip install pandas numpy matplotlib opencv-python tqdm scikit-image fuzzywuzzy python-Levenshtein reportlab

2️⃣ Install Backend Dependencies

Inside /backend:
npm install
Run the backend API:
npm start

▶️ How to Use the Python Scripts

✔ Generate EHR Dataset
python EHR_1.py

Creates:
ehr.csv
notes.csv
labels.csv
report.html
age_distribution.png

✔ Enhance Medical Images
python EHR_2.py --input_dir input_images --output_dir results --modality xray


Outputs:

Enhanced images
Metrics (PSNR, SSIM)

✔ Generate Clinical Notes + ICD Codes
python EHR_3.py --patients patients.csv --observations observations.txt --output_dir output_notes


Outputs:

clinical_notes_icd_suggestions.csv
report.md

✔ Generate Milestone 4 Deployment Docs
python EHR_4.py


Outputs:

Milestone4_Integration_Deployment.md

Milestone4_Integration_Deployment.pdf

📊 Outputs Summary

Module	Output
EHR_1.py	EHR data, CSVs, HTML report, charts

EHR_2.py	Enhanced images, metrics.csv

EHR_3.py	Clinical notes, ICD-10 code suggestions

EHR_4.py	Deployment documentation (PDF + MD)

Backend	REST API for EHR records

🛡️ Security & Compliance

This project includes guidelines aligned with:

HIPAA
Data encryption
Secure medical workflows
Role-based access in hospital IT systems

💡 Use Cases

Healthcare automation projects
AI medical documentation
Imaging preprocessing research
University/college final-year projects
Clinical NLP & ML workflows
Full-stack EHR system development

📜 License

This project is for educational and internship purposes under Infosys.

🏁 Conclusion

The AI-Powered Enhanced EHR Imaging & Documentation System is a step toward automating clinical workflows using Generative AI. It enhances both diagnostic support and administrative efficiency, allowing medical staff to focus more on patient care.

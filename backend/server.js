const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// ----------------------------
// TEST ROUTE
// ----------------------------
app.get("/", (req, res) => {
  res.json({ message: "Backend running successfully!" });
});

// ----------------------------
// IMAGE ENHANCEMENT (MOCK)
// ----------------------------
app.post("/image-enhancement", (req, res) => {
  res.json({
    success: true,
    enhanced_image: "BASE64_IMAGE_DATA_HERE",
    message: "Image enhanced successfully (mock response)."
  });
});

// ----------------------------
// CLINICAL NOTES (MOCK)
// ----------------------------
app.post("/clinical-notes", (req, res) => {
  const { note_type } = req.body;

  if (note_type === "soap") {
    res.json({
      note: "SOAP note: Subjective, Objective, Assessment, Plan (mock)"
    });
  } else if (note_type === "discharge") {
    res.json({
      note: "Discharge Summary generated successfully (mock)"
    });
  } else if (note_type === "radiology") {
    res.json({
      note: "Radiology Report generated successfully (mock)"
    });
  } else {
    res.status(400).json({ error: "Invalid note type" });
  }
});

// ----------------------------
// ICD-10 CODING (MOCK)
// ----------------------------
app.post("/icd10-coding", (req, res) => {
  res.json({
    codes: [
      { code: "A00", description: "Cholera" },
      { code: "B20", description: "HIV disease" }
    ]
  });
});

// ----------------------------
// PATIENT MANAGEMENT
// ----------------------------
let patients = [
  { id: 1, name: "John Doe", age: 30, diagnosis: "Fever" },
  { id: 2, name: "Jane Doe", age: 28, diagnosis: "Cough" }
];

app.get("/patients", (req, res) => {
  res.json(patients);
});

app.get("/patients/:id", (req, res) => {
  const patient = patients.find(p => p.id === parseInt(req.params.id));
  if (!patient) return res.status(404).json({ error: "Patient not found" });
  res.json(patient);
});

app.post("/patients", (req, res) => {
  const newPatient = {
    id: patients.length + 1,
    ...req.body
  };
  patients.push(newPatient);
  res.json({ message: "Patient added", patient: newPatient });
});

app.put("/patients/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const index = patients.findIndex(p => p.id === id);

  if (index === -1) return res.status(404).json({ error: "Patient not found" });

  patients[index] = { ...patients[index], ...req.body };
  res.json({ message: "Patient updated", patient: patients[index] });
});

// ----------------------------
// START SERVER
// ----------------------------
app.listen(5000, () => {
  console.log("Backend running at http://localhost:5000");
});

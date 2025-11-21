ICD10_CODES = {
    "fever": "R50.9",
    "headache": "R51",
    "diabetes": "E11.9",
    "hypertension": "I10",
    "cough": "R05"
}

def suggest_codes(text):
    text = text.lower()
    results = []

    for keyword, code in ICD10_CODES.items():
        if keyword in text:
            results.append({"keyword": keyword, "code": code})

    return {"matches": results or [{"message": "No matching ICD-10 codes found"}]}

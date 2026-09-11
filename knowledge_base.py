"""
knowledge_base.py
------------------
Central place for the "medical knowledge" this academic project uses:
symptoms list, diseases, which symptoms map to which disease (used to
generate training data), suggested medicines, and hospitals.

NOTE: This is simplified data for a college/academic project only.
It is NOT medically validated and must never be used for real diagnosis.
"""

# Master list of symptoms the model knows about (order matters - this
# is the exact column order used to build the feature vector).
SYMPTOMS = [
    "fever", "headache", "cough", "fatigue", "nausea", "vomiting",
    "joint_pain", "skin_rash", "chills", "sore_throat", "body_ache",
    "diarrhea", "abdominal_pain", "loss_of_appetite", "dizziness",
    "shortness_of_breath", "chest_pain", "runny_nose", "sneezing",
    "sweating", "weight_loss", "frequent_urination", "excessive_thirst",
    "blurred_vision", "yellowing_of_eyes", "dark_urine", "constipation",
    "muscle_weakness", "night_sweats", "swollen_lymph_nodes",
]

# disease_name -> (specialization, [typical symptoms])
DISEASES = {
    "Typhoid": ("General Medicine",
                ["fever", "headache", "fatigue", "abdominal_pain", "loss_of_appetite", "constipation"]),
    "Common Cold": ("General Medicine",
                    ["runny_nose", "sneezing", "sore_throat", "cough", "headache"]),
    "Influenza (Flu)": ("General Medicine",
                        ["fever", "chills", "body_ache", "fatigue", "cough", "sore_throat"]),
    "Malaria": ("General Medicine",
                ["fever", "chills", "sweating", "headache", "nausea", "body_ache"]),
    "Dengue": ("General Medicine",
               ["fever", "joint_pain", "skin_rash", "headache", "fatigue", "nausea"]),
    "Migraine": ("Neurology",
                 ["headache", "dizziness", "blurred_vision", "nausea"]),
    "Gastroenteritis": ("Gastroenterology",
                        ["diarrhea", "vomiting", "abdominal_pain", "nausea", "fever"]),
    "Diabetes (Type 2)": ("Endocrinology",
                          ["frequent_urination", "excessive_thirst", "fatigue", "weight_loss", "blurred_vision"]),
    "Hepatitis A": ("Gastroenterology",
                    ["yellowing_of_eyes", "dark_urine", "loss_of_appetite", "fatigue", "abdominal_pain", "nausea"]),
    "Asthma": ("Pulmonology",
               ["shortness_of_breath", "chest_pain", "cough", "fatigue"]),
    "Tuberculosis": ("Pulmonology",
                     ["cough", "night_sweats", "weight_loss", "fatigue", "chest_pain"]),
    "Rheumatoid Arthritis": ("Orthopedics",
                             ["joint_pain", "muscle_weakness", "fatigue", "swollen_lymph_nodes"]),
    "Chickenpox": ("Dermatology",
                   ["skin_rash", "fever", "fatigue", "loss_of_appetite"]),
    "Urinary Tract Infection": ("Urology",
                                ["frequent_urination", "abdominal_pain", "fever", "dark_urine"]),
    "Anemia": ("General Medicine",
               ["fatigue", "dizziness", "muscle_weakness", "shortness_of_breath"]),
}

# disease_name -> [(medicine, dosage_note), ...]
MEDICINES = {
    "Typhoid": [("Azithromycin", "500mg once daily for 7 days"), ("Paracetamol", "As needed for fever")],
    "Common Cold": [("Cetirizine", "10mg once daily"), ("Paracetamol", "As needed for fever/pain")],
    "Influenza (Flu)": [("Oseltamivir", "75mg twice daily for 5 days"), ("Paracetamol", "As needed")],
    "Malaria": [("Artemether-Lumefantrine", "As per weight-based dosing"), ("Paracetamol", "As needed for fever")],
    "Dengue": [("Paracetamol", "As needed for fever - avoid NSAIDs"), ("ORS", "Maintain hydration")],
    "Migraine": [("Sumatriptan", "50mg at onset"), ("Ibuprofen", "400mg as needed")],
    "Gastroenteritis": [("ORS", "Rehydration solution"), ("Ondansetron", "4mg for nausea")],
    "Diabetes (Type 2)": [("Metformin", "500mg twice daily"), ("Lifestyle & diet counseling", "Ongoing")],
    "Hepatitis A": [("Supportive care", "Rest & hydration"), ("Paracetamol (low dose)", "Avoid liver-toxic drugs")],
    "Asthma": [("Salbutamol inhaler", "As needed for attacks"), ("Budesonide inhaler", "Daily maintenance")],
    "Tuberculosis": [("Rifampicin + Isoniazid", "As per DOTS regimen"), ("Pyridoxine", "Supportive")],
    "Rheumatoid Arthritis": [("Methotrexate", "Weekly, as prescribed"), ("Ibuprofen", "For pain/inflammation")],
    "Chickenpox": [("Calamine lotion", "Apply on rashes"), ("Paracetamol", "As needed for fever")],
    "Urinary Tract Infection": [("Nitrofurantoin", "100mg twice daily for 5 days"), ("Increase fluid intake", "Ongoing")],
    "Anemia": [("Ferrous sulfate", "1 tablet daily"), ("Vitamin B12/Folic acid", "As prescribed")],
}

# specialization -> [(hospital_name, location, contact), ...]
HOSPITALS = {
    "General Medicine": [("City General Hospital", "MG Road", "022-2345001")],
    "Neurology": [("Neuro Care Institute", "Andheri West", "022-2345002")],
    "Gastroenterology": [("Digestive Health Center", "Dadar", "022-2345003")],
    "Endocrinology": [("Metro Diabetes & Endocrine Clinic", "Bandra", "022-2345004")],
    "Pulmonology": [("Lung & Chest Care Hospital", "Powai", "022-2345005")],
    "Orthopedics": [("OrthoLife Hospital", "Thane", "022-2345006")],
    "Dermatology": [("SkinCare Multispeciality", "Vashi", "022-2345007")],
    "Urology": [("Urology & Kidney Institute", "Kurla", "022-2345008")],
}

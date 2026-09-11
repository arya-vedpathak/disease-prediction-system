"""
generate_seed_sql.py
----------------------
Turns knowledge_base.py into seed_data.sql - the INSERT statements
that populate symptoms_master, diseases_master, disease_medicine and
hospitals. Run this once (after schema.sql) to prepare reference data:

    python generate_seed_sql.py
    mysql -u root -p disease_prediction_db < schema.sql
    mysql -u root -p disease_prediction_db < seed_data.sql
"""

from knowledge_base import SYMPTOMS, DISEASES, MEDICINES, HOSPITALS


def esc(text):
    return text.replace("'", "''")


def main():
    lines = ["USE disease_prediction_db;\n"]

    lines.append("-- Symptoms")
    for s in SYMPTOMS:
        pretty = s.replace("_", " ").title()
        lines.append(f"INSERT IGNORE INTO symptoms_master (symptom_name) VALUES ('{esc(pretty)}');")

    lines.append("\n-- Diseases")
    for disease, (specialization, _symptoms) in DISEASES.items():
        lines.append(
            f"INSERT IGNORE INTO diseases_master (disease_name, specialization) "
            f"VALUES ('{esc(disease)}', '{esc(specialization)}');"
        )

    lines.append("\n-- Medicines")
    for disease, meds in MEDICINES.items():
        for med_name, note in meds:
            lines.append(
                "INSERT INTO disease_medicine (disease_id, medicine_name, dosage_note) "
                f"SELECT disease_id, '{esc(med_name)}', '{esc(note)}' FROM diseases_master "
                f"WHERE disease_name='{esc(disease)}';"
            )

    lines.append("\n-- Hospitals")
    for specialization, hospitals in HOSPITALS.items():
        for name, location, contact in hospitals:
            lines.append(
                "INSERT INTO hospitals (name, specialization, location, contact) VALUES "
                f"('{esc(name)}', '{esc(specialization)}', '{esc(location)}', '{esc(contact)}');"
            )

    with open("seed_data.sql", "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"seed_data.sql written with {len(SYMPTOMS)} symptoms, {len(DISEASES)} diseases,"
          f" {sum(len(v) for v in MEDICINES.values())} medicine rows,"
          f" {sum(len(v) for v in HOSPITALS.values())} hospitals.")


if __name__ == "__main__":
    main()

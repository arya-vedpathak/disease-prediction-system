# MediPredict — Disease Prediction System

A desktop app built **entirely in Python + MySQL** — no web framework, no
HTML/CSS/JS. Patient details, symptoms, and lab reports go into MySQL; a
scikit-learn model predicts the likely disease and suggests medicine +
a hospital, pulled from the database. It starts empty — every number
and record you see is real data you've entered, not a demo/sample.

## Tech stack
- **UI:** `customtkinter` (dark, colored theme)
- **Database:** MySQL, via `mysql-connector-python`
- **ML:** `scikit-learn` (RandomForestClassifier)
- **Charts:** `matplotlib` embedded in the dashboard

## Project files
```
disease_prediction/
├── schema.sql            # MySQL tables — run first
├── knowledge_base.py     # symptoms / diseases / medicines / hospitals data
├── generate_seed_sql.py  # turns knowledge_base.py into seed_data.sql
├── seed_data.sql         # generated — reference data to load into MySQL
├── train_model.py        # trains the ML model → model.pkl
├── db.py                 # all MySQL queries live here
├── theme.py               # color palette
├── main.py                # the actual app — RUN THIS
├── requirements.txt
└── .env.example
```

## Setup (one-time)

**1. Install MySQL** if you don't have it (MySQL Server + Workbench, or XAMPP's MySQL).

**2. Install Python packages**
```bash
pip install -r requirements.txt
```

**3. Create the database + tables**
```bash
mysql -u root -p < schema.sql
```

**4. Load reference data (symptoms, diseases, medicines, hospitals)**
```bash
python generate_seed_sql.py
mysql -u root -p disease_prediction_db < seed_data.sql
```

**5. Set your MySQL password** so `db.py` can connect. Easiest way —
open a terminal and set it before running the app:
```bash
# Windows (cmd)
set DB_PASSWORD=your_mysql_password

# Mac/Linux
export DB_PASSWORD=your_mysql_password
```
(Or edit the defaults directly in `db.py` — see `.env.example` for all
available settings: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.)

**6. Train the ML model**
```bash
python train_model.py
```
This creates `model.pkl`, `symptoms.pkl`, `label_encoder.pkl` — the app
loads these at startup, so run this once before first launch (and
again any time you change `knowledge_base.py`).

**7. Run the app**
```bash
python main.py
```

Login with **admin / admin123** (default seeded user — change this in
`users` table for a real deployment).

## How it works (data flow)
```
Login
 → Add Patient           → INSERT into patients, get patient_id
 → Add Symptoms          → checklist saved to patient_symptoms
 → Add Lab Report        → saved to lab_reports
 → Predict                → symptoms fetched from MySQL → converted to a
                              0/1 feature vector → model.predict_proba()
                              → result saved to predictions table
 → Medicine + Hospital    → auto looked-up from disease_medicine /
                              hospitals tables using the predicted disease
 → History                → past symptoms/reports/predictions per patient
 → Dashboard               → live counts + a chart of most-predicted
                              diseases, generated from your real data
```

## Notes
- All data is real — the dashboard, history, and stats only show what
  you've actually entered through the app. There is no fake/demo data
  baked in beyond the reference tables (symptoms/diseases/medicines/
  hospitals) needed for the app to function.
- The ML model is trained on a **synthetic dataset** generated from
  `knowledge_base.py` for academic purposes — clearly label this in any
  report/viva as a simplified educational model, not a clinically
  validated one.
- Change the default admin password before sharing this with anyone.
- To turn this into a `.exe` later: `pip install pyinstaller` then
  `pyinstaller --onefile --windowed main.py`.

**Disclaimer:** This project is for academic/educational purposes only
and must not be used for real medical diagnosis.

"""
db.py
------
Single place for all MySQL access. Every screen in main.py imports
functions from here instead of writing raw SQL inline.

Reads connection settings from environment variables (with sensible
local defaults) so you never hardcode a password in the code -
see .env.example.
"""

import os
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "arya@1234"),
    "database": os.environ.get("DB_NAME", "disease_prediction_db"),
}


def get_connection():
    """Open a fresh MySQL connection. Caller is responsible for closing it."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        raise ConnectionError(
            f"Could not connect to MySQL ({DB_CONFIG['host']}/{DB_CONFIG['database']}): {e}"
        )


def run_query(query, params=None, fetch=False, fetchone=False, commit=False):
    """
    Generic helper: opens a connection, runs one query, optionally
    fetches results or commits, then always closes the connection.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = None
        if fetch:
            result = cursor.fetchall()
        elif fetchone:
            result = cursor.fetchone()
        if commit:
            conn.commit()
            result = cursor.lastrowid
        return result
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------
# Auth
# ---------------------------------------------------------------

def verify_login(username, password):
    return run_query(
        "SELECT user_id, username, role FROM users WHERE username=%s AND password=%s",
        (username, password),
        fetchone=True,
    )


# ---------------------------------------------------------------
# Patients
# ---------------------------------------------------------------

def add_patient(name, age, gender, contact, address):
    return run_query(
        "INSERT INTO patients (name, age, gender, contact, address) VALUES (%s,%s,%s,%s,%s)",
        (name, age, gender, contact, address),
        commit=True,
    )


def get_all_patients():
    return run_query(
        "SELECT patient_id, name, age, gender, contact, registered_on FROM patients ORDER BY patient_id DESC",
        fetch=True,
    )


def get_patient(patient_id):
    return run_query(
        "SELECT * FROM patients WHERE patient_id=%s", (patient_id,), fetchone=True
    )


# ---------------------------------------------------------------
# Symptoms
# ---------------------------------------------------------------

def get_all_symptoms():
    return run_query(
        "SELECT symptom_id, symptom_name FROM symptoms_master ORDER BY symptom_name",
        fetch=True,
    )


def save_patient_symptoms(patient_id, symptom_ids):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(
            "INSERT INTO patient_symptoms (patient_id, symptom_id) VALUES (%s,%s)",
            [(patient_id, sid) for sid in symptom_ids],
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_patient_symptoms(patient_id):
    return run_query(
        """SELECT s.symptom_name, ps.report_date FROM patient_symptoms ps
           JOIN symptoms_master s ON ps.symptom_id = s.symptom_id
           WHERE ps.patient_id=%s ORDER BY ps.report_date DESC""",
        (patient_id,),
        fetch=True,
    )


# ---------------------------------------------------------------
# Lab reports
# ---------------------------------------------------------------

def add_lab_report(patient_id, test_name, value, unit):
    return run_query(
        "INSERT INTO lab_reports (patient_id, test_name, value, unit) VALUES (%s,%s,%s,%s)",
        (patient_id, test_name, value, unit),
        commit=True,
    )


def get_patient_lab_reports(patient_id):
    return run_query(
        "SELECT test_name, value, unit, report_date FROM lab_reports WHERE patient_id=%s ORDER BY report_date DESC",
        (patient_id,),
        fetch=True,
    )


# ---------------------------------------------------------------
# Diseases / medicine / hospitals
# ---------------------------------------------------------------

def get_disease_by_name(disease_name):
    return run_query(
        "SELECT * FROM diseases_master WHERE disease_name=%s", (disease_name,), fetchone=True
    )


def get_medicines_for_disease(disease_id):
    return run_query(
        "SELECT medicine_name, dosage_note FROM disease_medicine WHERE disease_id=%s",
        (disease_id,),
        fetch=True,
    )


def get_hospitals_for_specialization(specialization):
    return run_query(
        "SELECT name, location, contact FROM hospitals WHERE specialization=%s",
        (specialization,),
        fetch=True,
    )


# ---------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------

def save_prediction(patient_id, disease_id, confidence):
    return run_query(
        "INSERT INTO predictions (patient_id, disease_id, confidence) VALUES (%s,%s,%s)",
        (patient_id, disease_id, confidence),
        commit=True,
    )


def get_patient_predictions(patient_id):
    return run_query(
        """SELECT d.disease_name, p.confidence, p.predicted_on FROM predictions p
           JOIN diseases_master d ON p.disease_id = d.disease_id
           WHERE p.patient_id=%s ORDER BY p.predicted_on DESC""",
        (patient_id,),
        fetch=True,
    )


# ---------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------

def get_dashboard_stats():
    total_patients = run_query("SELECT COUNT(*) c FROM patients", fetchone=True)["c"]
    today_patients = run_query(
        "SELECT COUNT(*) c FROM patients WHERE DATE(registered_on)=CURDATE()", fetchone=True
    )["c"]
    total_predictions = run_query("SELECT COUNT(*) c FROM predictions", fetchone=True)["c"]
    disease_counts = run_query(
        """SELECT d.disease_name, COUNT(*) as cnt FROM predictions p
           JOIN diseases_master d ON p.disease_id = d.disease_id
           GROUP BY d.disease_name ORDER BY cnt DESC LIMIT 6""",
        fetch=True,
    )
    return {
        "total_patients": total_patients,
        "today_patients": today_patients,
        "total_predictions": total_predictions,
        "disease_counts": disease_counts,
    }

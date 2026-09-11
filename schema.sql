-- ============================================================
-- Disease Prediction System - Database Schema
-- Run this once in MySQL Workbench / phpMyAdmin / CLI to set up
-- ============================================================

CREATE DATABASE IF NOT EXISTS disease_prediction_db;
USE disease_prediction_db;

-- Login users (doctor / receptionist / admin)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'doctor', 'receptionist') DEFAULT 'receptionist',
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    contact VARCHAR(20),
    address VARCHAR(255),
    registered_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master list of all symptoms the model understands
CREATE TABLE IF NOT EXISTS symptoms_master (
    symptom_id INT AUTO_INCREMENT PRIMARY KEY,
    symptom_name VARCHAR(100) UNIQUE NOT NULL
);

-- Symptoms reported by a patient on a given date
CREATE TABLE IF NOT EXISTS patient_symptoms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    symptom_id INT NOT NULL,
    report_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptoms_master(symptom_id) ON DELETE CASCADE
);

-- Lab report entries
CREATE TABLE IF NOT EXISTS lab_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    test_name VARCHAR(100) NOT NULL,
    value VARCHAR(50) NOT NULL,
    unit VARCHAR(20),
    report_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Master list of diseases the model can predict
CREATE TABLE IF NOT EXISTS diseases_master (
    disease_id INT AUTO_INCREMENT PRIMARY KEY,
    disease_name VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(100)
);

-- Suggested medicines per disease
CREATE TABLE IF NOT EXISTS disease_medicine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    disease_id INT NOT NULL,
    medicine_name VARCHAR(150) NOT NULL,
    dosage_note VARCHAR(255),
    FOREIGN KEY (disease_id) REFERENCES diseases_master(disease_id) ON DELETE CASCADE
);

-- Hospitals, tagged by specialization
CREATE TABLE IF NOT EXISTS hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    specialization VARCHAR(100),
    location VARCHAR(150),
    contact VARCHAR(20)
);

-- Every prediction made, for history + dashboard
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    disease_id INT NOT NULL,
    confidence DECIMAL(5,2),
    predicted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (disease_id) REFERENCES diseases_master(disease_id) ON DELETE CASCADE
);

-- Default admin login (username: admin / password: admin123)
INSERT IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');

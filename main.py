"""
main.py
--------
Disease Prediction System - main application.

Run with:  python main.py

Requires:
  - MySQL server running with the schema + seed data loaded (see README.md)
  - model.pkl / symptoms.pkl / label_encoder.pkl present (run train_model.py first)
"""

import customtkinter as ctk
import joblib
import numpy as np
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import db
import theme as t
from knowledge_base import SYMPTOMS

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =================================================================
# Small reusable widgets
# =================================================================

class StatTile(ctk.CTkFrame):
    def __init__(self, master, label, value, color=t.PURPLE, **kwargs):
        super().__init__(master, fg_color=t.BG_CARD, corner_radius=10, **kwargs)
        ctk.CTkLabel(self, text=label, font=(t.FONT_FAMILY, 11), text_color=t.TEXT_MUTED).pack(
            anchor="w", padx=12, pady=(10, 0)
        )
        self.value_label = ctk.CTkLabel(
            self, text=str(value), font=(t.FONT_FAMILY, 20, "bold"), text_color=color
        )
        self.value_label.pack(anchor="w", padx=12, pady=(0, 10))

    def set_value(self, value):
        self.value_label.configure(text=str(value))


class SidebarButton(ctk.CTkButton):
    def __init__(self, master, text, icon, command, **kwargs):
        super().__init__(
            master,
            text=f"{icon}\n{text}",
            command=command,
            width=84,
            height=56,
            corner_radius=10,
            fg_color="transparent",
            hover_color=t.BG_CARD_ALT,
            font=(t.FONT_FAMILY, 11),
            **kwargs,
        )


# =================================================================
# Main application
# =================================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MediPredict - Disease Prediction System")
        self.geometry("1100x680")
        self.configure(fg_color=t.BG_MAIN)

        self.current_user = None
        self.selected_patient_id = None

        # Load ML artifacts once at startup
        try:
            self.model = joblib.load("model.pkl")
            self.symptoms_list = joblib.load("symptoms.pkl")
            self.label_encoder = joblib.load("label_encoder.pkl")
        except FileNotFoundError:
            self.model = None
            self.symptoms_list = SYMPTOMS
            self.label_encoder = None

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_login()

    # -------------------------------------------------------
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_container()
        LoginScreen(self.container, self)

    def show_main_app(self):
        self.clear_container()
        MainAppScreen(self.container, self)


# =================================================================
# Login screen
# =================================================================

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, app: App):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        card = ctk.CTkFrame(self, fg_color=t.BG_CARD, corner_radius=16, width=360)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card, text="⚕  MediPredict", font=(t.FONT_FAMILY, 22, "bold"), text_color=t.PURPLE
        ).pack(padx=40, pady=(30, 4))
        ctk.CTkLabel(
            card, text="Disease Prediction System", font=(t.FONT_FAMILY, 12), text_color=t.TEXT_MUTED
        ).pack(pady=(0, 24))

        self.username_entry = ctk.CTkEntry(card, placeholder_text="Username", width=280, height=38)
        self.username_entry.pack(padx=40, pady=6)

        self.password_entry = ctk.CTkEntry(
            card, placeholder_text="Password", show="*", width=280, height=38
        )
        self.password_entry.pack(padx=40, pady=6)

        self.error_label = ctk.CTkLabel(card, text="", text_color=t.PINK, font=(t.FONT_FAMILY, 11))
        self.error_label.pack(pady=(4, 0))

        ctk.CTkButton(
            card,
            text="Login",
            width=280,
            height=40,
            fg_color=t.PURPLE,
            hover_color=t.PURPLE_DARK,
            command=self.attempt_login,
        ).pack(padx=40, pady=(14, 10))

        ctk.CTkLabel(
            card,
            text="Default: admin / admin123",
            font=(t.FONT_FAMILY, 10),
            text_color=t.TEXT_MUTED,
        ).pack(pady=(0, 24))

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            user = db.verify_login(username, password)
        except ConnectionError as e:
            self.error_label.configure(text=str(e))
            return

        if user:
            self.app.current_user = user
            self.app.show_main_app()
        else:
            self.error_label.configure(text="Invalid username or password")


# =================================================================
# Main app shell: sidebar + swappable content area
# =================================================================

class MainAppScreen(ctk.CTkFrame):
    def __init__(self, master, app: App):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        # ---- Sidebar ----
        sidebar = ctk.CTkFrame(self, fg_color=t.BG_SIDEBAR, width=100, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar, text="⚕", font=(t.FONT_FAMILY, 26)
        ).pack(pady=(20, 0))
        ctk.CTkLabel(
            sidebar, text="MediPredict", font=(t.FONT_FAMILY, 11, "bold"), text_color=t.TEXT_WHITE
        ).pack(pady=(0, 20))

        nav_items = [
            ("👤", "Patient", self.show_patient),
            ("📋", "Symptoms", self.show_symptoms),
            ("🧪", "Lab report", self.show_lab_report),
            ("🔬", "Predict", self.show_predict),
            ("🕑", "History", self.show_history),
            ("📊", "Dashboard", self.show_dashboard),
        ]
        for icon, label, cmd in nav_items:
            SidebarButton(sidebar, label, icon, cmd).pack(pady=4, padx=8)

        ctk.CTkButton(
            sidebar, text="⎋\nLogout", width=84, height=50, fg_color="transparent",
            hover_color=t.PINK, font=(t.FONT_FAMILY, 11), command=self.app.show_login,
        ).pack(side="bottom", pady=20)

        # ---- Content area ----
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True, padx=14, pady=14)

        self.show_patient()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_patient(self):
        self.clear_content()
        PatientScreen(self.content, self.app)

    def show_symptoms(self):
        self.clear_content()
        SymptomsScreen(self.content, self.app)

    def show_lab_report(self):
        self.clear_content()
        LabReportScreen(self.content, self.app)

    def show_predict(self):
        self.clear_content()
        PredictScreen(self.content, self.app)

    def show_history(self):
        self.clear_content()
        HistoryScreen(self.content, self.app)

    def show_dashboard(self):
        self.clear_content()
        DashboardScreen(self.content, self.app)


# =================================================================
# Shared: patient picker dropdown (used on Symptoms/Lab/Predict/History)
# =================================================================

class PatientPicker(ctk.CTkFrame):
    """Dropdown to select an already-registered patient. Calls on_change(patient_id)."""

    def __init__(self, master, app: App, on_change=None):
        super().__init__(master, fg_color=t.BG_CARD, corner_radius=10)
        self.app = app
        self.on_change = on_change
        self.patients = {}

        ctk.CTkLabel(self, text="Select patient", font=(t.FONT_FAMILY, 11), text_color=t.TEXT_MUTED).pack(
            anchor="w", padx=12, pady=(10, 2)
        )
        self.dropdown = ctk.CTkOptionMenu(
            self, values=["Loading..."], command=self._selected, width=300,
            fg_color=t.BG_CARD_ALT, button_color=t.PURPLE, button_hover_color=t.PURPLE_DARK,
        )
        self.dropdown.pack(anchor="w", padx=12, pady=(0, 12))
        self.reload()

    def reload(self):
        try:
            patients = db.get_all_patients()
        except ConnectionError as e:
            self.dropdown.configure(values=[str(e)])
            return
        self.patients = {f"{p['name']} (ID {p['patient_id']}, age {p['age']})": p["patient_id"] for p in patients}
        values = list(self.patients.keys()) or ["No patients yet - add one first"]
        self.dropdown.configure(values=values)
        self.dropdown.set(values[0])
        if self.patients:
            self._selected(values[0])

    def _selected(self, label):
        patient_id = self.patients.get(label)
        self.app.selected_patient_id = patient_id
        if self.on_change and patient_id:
            self.on_change(patient_id)


# =================================================================
# 1) Patient screen
# =================================================================

class PatientScreen(ctk.CTkFrame):
    def __init__(self, master, app: App):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Add new patient", font=(t.FONT_FAMILY, 16, "bold"), text_color=t.TEXT_WHITE).pack(
            anchor="w", pady=(0, 10)
        )

        form = ctk.CTkFrame(self, fg_color=t.BG_CARD, corner_radius=12)
        form.pack(fill="x", pady=(0, 14))

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(16, 6))
        self.name_entry = self._labeled_entry(row1, "Full name", "Anjali Patil", side="left")
        self.age_entry = self._labeled_entry(row1, "Age", "29", side="left")

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(row2, text="Gender", font=(t.FONT_FAMILY, 11), text_color=t.TEXT_MUTED).pack(anchor="w")
        self.gender_menu = ctk.CTkOptionMenu(row2, values=["Female", "Male", "Other"], width=260)
        self.gender_menu.pack(anchor="w", pady=(2, 8))

        row3 = ctk.CTkFrame(form, fg_color="transparent")
        row3.pack(fill="x", padx=16, pady=6)
        self.contact_entry = self._labeled_entry(row3, "Contact", "98XXXXXXXX", side="left")
        self.address_entry = self._labeled_entry(row3, "Address", "City, area", side="left")

        ctk.CTkButton(
            form, text="Save patient", fg_color=t.PURPLE, hover_color=t.PURPLE_DARK,
            command=self.save_patient,
        ).pack(anchor="w", padx=16, pady=16)

        ctk.CTkLabel(self, text="Recent patients", font=(t.FONT_FAMILY, 13, "bold"), text_color=t.TEXT_WHITE).pack(
            anchor="w", pady=(6, 6)
        )
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=220)
        self.list_frame.pack(fill="both", expand=True)
        self.refresh_list()

    def _labeled_entry(self, parent, label, placeholder, side="left"):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(side=side, padx=(0, 16))
        ctk.CTkLabel(wrap, text=label, font=(t.FONT_FAMILY, 11), text_color=t.TEXT_MUTED).pack(anchor="w")
        entry = ctk.CTkEntry(wrap, placeholder_text=placeholder, width=220)
        entry.pack(pady=(2, 0))
        return entry

    def save_patient(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        gender = self.gender_menu.get()
        contact = self.contact_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name or not age.isdigit():
            messagebox.showerror("Missing info", "Please enter at least a valid name and numeric age.")
            return
        try:
            new_id = db.add_patient(name, int(age), gender, contact, address)
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))
            return

        self.app.selected_patient_id = new_id
        messagebox.showinfo("Saved", f"Patient '{name}' saved with ID {new_id}.")
        self.name_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.contact_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.refresh_list()

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        try:
            patients = db.get_all_patients()
        except ConnectionError as e:
            ctk.CTkLabel(self.list_frame, text=str(e), text_color=t.PINK).pack(anchor="w")
            return
        for p in patients:
            row = ctk.CTkFrame(self.list_frame, fg_color=t.BG_CARD, corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(
                row, text=f"#{p['patient_id']}  {p['name']}  ·  {p['age']} yrs  ·  {p['gender']}",
                font=(t.FONT_FAMILY, 12), text_color=t.TEXT_WHITE,
            ).pack(side="left", padx=12, pady=8)


# =================================================================
# 2) Symptoms screen
# =================================================================

class SymptomsScreen(ctk.CTkFrame):
    def __init__(self, master, app: App):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)
        self.check_vars = {}

        ctk.CTkLabel(self, text="Add symptoms", font=(t.FONT_FAMILY, 16, "bold"), text_color=t.TEXT_WHITE).pack(
            anchor="w", pady=(0, 10)
        )
        PatientPicker(self, app).pack(fill="x", pady=(0, 12))

        card = ctk.CTkScrollableFrame(self, fg_color=t.BG_CARD, corner_radius=12, height=340)
        card.pack(fill="both", expand=True)

        try:
            symptoms = db.get_all_symptoms()
        except ConnectionError as e:
            ctk.CTkLabel(card, text=str(e), text_color=t.PINK).pack(anchor="w", padx=12, pady=12)
            symptoms = []

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=10)
        for i, s in enumerate(symptoms):
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(
                grid, text=s["symptom_name"], variable=var,
                fg_color=t.GREEN, hover_color=t.GREEN, font=(t.FONT_FAMILY, 12),
            )
            cb.grid(row=i // 3, column=i % 3, sticky="w", padx=10, pady=6)
            self.check_vars[s["symptom_id"]] = var

        ctk.CTkButton(
            self, text="Save symptoms", fg_color=t.GREEN, hover_color="#249c69",
            command=self.save_symptoms,
        ).pack(anchor="w", pady=12)

    def save_symptoms(self):
        patient_id = self.app.selected_patient_id
        if not patient_id:
            messagebox.showerror("No patient", "Add or select a patient first.")
            return
        selected_ids = [sid for sid, var in self.check_vars.items() if var.get()]
        if not selected_ids:
            messagebox.showwarning("No symptoms", "Select at least one symptom.")
            return
        try:
            db.save_patient_symptoms(patient_id, selected_ids)
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))
            return
        messagebox.showinfo("Saved", f"{len(selected_ids)} symptom(s) saved for patient #{patient_id}.")


# =================================================================
# 3) Lab report screen
# =================================================================

class LabReportScreen(ctk.CTkFrame):
    def __init__(self, master, app: App):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Add lab report", font=(t.FONT_FAMILY, 16, "bold"), text_color=t.TEXT_WHITE).pack(
            anchor="w", pady=(0, 10)
        )
        PatientPicker(self, app).pack(fill="x", pady=(0, 12))

        form = ctk.CTkFrame(self, fg_color=t.BG_CARD, corner_radius=12)
        form.pack(fill="x", pady=(0, 12))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=16)
        self.test_entry = self._labeled_entry(row, "Test name", "WBC count")
        self.value_entry = self._labeled_entry(row, "Value", "7500")
        self.unit_entry = self._labeled_entry(row, "Unit", "cells/mcL")

        ctk.CTkButton(
            form, text="Save report", fg_color=t.ORANGE, hover_color="#cc6d04",
            command=self.save_report,
        ).pack(anchor="w", padx=16, pady=(0, 16))

        ctk.CTkLabel(self, text="Reports for selected patient", font=(t.FONT_FAMILY, 13, "bold"),
                     text_color=t.TEXT_WHITE).pack(anchor="w", pady=(6, 6))
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=200)
        self.list_frame.pack(fill="both", expand=True)
        self.refresh_list()

    def _labeled_entry(self, parent, label, placeholder):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(wrap, text=label, font=(t.FONT_FAMILY, 11), text_color=t.TEXT_MUTED).pack(anchor="w")
        entry = ctk.CTkEntry(wrap, placeholder_text=placeholder, width=180)
        entry.pack(pady=(2, 0))
        return entry

    def save_report(self):
        patient_id = self.app.selected_patient_id
        if not patient_id:
            messagebox.showerror("No patient", "Add or select a patient first.")
            return
        test_name = self.test_entry.get().strip()
        value = self.value_entry.get().strip()
        unit = self.unit_entry.get().strip()
        if not test_name or not value:
            messagebox.showwarning("Missing info", "Enter at least a test name and value.")
            return
        try:
            db.add_lab_report(patient_id, test_name, value, unit)
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))
            return
        self.test_entry.delete(0, "end")
        self.value_entry.delete(0, "end")
        self.unit_entry.delete(0, "end")
        self.refresh_list()

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        patient_id = self.app.selected_patient_id
        if not patient_id:
            return
        try:
            reports = db.get_patient_lab_reports(patient_id)
        except ConnectionError as e:
            ctk.CTkLabel(self.list_frame, text=str(e), text_color=t.PINK).pack(anchor="w")
            return
        for r in reports:
            row = ctk.CTkFrame(self.list_frame, fg_color=t.BG_CARD, corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(
                row, text=f"{r['test_name']}: {r['value']} {r['unit'] or ''}  ({r['report_date']})",
                font=(t.FONT_FAMILY, 12), text_color=t.TEXT_WHITE,
            ).pack(side="left", padx=12, pady=8)


# =================================================================
# 4) Predict screen (core ML step)
# =================================================================

class PredictScreen(ctk.CTkFrame):
    def __init__(self, master, app: App):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Predict disease", font=(t.FONT_FAMILY, 16, "bold"), text_color=t.TEXT_WHITE).pack(
            anchor="w", pady=(0, 10)
        )
        PatientPicker(self, app).pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            self, text="🔬  Run prediction", height=42, fg_color=t.PINK, hover_color="#c22a5f",
            font=(t.FONT_FAMILY, 13, "bold"), command=self.run_prediction,
        ).pack(fill="x", pady=(0, 14))

        self.result_card = ctk.CTkFrame(self, fg_color=t.BG_CARD, corner_radius=12)
        self.result_card.pack(fill="both", expand=True)
        self.result_placeholder = ctk.CTkLabel(
            self.result_card, text="Run a prediction to see the result here.",
            font=(t.FONT_FAMILY, 12), text_color=t.TEXT_MUTED,
        )
        self.result_placeholder.pack(pady=40)

    def run_prediction(self):
        patient_id = self.app.selected_patient_id
        if not patient_id:
            messagebox.showerror("No patient", "Add or select a patient first.")
            return
        if self.app.model is None:
            messagebox.showerror(
                "Model not found",
                "model.pkl not found. Run 'python train_model.py' first, then restart the app.",
            )
            return

        try:
            recorded = db.get_patient_symptoms(patient_id)
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))
            return
        if not recorded:
            messagebox.showwarning("No symptoms", "This patient has no symptoms recorded yet.")
            return

        recorded_names = {r["symptom_name"].lower().replace(" ", "_") for r in recorded}
        feature_vector = np.array(
            [[1 if s in recorded_names else 0 for s in self.app.symptoms_list]]
        )

        probs = self.app.model.predict_proba(feature_vector)[0]
        best_idx = int(np.argmax(probs))
        disease_name = self.app.label_encoder.inverse_transform([best_idx])[0]
        confidence = round(float(probs[best_idx]) * 100, 2)

        self.display_result(patient_id, disease_name, confidence)

    def display_result(self, patient_id, disease_name, confidence):
        for w in self.result_card.winfo_children():
            w.destroy()

        try:
            disease = db.get_disease_by_name(disease_name)
        except ConnectionError as e:
            ctk.CTkLabel(self.result_card, text=str(e), text_color=t.PINK).pack(padx=16, pady=16)
            return

        if disease:
            try:
                db.save_prediction(patient_id, disease["disease_id"], confidence)
                medicines = db.get_medicines_for_disease(disease["disease_id"])
                hospitals = db.get_hospitals_for_specialization(disease["specialization"])
            except ConnectionError:
                medicines, hospitals = [], []
        else:
            medicines, hospitals = [], []

        ctk.CTkLabel(
            self.result_card, text="PREDICTED DISEASE", font=(t.FONT_FAMILY, 10), text_color=t.TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(16, 0))
        ctk.CTkLabel(
            self.result_card, text=f"{disease_name}  ·  {confidence}% confidence",
            font=(t.FONT_FAMILY, 20, "bold"), text_color=t.PURPLE,
        ).pack(anchor="w", padx=16, pady=(0, 14))

        tiles = ctk.CTkFrame(self.result_card, fg_color="transparent")
        tiles.pack(fill="x", padx=16, pady=(0, 16))

        med_box = ctk.CTkFrame(tiles, fg_color=t.BG_CARD_ALT, corner_radius=10)
        med_box.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ctk.CTkLabel(med_box, text="💊 Suggested medicine", font=(t.FONT_FAMILY, 12, "bold"),
                     text_color=t.BLUE).pack(anchor="w", padx=12, pady=(10, 4))
        if medicines:
            for m in medicines:
                ctk.CTkLabel(
                    med_box, text=f"• {m['medicine_name']} — {m['dosage_note']}",
                    font=(t.FONT_FAMILY, 11), text_color=t.TEXT_WHITE, wraplength=260, justify="left",
                ).pack(anchor="w", padx=12, pady=2)
        else:
            ctk.CTkLabel(med_box, text="No medicine data found.", font=(t.FONT_FAMILY, 11),
                         text_color=t.TEXT_MUTED).pack(anchor="w", padx=12, pady=2)
        ctk.CTkLabel(med_box, text="", font=(t.FONT_FAMILY, 4)).pack(pady=4)

        hosp_box = ctk.CTkFrame(tiles, fg_color=t.BG_CARD_ALT, corner_radius=10)
        hosp_box.pack(side="left", fill="both", expand=True, padx=(8, 0))
        ctk.CTkLabel(hosp_box, text="🏥 Suggested hospital", font=(t.FONT_FAMILY, 12, "bold"),
                     text_color=t.ORANGE).pack(anchor="w", padx=12, pady=(10, 4))
        if hospitals:
            for h in hospitals:
                ctk.CTkLabel(
                    hosp_box, text=f"• {h['name']} — {h['location']} ({h['contact']})",
                    font=(t.FONT_FAMILY, 11), text_color=t.TEXT_WHITE, wraplength=260, justify="left",
                ).pack(anchor="w", padx=12, pady=2)
        else:
            ctk.CTkLabel(hosp_box, text="No hospital data found.", font=(t.FONT_FAMILY, 11),
                         text_color=t.TEXT_MUTED).pack(anchor="w", padx=12, pady=2)
        ctk.CTkLabel(hosp_box, text="", font=(t.FONT_FAMILY, 4)).pack(pady=4)

        ctk.CTkLabel(
            self.result_card,
            text="⚠ For academic/demo purposes only - not a substitute for professional medical diagnosis.",
            font=(t.FONT_FAMILY, 10), text_color=t.TEXT_MUTED,
        ).pack(pady=(0, 12))


# =================================================================
# 5) History screen
# =================================================================

class HistoryScreen(ctk.CTkFrame):
    def __init__(self, master, app: App):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Patient history", font=(t.FONT_FAMILY, 16, "bold"), text_color=t.TEXT_WHITE).pack(
            anchor="w", pady=(0, 10)
        )
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", height=420)

        PatientPicker(self, app, on_change=self.load_history).pack(fill="x", pady=(0, 12))

        self.scroll.pack(fill="both", expand=True)
    def _section(self, title, color):
        ctk.CTkLabel(self.scroll, text=title, font=(t.FONT_FAMILY, 13, "bold"), text_color=color).pack(
            anchor="w", pady=(10, 4)
        )

    def load_history(self, patient_id):
        for w in self.scroll.winfo_children():
            w.destroy()
        try:
            symptoms = db.get_patient_symptoms(patient_id)
            reports = db.get_patient_lab_reports(patient_id)
            predictions = db.get_patient_predictions(patient_id)
        except ConnectionError as e:
            ctk.CTkLabel(self.scroll, text=str(e), text_color=t.PINK).pack(anchor="w")
            return

        self._section("📋 Symptoms reported", t.GREEN)
        if symptoms:
            for s in symptoms:
                ctk.CTkLabel(self.scroll, text=f"• {s['symptom_name']}  ({s['report_date']})",
                             font=(t.FONT_FAMILY, 12), text_color=t.TEXT_WHITE).pack(anchor="w", padx=8)
        else:
            ctk.CTkLabel(self.scroll, text="No symptoms recorded yet.", text_color=t.TEXT_MUTED).pack(anchor="w", padx=8)

        self._section("🧪 Lab reports", t.ORANGE)
        if reports:
            for r in reports:
                ctk.CTkLabel(self.scroll, text=f"• {r['test_name']}: {r['value']} {r['unit'] or ''}  ({r['report_date']})",
                             font=(t.FONT_FAMILY, 12), text_color=t.TEXT_WHITE).pack(anchor="w", padx=8)
        else:
            ctk.CTkLabel(self.scroll, text="No lab reports yet.", text_color=t.TEXT_MUTED).pack(anchor="w", padx=8)

        self._section("🔬 Past predictions", t.PURPLE)
        if predictions:
            for p in predictions:
                ctk.CTkLabel(
                    self.scroll,
                    text=f"• {p['disease_name']}  ·  {p['confidence']}%  ({p['predicted_on']})",
                    font=(t.FONT_FAMILY, 12), text_color=t.TEXT_WHITE,
                ).pack(anchor="w", padx=8)
        else:
            ctk.CTkLabel(self.scroll, text="No predictions made yet.", text_color=t.TEXT_MUTED).pack(anchor="w", padx=8)


# =================================================================
# 6) Dashboard screen
# =================================================================

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, app: App):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Dashboard", font=(t.FONT_FAMILY, 16, "bold"), text_color=t.TEXT_WHITE).pack(
            anchor="w", pady=(0, 10)
        )

        try:
            stats = db.get_dashboard_stats()
        except ConnectionError as e:
            ctk.CTkLabel(self, text=str(e), text_color=t.PINK).pack(anchor="w")
            return

        tiles = ctk.CTkFrame(self, fg_color="transparent")
        tiles.pack(fill="x", pady=(0, 16))
        StatTile(tiles, "Total patients", stats["total_patients"], t.PURPLE).pack(side="left", fill="x", expand=True, padx=(0, 6))
        StatTile(tiles, "Registered today", stats["today_patients"], t.GREEN).pack(side="left", fill="x", expand=True, padx=6)
        StatTile(tiles, "Total predictions", stats["total_predictions"], t.ORANGE).pack(side="left", fill="x", expand=True, padx=(6, 0))

        chart_card = ctk.CTkFrame(self, fg_color=t.BG_CARD, corner_radius=12)
        chart_card.pack(fill="both", expand=True)
        ctk.CTkLabel(chart_card, text="Most predicted diseases", font=(t.FONT_FAMILY, 13, "bold"),
                     text_color=t.TEXT_WHITE).pack(anchor="w", padx=16, pady=(14, 0))

        disease_counts = stats["disease_counts"]
        if not disease_counts:
            ctk.CTkLabel(chart_card, text="No predictions yet - run some from the Predict tab.",
                         text_color=t.TEXT_MUTED).pack(pady=40)
            return

        names = [d["disease_name"] for d in disease_counts]
        counts = [d["cnt"] for d in disease_counts]

        fig = Figure(figsize=(6, 3), dpi=100)
        fig.patch.set_facecolor(t.BG_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(t.BG_CARD)
        bars = ax.bar(names, counts, color=t.PURPLE)
        ax.tick_params(colors=t.TEXT_MUTED, labelsize=8, rotation=20)
        for spine in ax.spines.values():
            spine.set_color(t.BG_CARD_ALT)
        ax.set_ylabel("Predictions", color=t.TEXT_MUTED, fontsize=9)

        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)


if __name__ == "__main__":
    app = App()
    app.mainloop()

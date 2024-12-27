from mysql.connector import Error  
from tabulate import tabulate 

def execute_query(cursor, query, params=()):
    try:
        cursor.execute(query, params)
        return True
    except Error as e:
        print(f"Error executing query: {e}")
        return False

def add_patient_history(connection):
    try:
        cursor = connection.cursor()
        patient_id = input("Enter patient ID: ")
        treatment_date = input("Enter treatment date (YYYY-MM-DD): ")

        if len(treatment_date) != 10 or treatment_date[4] != '-' or treatment_date[7] != '-':
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
            return
        
        details = input("Enter treatment details: ")
        doctor_notes = input("Enter doctor notes (optional): ")

        query = """
        INSERT INTO patient_history (patient_id, treatment_date, details, doctor_notes)
        VALUES (%s, %s, %s, %s)
        """
        if execute_query(cursor, query, (patient_id, treatment_date, details, doctor_notes)):
            connection.commit()
            print("Patient history added successfully.")
    except Error as e:
        print(f"Error adding patient history: {e}")


def view_patient_history(connection):
    try:
        cursor = connection.cursor()
        patient_id = input("Enter patient ID to view history: ")
        query = "SELECT * FROM patient_history WHERE patient_id = %s"
        cursor.execute(query, (patient_id,))
        records = cursor.fetchall()

        if records:
            print("Patient History:")
            print(tabulate(records, headers=cursor.column_names, tablefmt="grid"))
        else:
            print("No history found for this patient.")
    except Error as e:
        print(f"Error viewing patient history: {e}")

def schedule_appointment(connection):
    try:
        patient_id = input("Enter patient ID: ")
        doctor_name = input("Enter doctor's name: ")
        appointment_date = input("Enter appointment date (YYYY-MM-DD): ")
        
        if len(appointment_date) != 10 or appointment_date[4] != '-' or appointment_date[7] != '-':
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
            return

        cursor = connection.cursor()
        query = """
            INSERT INTO appointments (patient_id, doctor_name, appointment_date)
            VALUES (%s, %s, %s)
        """
        if execute_query(cursor, query, (patient_id, doctor_name, appointment_date)):
            connection.commit()
            print("Appointment scheduled successfully.")
    except Error as e:
        print(f"Error scheduling appointment: {e}")

def update_appointment_status(connection):
    try:
        appointment_id = input("Enter appointment ID: ")
        new_status = input("Enter new status (Pending, Completed, Canceled): ")

        if new_status not in ['Pending', 'Completed', 'Canceled']:
            print("Invalid status. Please choose from 'Pending', 'Completed', or 'Canceled'.")
            return

        cursor = connection.cursor()
        query = "UPDATE appointments SET status = %s WHERE appointment_id = %s"
        if execute_query(cursor, query, (new_status, appointment_id)):
            connection.commit()
            print("Appointment status updated successfully.")
    except Error as e:
        print(f"Error updating appointment status: {e}")

def view_appointments(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM appointments ORDER BY appointment_date ASC"
        cursor.execute(query)
        records = cursor.fetchall()
        if records:
            print("Appointments:")
            print(tabulate(records, headers=cursor.column_names, tablefmt="grid"))
        else:
            print("No appointments found.")
    except Error as e:
        print(f"Error retrieving appointments: {e}")

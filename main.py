from tabulate import tabulate
from models import create_tables, drop_tables
import mysql.connector
from mysql.connector import Error
from utils import add_patient_history,view_patient_history,schedule_appointment, update_appointment_status, view_appointments
from db_config import get_database_connection, close_connection

def connect():
    try:
        print("Attempting to connect to the database...")
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='hospital_user',
            password='6305978196',
            database='hospital_db',
            connection_timeout=5
        )
        if connection.is_connected():
            print("Connection to MySQL database successful")
        else:
            print("Connection to MySQL database failed")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def new_patient(connection):
    try:
        name = input("Enter patient's name: ")
        age = int(input("Enter patient's age: "))
        symptoms = input("Enter patient's symptoms: ")
        diagnosis = input("Enter patient's diagnosis: ")
        admitted = input("Is the patient admitted? (yes/no): ").strip().lower() == 'yes'
        room_allotted = input("Enter room number if admitted (or leave blank): ") if admitted else None
        icu = input("Is the patient in ICU? (yes/no): ").strip().lower() == 'yes'

        cursor = connection.cursor()
        insert_query = """
            INSERT INTO patients (name, age, symptoms, diagnosis, admitted, room_allotted, icu)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (name, age, symptoms, diagnosis, admitted, room_allotted, icu))
        connection.commit()

        print("New patient record added successfully.")
    except Error as e:
        print(f"Error adding patient data: {e}")

def search_patient(connection):
    search_by = input("Do you want to search by (1) name, (2) age, (3) symptoms, (4) diagnosis, or (5) admission date?: ")
    try:
        cursor = connection.cursor()
        if search_by == '1':
            name = input("Enter the patient's name: ")
            cursor.execute("SELECT * FROM patients WHERE name LIKE %s", ('%' + name + '%',))
        elif search_by == '2':
            age = int(input("Enter the patient's age: "))
            cursor.execute("SELECT * FROM patients WHERE age = %s", (age,))
        elif search_by == '3':
            symptoms = input("Enter the patient's symptoms: ")
            cursor.execute("SELECT * FROM patients WHERE symptoms LIKE %s", ('%' + symptoms + '%',))
        elif search_by == '4':
            diagnosis = input("Enter the patient's diagnosis: ")
            cursor.execute("SELECT * FROM patients WHERE diagnosis LIKE %s", ('%' + diagnosis + '%',))
        elif search_by == '5':
            admission_date = input("Enter the admission date (YYYY-MM-DD): ")
            cursor.execute("SELECT * FROM patients WHERE admission_date = %s", (admission_date,))
        else:
            print("Invalid choice.")
            return

        records = cursor.fetchall()
        if records:
            print(tabulate(records, headers=[desc[0] for desc in cursor.description], tablefmt='grid'))
        else:
            print("No records found.")
    except Error as e:
        print(f"Error querying data: {e}")
    except ValueError:
        print("Invalid input. Please try again.")

def query_all_data(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM patients")
        records = cursor.fetchall()
        print(tabulate(records, headers=[desc[0] for desc in cursor.description], tablefmt='grid'))
    except Error as e:
        print(f"Error querying data: {e}")

def update_patient(connection):
    try:
        patient_id = int(input("Enter the patient's ID to update: "))
        name = input("Enter new name (leave blank to keep current): ")
        age = input("Enter new age (leave blank to keep current): ")
        symptoms = input("Enter new symptoms (leave blank to keep current): ")
        diagnosis = input("Enter new diagnosis (leave blank to keep current): ")

        cursor = connection.cursor()
        update_query = "UPDATE patients SET "
        updates = []
        params = []

        if name:
            updates.append("name = %s")
            params.append(name)
        if age:
            updates.append("age = %s")
            params.append(int(age))
        if symptoms:
            updates.append("symptoms = %s")
            params.append(symptoms)
        if diagnosis:
            updates.append("diagnosis = %s")
            params.append(diagnosis)

        if updates:
            update_query += ", ".join(updates) + " WHERE patient_id = %s"
            params.append(patient_id)
            cursor.execute(update_query, tuple(params))
            connection.commit()
            print("Patient record updated successfully.")
        else:
            print("No updates provided.")
    except Error as e:
        print(f"Error updating patient data: {e}")
    except ValueError:
        print("Invalid input. Please try again.")

def delete_patient(connection):
    try:
        patient_id = int(input("Enter the patient's ID to delete: "))
        cursor = connection.cursor()
        cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
        connection.commit()
        print("Patient record deleted successfully.")
    except Error as e:
        print(f"Error deleting patient data: {e}")
    except ValueError:
        print("Invalid input. Please try again.")

def generate_diagnosis_report(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT diagnosis, COUNT(*) AS count FROM patients GROUP BY diagnosis ORDER BY count DESC"
        cursor.execute(query)
        records = cursor.fetchall()
        print(tabulate(records, headers=["Diagnosis", "Count"], tablefmt="grid"))
    except Error as e:
        print(f"Error generating diagnosis report: {e}")

def calculate_patient_statistics(connection):
    try:
        cursor = connection.cursor()

        last_week_query = """
            SELECT * FROM patients
            WHERE admitted = TRUE AND admission_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """
        cursor.execute(last_week_query)
        last_week_records = cursor.fetchall()
        print("Patients admitted in the last week:")
        print(tabulate(last_week_records, headers=cursor.column_names, tablefmt="grid"))

        common_diagnosis_query = """
            SELECT diagnosis, COUNT(*) AS count
            FROM patients
            GROUP BY diagnosis
            ORDER BY count DESC
            LIMIT 5
        """
        cursor.execute(common_diagnosis_query)
        diagnosis_records = cursor.fetchall()
        print("Most common diagnoses:")
        print(tabulate(diagnosis_records, headers=["Diagnosis", "Count"], tablefmt="grid"))

        doctor_query = """
            SELECT doctor_name, COUNT(*) AS count
            FROM patients
            GROUP BY doctor_name
            ORDER BY count DESC
        """
        cursor.execute(doctor_query)
        doctor_records = cursor.fetchall()
        print("Doctor-wise patient count:")
        print(tabulate(doctor_records, headers=["Doctor Name", "Patient Count"], tablefmt="grid"))

    except Error as e:
        print(f"Error calculating statistics: {e}")

def search_with_multiple_criteria(connection):
    try:
        name = input("Enter patient's name (leave blank if not searching by name): ")
        age = input("Enter patient's age (leave blank if not searching by age): ")
        symptoms = input("Enter patient's symptoms (leave blank if not searching by symptoms): ")

        query = "SELECT * FROM patients WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE %s"
            params.append(f"%{name}%")
        if age:
            query += " AND age = %s"
            params.append(age)
        if symptoms:
            query += " AND symptoms LIKE %s"
            params.append(f"%{symptoms}%")

        cursor = connection.cursor()
        cursor.execute(query, params)
        records = cursor.fetchall()

        if records:
            print(tabulate(records, headers=cursor.column_names, tablefmt="grid"))
        else:
            print("No records found matching the criteria.")

    except Error as e:
        print(f"Error searching with multiple criteria: {e}")

def show_menu():
    print("""
    1. Add New Patient
    2. Search Patient
    3. View All Patients
    4. Update Patient Details
    5. Delete Patient
    6. Generate Diagnosis Report
    7. Calculate Patient Statistics
    8. Search with Multiple Criteria
    9. Add Patient History
    10. View Patient History
    11. Create Tables (Database Setup)
    12.Schedule Appointment
    13.Update Appointment Status      
    14.View Appointments    
    15.Drop Tables (Caution: Deletes All Data)
    16. Exit
    """)

def main():
    connection = get_database_connection()
    if not connection:
        print("Could not establish a connection to the database.")
        print("Exiting program.")
        return
    else:
        while True:
            show_menu()
            task = input("Enter your choice: ").strip()

            match task:
                case "1":
                    new_patient(connection)
                case "2":
                    search_patient(connection)
                case "3":
                    query_all_data(connection)
                case "4":
                    update_patient(connection)
                case "5":
                    delete_patient(connection)
                case "6":
                    generate_diagnosis_report(connection)
                case "7":
                    calculate_patient_statistics(connection)
                case "8":
                    search_with_multiple_criteria(connection)
                case "9":
                    add_patient_history(connection)
                case "10":
                    view_patient_history(connection)
                case "11":
                    create_tables(connection)
                case "12":
                    schedule_appointment(connection)
                case "13":
                    update_appointment_status(connection)
                case "14":
                    view_appointments(connection)
                case "15":
                    confirm = input("Are you sure you want to drop all tables? This action cannot be undone. (yes/no): ").strip().lower()
                    if confirm == "yes":
                        drop_tables(connection)
                        break
                case "16":
                    break
                case _:
                    print("Invalid option. Please try again.")


            repeat = input("Do you want to perform another operation? (yes/no): ").strip().lower()
            if repeat != "yes":
                break

        close_connection(connection)
        print("Connection closed.")

if __name__ == "__main__":
    main()
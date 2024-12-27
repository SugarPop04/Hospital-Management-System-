import mysql.connector
from mysql.connector import Error

def create_tables(connection):
    try:
        cursor = connection.cursor()

        table_queries = {
            "patients": """
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    age INT,
                    symptoms TEXT,
                    diagnosis TEXT,
                    admitted BOOLEAN,
                    room_allotted VARCHAR(50),
                    icu BOOLEAN,
                    admission_date DATE
                )
            """,
            "appointments": """
                CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id INT,
                    doctor_name VARCHAR(100),
                    appointment_date DATE,
                    status VARCHAR(20) DEFAULT 'Pending',
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                )
            """,
            "patient_history": """
                CREATE TABLE IF NOT EXISTS patient_history (
                    history_id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id INT,
                    treatment_date DATE,
                    details TEXT,
                    doctor_notes TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                )
            """
        }

        print("Which table would you like to create?")
        print("1. Patients")
        print("2. Appointments")
        print("3. Patient History")
        print("4. All tables")

        choice = input("Enter the number corresponding to the table you want to create: ")

        if choice == "1":
            tables_to_create = ["patients"]
        elif choice == "2":
            tables_to_create = ["appointments"]
        elif choice == "3":
            tables_to_create = ["patient_history"]
        elif choice == "4":
            tables_to_create = ["patients", "appointments", "patient_history"]
        else:
            print("Invalid choice. Please try again.")
            return

        for table in tables_to_create:
            cursor.execute(table_queries[table])
            print(f"{table.capitalize()} table created.")

        connection.commit()
        print("Table(s) created successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")

def drop_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;") #This disables foreign key checks, allowing the DROP TABLE commands to execute without considering foreign key constraints.

        cursor.execute("DROP TABLE IF EXISTS appointments")
        cursor.execute("DROP TABLE IF EXISTS patient_history")
        cursor.execute("DROP TABLE IF EXISTS patients")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;") #This re-enables foreign key checks after the tables have been dropped.

        print("All tables dropped successfully.")
    except Error as e:
        print(f"Error dropping tables: {e}")
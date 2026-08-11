import pandas as pd
import pyodbc


# Excel file read
data = pd.read_excel("student_data.xlsx")


# MS SQL connection
connection = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=LAPTOP-MO4U2FP0\\SQLEXPRESS;"
    "Database=student_dsbd12072206;"
    "Trusted_Connection=yes;"
)


cursor = connection.cursor()


# Insert data row by row

for index, row in data.iterrows():

    query = """
    INSERT INTO Students
    (Student_ID, Name, Subject, Mark, Attendance)
    VALUES (?, ?, ?, ?, ?)
    """

    cursor.execute(
        query,
        row["Student_ID"],
        row["Name"],
        row["Subject"],
        row["Mark"],
        row["Attendance"]
    )


# Save changes
connection.commit()


print("Data Inserted Successfully")


cursor.close()
connection.close()
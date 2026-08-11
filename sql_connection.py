import pyodbc

try:

    connection = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=LAPTOP-MO4U2FP0\\SQLEXPRESS;"
        "Database=student_dsbd12072206;"
        "Trusted_Connection=yes;"
    )

    print("MS SQL Connected Successfully")

    connection.close()


except Exception as e:

    print("Connection Failed")
    print(e)
    
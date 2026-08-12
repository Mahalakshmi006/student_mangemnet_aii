from ai_anlysiss import generate_feedback
# computer memory-la temporary file madhiri
from io import BytesIO
# aligned ah format panna required tools
from openpyxl.styles import Font, Alignment, Border, Side
import pandas as pd  
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
#HTML page open/display panna render,
#JSON response send panna jsonify,
# Success/Error popup message send panna flash

import pyodbc
#this are libreise to send & receive a files & to connect sql
#Jinja = Flask/Python data-va HTML-la display panna bridge.

# main flask to create
app = Flask(__name__)
app.secret_key = "student_dashboard_secret_key"
    
# SQL Server Connection & to start a cursor
connection = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=LAPTOP-MO4U2FP0\\SQLEXPRESS;"
        "Database=student_dsbd12072206;"
        "Trusted_Connection=yes;"
    )

cursor = connection.cursor()


#--------------------- Home page-----------------------

# to fetch a data into dropdown menu
@app.route("/")
def home():

    query = "SELECT * FROM Clean_Students"

    df = pd.read_sql(query, connection)

    students = df.to_dict(orient="records")
    

    return render_template(
        "index.html",
        students=students
    )
#----------------------------- Import page------------------------------------

@app.route("/import-page")
def import_page():
    return render_template("importdata.html")
#---------------------------------------------

@app.route("/home-page")
def home_page():
    return render_template("index.html")

#-------------------clean page-----------------------------

@app.route("/clean-page")
def clean_page():
    return render_template("clean.html")
    
#-------------------ai box ---------------------------------

@app.route("/ai-box")
def ai_box():

    query = "SELECT * FROM Clean_Students"

    df = pd.read_sql(query, connection)

    students = df.to_dict(orient="records")

    return render_template(
        "index.html",
        students=students
    ) 

#-------------------ai anlysys-----------------------------

@app.route("/generate-ai-feedback", methods=["POST"])
def ai_feedback():

    data = request.get_json()

    feedback = generate_feedback(
        data["name"],
        data["subject"],
        data["mark"],
        data["attendance"]
    )

    return jsonify({
        "feedback": feedback
    })

#----------------------------------import excl fle-----------------

@app.route("/analyze_student", methods=["POST"])
def analyze_student():

    try:
        data = request.get_json()
        student_id = data["student_id"]

        cursor = connection.cursor()

        cursor.execute("""
            SELECT Name, Subject, Mark, Attendance
            FROM Clean_Students
            WHERE Student_ID = ?
        """, student_id)

        student = cursor.fetchone()

        cursor.close()

        if student is None:
            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify({
            "name": student[0],
            "subject": student[1],
            "mark": student[2],
            "attendance": student[3]
        })

    except Exception as e:
        print("ANALYZE ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500
#-----------------------------------------------------------------

#import data exl file
@app.route("/import", methods=["POST"])
def import_data():
    try:
        file = request.files["file"]
        df = pd.read_excel(file) 
        
        # Create Student_ID if it is missing a id
        if "Student_ID" not in df.columns:
            df.insert(0, "Student_ID", range(1, len(df) + 1))
            
        #Python code table name  = SQL Server table name=SELECT query table name
        
        # Loop through every row
        
        for index, row in df.iterrows():
          mark = pd.to_numeric(row["Mark"], errors="coerce")
          attendance = pd.to_numeric(row["Attendance"], errors="coerce")
    

          if pd.isna(mark):    
                mark = 0

          if pd.isna(attendance):
              attendance = 0


          name = row["Name"]
          if pd.isna(name):
              name = "Unknown"


          subject = row["Subject"]
          if pd.isna(subject):
               subject = "Unknown"


          cursor.execute("""
            INSERT INTO Students
            (Student_ID, Name, Subject, Mark, Attendance)
            VALUES (?, ?, ?, ?, ?)
          """,
          int(row["Student_ID"]),
          name,
          subject,
          int(mark),
          int(attendance))
            

        connection.commit() # to close 

        flash("Excel Data Imported Successfully into SQL Server", "success")

        return redirect(url_for("import_page"))

    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("import_page"))
    
#-------------------------------clean data---------------------

@app.route("/clean-data", methods=["POST"])
def clean_data():
    
    try:
        query = "SELECT * FROM Students"
        df = pd.read_sql(query, connection)
    
        print(df)
        # -------------------------
        # DATA CLEANING
        # -------------------------

        # Remove leading & trailing spaces
        for col in df.select_dtypes(include="object"):
            df[col] = df[col].str.strip()
            
        # Remove extra spaces
        for col in df.select_dtypes(include="object"):
            df[col] = df[col].str.replace(r"\s+", " ", regex=True)

        # Proper case
        for col in df.select_dtypes(include="object"):
            df[col] = df[col].str.title()
        
        # Remove duplicates AFTER cleaning
        df.drop_duplicates(inplace=True)

        # Remove blank rows
        df.dropna(how="all", inplace=True)

        # Fill NULL values----------------------------------

    # Name empty -> Unknown
        df["Name"] = df["Name"].fillna("Unknown")

    # Subject empty -> Unknown
        df["Subject"] = df["Subject"].fillna("Unknown")

    # Mark empty -> 0
        df["Mark"] = pd.to_numeric(df["Mark"], errors="coerce")
        df["Mark"] = df["Mark"].fillna(0)

      # Attendance empty -> 0
        df["Attendance"] = pd.to_numeric(
            df["Attendance"],
            errors="coerce"
        )

        df["Attendance"] = df["Attendance"].fillna(0)

    # Create Student_ID if missing
        if "Student_ID" not in df.columns:
            df.insert(0, "Student_ID", range(1, len(df) + 1))
        else:
            df["Student_ID"] = pd.to_numeric(df["Student_ID"], errors="coerce")
            df["Student_ID"] = df["Student_ID"].fillna(0)

# Convert data types
        df["Student_ID"] = df["Student_ID"].astype(int)
        df["Mark"] = df["Mark"].astype(int)
        df["Attendance"] = df["Attendance"].astype(int)
    # Remove duplicate based on student details

        df.drop_duplicates(
            subset=[
                "Name",
                "Subject",
                "Mark",
                "Attendance"
            ],
            inplace=True
        )

        # Validate Marks
        df.loc[df["Mark"] < 0, "Mark"] = 0
        df.loc[df["Mark"] > 100, "Mark"] = 100

        # Validate Attendance
        
        df.loc[df["Attendance"] < 0, "Attendance"] = 0
        df.loc[df["Attendance"] > 100, "Attendance"] = 100

        
        for index, row in df.iterrows():
            cursor.execute("""
                    INSERT INTO Clean_Students
                    (Student_ID, Name, Subject, Mark, Attendance)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    int(row["Student_ID"]),
                    row["Name"],
                    row["Subject"],
                    int(row["Mark"]),
                    int(row["Attendance"]))
        connection.commit()
       
        flash("Data Cleaning Completed Successfully", "success")

        return redirect(url_for("clean_page"))
    
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("clean_page"))
    
#-------------------------------------------------------------------

@app.route("/export-report")
def export_report():

    query = "SELECT * FROM Clean_Students"
    df = pd.read_sql(query, connection)
    
# Excel file-ku temporary memory spac vraiable
# openpyxl to handle a excel file

    output = BytesIO()
    
    # output laexcl file create panu nu soluthu 
    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        # Cleaned Data
        # excl file hh create panuom 1 file  index 0 na 
        # no added extra numbering clomun
        df.to_excel(
            writer,
            sheet_name="Cleaned Data",
            index=False
        )

        # Summary to create 
        total_students = len(df)
        average_mark = df["Mark"].mean()
        pass_students = len(df[df["Mark"] >= 35])
        fail_students = len(df[df["Mark"] < 35])
        average_attendance = df["Attendance"].mean()

        summary = pd.DataFrame({
            "Metric": [
                "Total Students",
                "Average Mark",
                "Pass Students",
                "Fail Students",
                "Average Attendance"
            ],
            "Value": [
                total_students,
                round(average_mark, 2),
                pass_students,
                fail_students,
                round(average_attendance, 2)
            ]
        })
# Summary sheet to crearete2 file

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        # Top 5 Mark high to low sort panni 
        # first 5 students eduthu vaa.
        top5 = df.sort_values(
            by="Mark",
            ascending=False
        ).head(5)
        
        # 3 file to create 
        top5.to_excel(
            writer,
            sheet_name="Top 5 Students",
            index=False
        )

         # bottom 5 Mark high to low sort panni 
        # bottom 5 students eduthu vaa.
        bottom5 = df.sort_values(
            by="Mark",
            ascending=True
        ).head(5)

        # 4 file cteated
        bottom5.to_excel(
            writer,
            sheet_name="Bottom 5 Students",
            index=False
        )

        # --------------------------------
        # EXCEL FORMATTING
        # --------------------------------
        #Namma create pannina Excel workbook-ai 
        # eduthu workbook variable-la store pannu.
        workbook = writer.book
        
        # to craeta a border
        
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")
        )
        #Every sheet-ku formatting
        for worksheet in workbook.worksheets:

            # Header formatting
            # first sht in fisrts row
            #alla re set 
            for cell in worksheet[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center"
                )
                cell.border = thin_border

            # All cells alignment + border
            for row in worksheet.iter_rows():

                for cell in row:

                    cell.alignment = Alignment(
                        horizontal="center",
                        vertical="center"
                    )

                    cell.border = thin_border

            # Column width
            for column in worksheet.columns:

                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:

                    if cell.value is not None:
                        max_length = max(
                            max_length,
                            len(str(cell.value))
                        )

                worksheet.column_dimensions[
                    column_letter
                ].width = max_length + 3

            # Freeze first row
            worksheet.freeze_panes = "A2"
            
    #Temporary Excel file-ai beginning position-ku kondu vaa.
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,   #File-ah download pannu so true oru view na false     
        download_name="Student_Analysis_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" # to chk a xlx file or not
    )
#------------------------ dashboard -----------------------------
    
@app.route("/dashboard")
def dashboard():

    query = "SELECT * FROM Clean_Students"
    df = pd.read_sql(query, connection)

    total_students = len(df)
    average_mark = df["Mark"].mean()

    pass_students = len(df[df["Mark"] >= 35])
    fail_students = len(df[df["Mark"] < 35])


    average_attendance = df["Attendance"].mean()

    subject_data = df["Subject"].value_counts()

    subjects = subject_data.index.tolist()
    counts = subject_data.values.tolist()
    
    # Top 5 Students
    top5 = df.sort_values(by="Mark", ascending=False).head(5)

    top_names = top5["Name"].tolist()
    top_marks = top5["Mark"].tolist()


    #Bottom 5 Students
    bottom5 = df.sort_values(by="Mark", ascending=True).head(5)

    bottom_names = bottom5["Name"].tolist()
    bottom_marks = bottom5["Mark"].tolist()
    # Change 0 mark to 1 for chart display
    bottom_marks = [1 if mark == 0 else mark for mark in bottom_marks]
    
    # Performance Trend Line Chart
# Attendance Trend Line Chart

    df = df.sort_values("Student_ID")
    attendance_names = df["Name"].tolist()
    attendance_values = df["Attendance"].tolist()
      
      # attendence to validate --------------------------------
     
    attendance_range = {
    "90-100":0,
    "75-89":0,
    "50-74":0,
    "Below 50":0
}
    # SQL data fetch------------
    
    cursor.execute("SELECT Attendance FROM Clean_Students")
    attendance_db_values = [row[0] for row in cursor.fetchall()]
    
    for att in attendance_db_values:

        if att >= 90:
            attendance_range["90-100"] += 1

        elif att >= 75:
            attendance_range["75-89"] += 1

        elif att >= 50:
            attendance_range["50-74"] += 1

        else:
          attendance_range["Below 50"] += 1
    

    return render_template(
    "dashboard.html",

    total=total_students,
    avg=average_mark,
    passed=pass_students,
    failed=fail_students,
    attendance=average_attendance,
    

    subjects=subjects,
    counts=counts,

    top_names=top_names,
    top_marks=top_marks,

    bottom_names=bottom_names,
    bottom_marks=bottom_marks,
    
    attendance_names=attendance_names,
    attendance_values=attendance_values,
    
    attendance_labels=list(attendance_range.keys()),
    attendance_counts=list(attendance_range.values()),

)
    

 # this is a main owner not writable no code run 
if __name__ == "__main__":
    app.run(debug=True)
   
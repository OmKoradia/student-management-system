import os
import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector
import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# DATABASE SETTINGS
# ============================================================

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = "student_management"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection

    except mysql.connector.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not connect to MySQL.\n\n{error}"
        )
        return None


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    connection = connect_database()

    if connection is None:
        return pd.DataFrame()

    try:
        query = "SELECT * FROM students"

        df = pd.read_sql(query, connection)

        return df

    except Exception as error:
        messagebox.showerror(
            "Error",
            f"Could not load data.\n\n{error}"
        )
        return pd.DataFrame()

    finally:
        if connection.is_connected():
            connection.close()


# ============================================================
# CLEAR INPUT FIELDS
# ============================================================

def clear_fields():

    entry_roll.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_branch.delete(0, tk.END)
    entry_semester.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_mobile.delete(0, tk.END)

    entry_math.delete(0, tk.END)
    entry_python.delete(0, tk.END)
    entry_cn.delete(0, tk.END)
    entry_wad.delete(0, tk.END)

    entry_attendance.delete(0, tk.END)

    entry_roll.focus()


# ============================================================
# GET STUDENT DATA FROM FORM
# ============================================================

def get_student_data():

    try:
        roll_no = entry_roll.get().strip()
        name = entry_name.get().strip()
        branch = entry_branch.get().strip()
        semester = int(entry_semester.get())

        email = entry_email.get().strip()
        mobile = entry_mobile.get().strip()

        math_marks = float(entry_math.get())
        python_marks = float(entry_python.get())
        cn_marks = float(entry_cn.get())
        wad_marks = float(entry_wad.get())

        attendance = float(entry_attendance.get())

        # Check required fields

        if roll_no == "" or name == "" or branch == "":
            messagebox.showwarning(
                "Input Error",
                "Please enter Roll No, Name and Branch."
            )
            return None

        # Check marks

        marks = [
            math_marks,
            python_marks,
            cn_marks,
            wad_marks
        ]

        for mark in marks:
            if mark < 0 or mark > 100:
                messagebox.showwarning(
                    "Input Error",
                    "Marks must be between 0 and 100."
                )
                return None

        # Check attendance

        if attendance < 0 or attendance > 100:
            messagebox.showwarning(
                "Input Error",
                "Attendance must be between 0 and 100."
            )
            return None

        # NumPy average

        average_marks = float(np.mean(marks))

        return (
            roll_no,
            name,
            branch,
            semester,
            email,
            mobile,
            math_marks,
            python_marks,
            cn_marks,
            wad_marks,
            average_marks,
            attendance
        )

    except ValueError:

        messagebox.showwarning(
            "Input Error",
            "Please enter valid numbers in Semester, Marks and Attendance."
        )

        return None


# ============================================================
# ADD STUDENT
# ============================================================

def add_student():

    data = get_student_data()

    if data is None:
        return

    connection = connect_database()

    if connection is None:
        return

    try:

        query = """
        INSERT INTO students
        (
            roll_no,
            name,
            branch,
            semester,
            email,
            mobile,
            math_marks,
            python_marks,
            cn_marks,
            wad_marks,
            average_marks,
            attendance
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor = connection.cursor()

        cursor.execute(query, data)

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Student added successfully."
        )

        cursor.close()
        connection.close()

        clear_fields()
        view_students()

    except mysql.connector.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Could not add student.\n\n{error}"
        )

        connection.close()


# ============================================================
# VIEW STUDENTS
# ============================================================

def view_students():

    for item in tree.get_children():
        tree.delete(item)

    df = load_data()

    if df.empty:
        return

    for _, row in df.iterrows():

        tree.insert(
            "",
            tk.END,
            values=(
                row["student_id"],
                row["roll_no"],
                row["name"],
                row["branch"],
                row["semester"],
                row["email"],
                row["mobile"],
                row["math_marks"],
                row["python_marks"],
                row["cn_marks"],
                row["wad_marks"],
                round(row["average_marks"], 2),
                row["attendance"]
            )
        )


# ============================================================
# SELECT STUDENT
# ============================================================

def select_student(event):

    selected = tree.focus()

    if selected == "":
        return

    values = tree.item(selected, "values")

    if not values:
        return

    clear_fields()

    entry_roll.insert(0, values[1])
    entry_name.insert(0, values[2])
    entry_branch.insert(0, values[3])
    entry_semester.insert(0, values[4])

    entry_email.insert(0, values[5])
    entry_mobile.insert(0, values[6])

    entry_math.insert(0, values[7])
    entry_python.insert(0, values[8])
    entry_cn.insert(0, values[9])
    entry_wad.insert(0, values[10])

    entry_attendance.insert(0, values[12])


# ============================================================
# UPDATE STUDENT
# ============================================================

def update_student():

    selected = tree.focus()

    if selected == "":
        messagebox.showwarning(
            "Selection Error",
            "Please select a student from the table."
        )
        return

    values = tree.item(selected, "values")

    if not values:
        return

    student_id = values[0]

    data = get_student_data()

    if data is None:
        return

    connection = connect_database()

    if connection is None:
        return

    try:

        query = """
        UPDATE students
        SET
            roll_no = %s,
            name = %s,
            branch = %s,
            semester = %s,
            email = %s,
            mobile = %s,
            math_marks = %s,
            python_marks = %s,
            cn_marks = %s,
            wad_marks = %s,
            average_marks = %s,
            attendance = %s
        WHERE student_id = %s
        """

        cursor = connection.cursor()

        cursor.execute(
            query,
            data + (student_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Student updated successfully."
        )

        clear_fields()
        view_students()

    except mysql.connector.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Could not update student.\n\n{error}"
        )

        connection.close()


# ============================================================
# DELETE STUDENT
# ============================================================

def delete_student():

    selected = tree.focus()

    if selected == "":
        messagebox.showwarning(
            "Selection Error",
            "Please select a student from the table."
        )
        return

    values = tree.item(selected, "values")

    if not values:
        return

    student_id = values[0]

    confirm = messagebox.askyesno(
        "Delete Student",
        "Are you sure you want to delete this student?"
    )

    if not confirm:
        return

    connection = connect_database()

    if connection is None:
        return

    try:

        query = "DELETE FROM students WHERE student_id = %s"

        cursor = connection.cursor()

        cursor.execute(
            query,
            (student_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Student deleted successfully."
        )

        clear_fields()
        view_students()

    except mysql.connector.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Could not delete student.\n\n{error}"
        )

        connection.close()


# ============================================================
# SEARCH STUDENT
# ============================================================

def search_student():

    search_text = entry_search.get().strip()

    if search_text == "":
        view_students()
        return

    connection = connect_database()

    if connection is None:
        return

    try:

        query = """
        SELECT *
        FROM students
        WHERE roll_no LIKE %s
        OR name LIKE %s
        """

        search_value = "%" + search_text + "%"

        cursor = connection.cursor()

        cursor.execute(
            query,
            (search_value, search_value)
        )

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        for item in tree.get_children():
            tree.delete(item)

        for row in rows:

            tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                    row[10],
                    round(row[11], 2),
                    row[12]
                )
            )

    except mysql.connector.Error as error:

        messagebox.showerror(
            "Search Error",
            str(error)
        )


# ============================================================
# DATA ANALYSIS
# ============================================================

def data_analysis():

    df = load_data()

    if df.empty:

        messagebox.showwarning(
            "No Data",
            "No student data available."
        )

        return

    print("\n==============================")
    print("STUDENT DATA ANALYSIS")
    print("==============================")

    columns = [
        "math_marks",
        "python_marks",
        "cn_marks",
        "wad_marks",
        "average_marks",
        "attendance"
    ]

    # Pandas descriptive statistics

    print("\nDescriptive Statistics:")

    print(
        df[columns].describe()
    )

    # Mean

    print("\nMean:")

    print(
        df[columns].mean()
    )

    # Median

    print("\nMedian:")

    print(
        df[columns].median()
    )

    # Highest marks

    print("\nHighest Average Marks:")

    print(
        df["average_marks"].max()
    )

    # Lowest marks

    print("\nLowest Average Marks:")

    print(
        df["average_marks"].min()
    )

    # Average attendance

    print("\nAverage Attendance:")

    print(
        df["attendance"].mean()
    )

    # ========================================================
    # SCIPY
    # ========================================================

    print("\nSciPy Statistical Analysis:")

    # Standard deviation

    standard_deviation = stats.tstd(
        df["average_marks"]
    )

    print(
        "Standard Deviation of Average Marks:"
    )

    print(
        standard_deviation
    )

    # Mode

    mode_result = stats.mode(
        df["average_marks"],
        keepdims=True
    )

    print(
        "Mode of Average Marks:"
    )

    print(
        mode_result.mode[0]
    )

    messagebox.showinfo(
        "Analysis Complete",
        "Analysis completed successfully.\n\n"
        "Check the CMD window for the results."
    )


# ============================================================
# VISUALIZATION
# ============================================================

def show_visualization():

    df = load_data()

    if df.empty:

        messagebox.showwarning(
            "No Data",
            "No student data available."
        )

        return

    # ========================================================
    # GRAPH 1 - STUDENT AVERAGE MARKS
    # ========================================================

    plt.figure(figsize=(12, 6))

    plt.bar(
        df["roll_no"],
        df["average_marks"]
    )

    plt.xlabel("Roll Number")
    plt.ylabel("Average Marks")
    plt.title("Average Marks of Students")

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    plt.show()

    # ========================================================
    # GRAPH 2 - SUBJECT AVERAGE
    # ========================================================

    subject_names = [
        "Mathematics",
        "Python",
        "Computer Networks",
        "WAD"
    ]

    subject_averages = [
        df["math_marks"].mean(),
        df["python_marks"].mean(),
        df["cn_marks"].mean(),
        df["wad_marks"].mean()
    ]

    plt.figure(figsize=(8, 6))

    sns.barplot(
        x=subject_names,
        y=subject_averages
    )

    plt.xlabel("Subjects")
    plt.ylabel("Average Marks")
    plt.title("Average Marks by Subject")

    plt.xticks(
        rotation=20
    )

    plt.tight_layout()

    plt.show()

    # ========================================================
    # GRAPH 3 - ATTENDANCE VS MARKS
    # ========================================================

    plt.figure(figsize=(8, 6))

    sns.scatterplot(
        data=df,
        x="attendance",
        y="average_marks",
        s=100
    )

    plt.xlabel("Attendance (%)")
    plt.ylabel("Average Marks")
    plt.title("Attendance vs Average Marks")

    plt.tight_layout()

    plt.show()


# ============================================================
# MACHINE LEARNING
# ============================================================

def machine_learning():

    df = load_data()

    if df.empty:

        messagebox.showwarning(
            "No Data",
            "No student data available."
        )

        return

    print("\n==============================")
    print("MACHINE LEARNING")
    print("==============================")

    # --------------------------------------------------------
    # Create Pass / Fail result
    # --------------------------------------------------------

    df["result"] = np.where(
        (df["average_marks"] >= 40) &
        (df["attendance"] >= 75),
        1,
        0
    )

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    X = df[
        [
            "math_marks",
            "python_marks",
            "cn_marks",
            "wad_marks",
            "attendance"
        ]
    ]

    # Target

    y = df["result"]

    # --------------------------------------------------------
    # Train/Test Split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y
    )

    # --------------------------------------------------------
    # Decision Tree
    # --------------------------------------------------------

    model = DecisionTreeClassifier(
        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    print(
        "\nNumber of Records:",
        len(df)
    )

    print(
        "\nAccuracy:",
        accuracy
    )

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            y_pred
        )
    )

    messagebox.showinfo(
        "Machine Learning",
        f"Decision Tree Model Completed.\n\n"
        f"Accuracy: {accuracy:.2f}\n\n"
        f"Check the CMD window for the classification report."
    )


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "Student Management & Performance Analysis System"
)

root.geometry(
    "1400x800"
)

root.configure(
    bg="#f2f2f2"
)


# ============================================================
# TITLE
# ============================================================

title_label = tk.Label(
    root,
    text="Student Management & Performance Analysis System",
    font=("Arial", 20, "bold"),
    bg="#f2f2f2"
)

title_label.pack(
    pady=10
)


# ============================================================
# INPUT FRAME
# ============================================================

input_frame = tk.Frame(
    root,
    bg="#f2f2f2"
)

input_frame.pack(
    padx=10,
    pady=5
)


# ============================================================
# ROW 1
# ============================================================

tk.Label(
    input_frame,
    text="Roll No",
    bg="#f2f2f2"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)

entry_roll = tk.Entry(
    input_frame,
    width=18
)

entry_roll.grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    input_frame,
    text="Name",
    bg="#f2f2f2"
).grid(
    row=0,
    column=2,
    padx=5,
    pady=5
)

entry_name = tk.Entry(
    input_frame,
    width=18
)

entry_name.grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)


tk.Label(
    input_frame,
    text="Branch",
    bg="#f2f2f2"
).grid(
    row=0,
    column=4,
    padx=5,
    pady=5
)

entry_branch = tk.Entry(
    input_frame,
    width=18
)

entry_branch.grid(
    row=0,
    column=5,
    padx=5,
    pady=5
)


tk.Label(
    input_frame,
    text="Semester",
    bg="#f2f2f2"
).grid(
    row=0,
    column=6,
    padx=5,
    pady=5
)

entry_semester = tk.Entry(
    input_frame,
    width=10
)

entry_semester.grid(
    row=0,
    column=7,
    padx=5,
    pady=5
)


# ============================================================
# ROW 2
# ============================================================

tk.Label(
    input_frame,
    text="Email",
    bg="#f2f2f2"
).grid(
    row=1,
    column=0,
    padx=5,
    pady=5
)

entry_email = tk.Entry(
    input_frame,
    width=18
)

entry_email.grid(
    row=1,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    input_frame,
    text="Mobile",
    bg="#f2f2f2"
).grid(
    row=1,
    column=2,
    padx=5,
    pady=5
)

entry_mobile = tk.Entry(
    input_frame,
    width=18
)

entry_mobile.grid(
    row=1,
    column=3,
    padx=5,
    pady=5
)


tk.Label(
    input_frame,
    text="Math Marks",
    bg="#f2f2f2"
).grid(
    row=1,
    column=4,
    padx=5,
    pady=5
)

entry_math = tk.Entry(
    input_frame,
    width=18
)

entry_math.grid(
    row=1,
    column=5,
    padx=5,
    pady=5
)


tk.Label(
    input_frame,
    text="Python Marks",
    bg="#f2f2f2"
).grid(
    row=1,
    column=6,
    padx=5,
    pady=5
)

entry_python = tk.Entry(
    input_frame,
    width=10
)

entry_python.grid(
    row=1,
    column=7,
    padx=5,
    pady=5
)


# ============================================================
# ROW 3
# ============================================================

tk.Label(
    input_frame,
    text="CN Marks",
    bg="#f2f2f2"
).grid(
    row=2,
    column=0,
    padx=5,
    pady=5
)

entry_cn = tk.Entry(
    input_frame,
    width=18
)

entry_cn.grid(
    row=2,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    input_frame,
    text="WAD Marks",
    bg="#f2f2f2"
).grid(
    row=2,
    column=2,
    padx=5,
    pady=5
)

entry_wad = tk.Entry(
    input_frame,
    width=18
)

entry_wad.grid(
    row=2,
    column=3,
    padx=5,
    pady=5
)


tk.Label(
    input_frame,
    text="Attendance %",
    bg="#f2f2f2"
).grid(
    row=2,
    column=4,
    padx=5,
    pady=5
)

entry_attendance = tk.Entry(
    input_frame,
    width=18
)

entry_attendance.grid(
    row=2,
    column=5,
    padx=5,
    pady=5
)


# ============================================================
# BUTTON FRAME
# ============================================================

button_frame = tk.Frame(
    root,
    bg="#f2f2f2"
)

button_frame.pack(
    pady=10
)


tk.Button(
    button_frame,
    text="Add Student",
    width=15,
    command=add_student
).grid(
    row=0,
    column=0,
    padx=5
)


tk.Button(
    button_frame,
    text="Update Student",
    width=15,
    command=update_student
).grid(
    row=0,
    column=1,
    padx=5
)


tk.Button(
    button_frame,
    text="Delete Student",
    width=15,
    command=delete_student
).grid(
    row=0,
    column=2,
    padx=5
)


tk.Button(
    button_frame,
    text="Clear",
    width=15,
    command=clear_fields
).grid(
    row=0,
    column=3,
    padx=5
)


tk.Button(
    button_frame,
    text="View Students",
    width=15,
    command=view_students
).grid(
    row=0,
    column=4,
    padx=5
)


tk.Button(
    button_frame,
    text="Data Analysis",
    width=15,
    command=data_analysis
).grid(
    row=0,
    column=5,
    padx=5
)


tk.Button(
    button_frame,
    text="Visualization",
    width=15,
    command=show_visualization
).grid(
    row=0,
    column=6,
    padx=5
)


tk.Button(
    button_frame,
    text="ML Prediction",
    width=15,
    command=machine_learning
).grid(
    row=0,
    column=7,
    padx=5
)


# ============================================================
# SEARCH FRAME
# ============================================================

search_frame = tk.Frame(
    root,
    bg="#f2f2f2"
)

search_frame.pack(
    pady=5
)


tk.Label(
    search_frame,
    text="Search Roll No / Name:",
    bg="#f2f2f2",
    font=("Arial", 10, "bold")
).pack(
    side=tk.LEFT,
    padx=5
)


entry_search = tk.Entry(
    search_frame,
    width=30
)

entry_search.pack(
    side=tk.LEFT,
    padx=5
)


tk.Button(
    search_frame,
    text="Search",
    width=12,
    command=search_student
).pack(
    side=tk.LEFT,
    padx=5
)


tk.Button(
    search_frame,
    text="Show All",
    width=12,
    command=view_students
).pack(
    side=tk.LEFT,
    padx=5
)


# ============================================================
# TABLE FRAME
# ============================================================

table_frame = tk.Frame(
    root
)

table_frame.pack(
    fill=tk.BOTH,
    expand=True,
    padx=10,
    pady=10
)


# ============================================================
# SCROLLBARS
# ============================================================

vertical_scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.VERTICAL
)

horizontal_scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.HORIZONTAL
)


# ============================================================
# TREEVIEW
# ============================================================

columns = (
    "ID",
    "Roll No",
    "Name",
    "Branch",
    "Semester",
    "Email",
    "Mobile",
    "Math",
    "Python",
    "CN",
    "WAD",
    "Average",
    "Attendance"
)


tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set
)


vertical_scrollbar.config(
    command=tree.yview
)

horizontal_scrollbar.config(
    command=tree.xview
)


# ============================================================
# TABLE HEADINGS
# ============================================================

for column in columns:

    tree.heading(
        column,
        text=column
    )

    tree.column(
        column,
        width=110,
        anchor=tk.CENTER
    )


tree.column(
    "ID",
    width=50
)

tree.column(
    "Name",
    width=150
)

tree.column(
    "Email",
    width=180
)

tree.column(
    "Mobile",
    width=120
)


# ============================================================
# PACK TABLE
# ============================================================

tree.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)

vertical_scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)

horizontal_scrollbar.pack(
    side=tk.BOTTOM,
    fill=tk.X
)


# ============================================================
# SELECT EVENT
# ============================================================

tree.bind(
    "<ButtonRelease-1>",
    select_student
)


# ============================================================
# LOAD STUDENTS
# ============================================================

view_students()


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()
CREATE DATABASE IF NOT EXISTS student_management;

USE student_management;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    semester INT NOT NULL,
    email VARCHAR(100),
    mobile VARCHAR(15),
    math_marks FLOAT,
    python_marks FLOAT,
    cn_marks FLOAT,
    wad_marks FLOAT,
    average_marks FLOAT,
    attendance FLOAT
);
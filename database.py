import sqlite3
from config import DB_PATH
from datetime import datetime, timedelta

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, role TEXT, first_name TEXT, last_name TEXT, grade INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS homework
                 (homework_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id INTEGER,
                  assignment_details TEXT,
                  due_date TEXT,
                  submission_details TEXT,
                  submission_type TEXT,
                  check_results TEXT,
                  status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  homework_id INTEGER,
                  student_id INTEGER,
                  question_text TEXT,
                  timestamp TEXT,
                  answer_text TEXT,
                  answer_timestamp TEXT,
                  FOREIGN KEY (homework_id) REFERENCES homework (homework_id),
                  FOREIGN KEY (student_id) REFERENCES users (user_id))''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def set_user(user_id, role, first_name=None, last_name=None, grade=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, role, first_name, last_name, grade) VALUES (?, ?, ?, ?, ?)",
              (user_id, role, first_name, last_name, grade))
    conn.commit()
    conn.close()

def is_tutor_set():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role='tutor'")
    tutor = c.fetchone()
    conn.close()
    return tutor is not None

def get_tutor():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role='tutor'")
    tutor = c.fetchone()
    conn.close()
    return tutor

def get_all_students():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, last_name, grade FROM users WHERE role='student'")
    students = c.fetchall()
    conn.close()
    return students

def delete_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id=? AND role='student'", (student_id,))
    conn.commit()
    conn.close()

def create_homework(student_id, details, due_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO homework (student_id, assignment_details, due_date, status) VALUES (?, ?, ?, 'assigned')",
              (student_id, details, due_date))
    conn.commit()
    homework_id = c.lastrowid
    conn.close()
    return homework_id

def get_homeworks_for_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM homework WHERE student_id=?", (student_id,))
    homeworks = c.fetchall()
    conn.close()
    return homeworks

def get_homework(homework_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM homework WHERE homework_id=?", (homework_id,))
    homework = c.fetchone()
    conn.close()
    return homework

def update_homework_submission(homework_id, submission_details, submission_type):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE homework SET submission_details=?, submission_type=?, status='submitted' WHERE homework_id=?",
              (submission_details, submission_type, homework_id))
    conn.commit()
    conn.close()

def update_homework_check(homework_id, check_results):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE homework SET check_results=?, status='checked' WHERE homework_id=?",
              (check_results, homework_id))
    conn.commit()
    conn.close()

def get_submitted_homeworks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT homework_id, student_id, assignment_details FROM homework WHERE status='submitted'")
    submissions = c.fetchall()
    conn.close()
    return submissions

def get_checked_homeworks_for_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT homework_id, check_results FROM homework WHERE student_id=? AND status='checked'",
              (student_id,))
    checked = c.fetchall()
    conn.close()
    return checked

def get_upcoming_homeworks():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT homework_id, student_id, due_date FROM homework WHERE status='assigned' AND due_date <= ?",
              (tomorrow,))
    upcoming = c.fetchall()
    conn.close()
    return upcoming

def add_question(homework_id, student_id, question_text):
    conn = get_connection()
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO questions (homework_id, student_id, question_text, timestamp) VALUES (?, ?, ?, ?)",
              (homework_id, student_id, question_text, timestamp))
    conn.commit()
    conn.close()

def get_questions_for_homework(homework_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE homework_id=?", (homework_id,))
    questions = c.fetchall()
    conn.close()
    return questions

def get_unanswered_questions():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE answer_text IS NULL")
    questions = c.fetchall()
    conn.close()
    return questions

def answer_question(question_id, answer_text):
    conn = get_connection()
    c = conn.cursor()
    answer_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE questions SET answer_text=?, answer_timestamp=? WHERE question_id=?",
              (answer_text, answer_timestamp, question_id))
    conn.commit()
    conn.close()
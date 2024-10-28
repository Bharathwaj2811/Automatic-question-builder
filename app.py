from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from objective import ObjectiveTest
from subjective import SubjectiveTest
import json 
import pdfkit
import random
from db import create_connection
from flask import Flask, jsonify,make_response
from datetime import datetime
import ast
from flask_mail import Mail, Message
import MySQLdb 
import time
from urllib.parse import quote as url_quote
import psutil
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import mysql.connector
from send_email import send_email  # Ensure this line is included
import os
from fpdf import FPDF  
import sys
from dotenv import load_dotenv
from datetime import date
from flask_sqlalchemy import SQLAlchemy

# Load environment variables from .env file
app = Flask(__name__)
app.secret_key = 'aica2'  # Ensure this is secure in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:6789@localhost/bhargavr_banking'
db = SQLAlchemy(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    task_status = db.Column(db.String(20), default='Incomplete')  # Add task status column
    completion_date = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Employee {self.name}>'
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_number = request.form['phone_number']
        role = request.form['role']

        connection = create_connection()
        cursor = connection.cursor()

        try:
            # Insert user into the appropriate table based on their role
            if role == 'trainer':
                cursor.execute(
                    "INSERT INTO trainer (username, password, email, phone_number) VALUES (%s, %s, %s, %s)",
                    (username, password, email, phone_number)
                )
            elif role == 'employee':
                cursor.execute(
                    "INSERT INTO employee (username, password, email, phone_number) VALUES (%s, %s, %s, %s)",
                    (username, password, email, phone_number)
                )
            elif role == 'admin':
                cursor.execute(
                    "INSERT INTO admin (username, password) VALUES (%s, %s)",
                    (username, password)
                )

            connection.commit()
            flash('User successfully added!', 'success')

            # Use the send_email function to send the email with login credentials
            send_email(email, username, password)
            flash('Account details sent to user’s email.', 'success')

        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('create_user'))

    return render_template('createuser.html')
@app.route('/system_performance')
def system_performance():
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Get memory usage
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    # Get disk usage
    disk_info = psutil.disk_usage('/')
    disk_usage = disk_info.percent

    return render_template('system_performance.html', 
                           cpu_usage=cpu_usage, 
                           memory_usage=memory_usage, 
                           disk_usage=disk_usage)


# Example Model (Update with your actual models)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)

@app.route('/')
def index():
    return render_template('login.html')  # Render the login page

@app.route('/upload_curriculum', methods=['GET', 'POST'])
def upload_curriculum():
    if request.method == 'POST':
        # File upload handling logic here
        # ...
        return redirect(url_for('success'))
    
    return render_template('upload_curriculum.html')

@app.route('/curriculum')
def curriculum():
    return render_template('training.html')  # Render the training.html template


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        # Create a connection to the database
        connection = create_connection()
        cursor = connection.cursor()

        # Check the credentials against the correct table based on the role
        table_mapping = {
            "admin": "admin",
            "trainer": "trainer",
            "employee": "employee"
        }

        if role in table_mapping:
            cursor.execute(f"SELECT * FROM {table_mapping[role]} WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            session[role] = username  # Store username in session based on role
            if role == 'admin':
                return redirect(url_for('administration'))  # Redirect to the admin dashboard
            elif role == 'trainer':
                return redirect(url_for('trainer_dashboard'))  # Redirect to the trainer dashboard
            elif role == 'employee':
                return redirect(url_for('employee_dashboard'))  # Redirect to the employee dashboard
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/administration')
def administration():
    if 'admin' not in session:
        return redirect(url_for('login'))  # Ensure admin is logged in

    # Create a connection to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Count total users in both tables
    cursor.execute("SELECT COUNT(*) FROM employee")
    total_employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trainer")
    total_trainers = cursor.fetchone()[0]

    total_users = total_employees + total_trainers

    # Assuming static CPU usage for demonstration
    cpu_usage = "55%"  # Replace this with dynamic fetching if needed

    cursor.close()
    connection.close()

    return render_template('administration.html', total_users=total_users, cpu_usage=cpu_usage)  # Pass total_users and cpu_usage to template

@app.route('/employee_dashboard')
def employee_dashboard():
    if 'employee' not in session:
        return redirect(url_for('login'))  # Ensure employee is logged in
    return render_template('employee.html')  # Render the employee dashboard


# @app.route('/create_user', methods=['GET', 'POST'])
# def create_user():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']
#         phone_number = request.form['phone_number']
#         role = request.form['role']

#         # Insert user into specific table based on role
#         connection = create_connection()
#         cursor = connection.cursor()

#         try:
#             if role == 'trainer':
#                 cursor.execute(
#                     "INSERT INTO trainer (username, password, email, phone_number) VALUES (%s, %s, %s, %s)",
#                     (username, password, email, phone_number)
#                 )
#             elif role == 'employee':
#                 cursor.execute(
#                     "INSERT INTO employee (username, password, email, phone_number) VALUES (%s, %s, %s, %s)",
#                     (username, password, email, phone_number)
#                 )
#             elif role == 'admin':
#                 cursor.execute(
#                     "INSERT INTO admin (username, password) VALUES (%s, %s)",
#                     (username, password)
#                 )

#             connection.commit()
#             flash('User successfully added!', 'success')

#             # Send email with username and password
#             msg = Message(
#                 'Hexaware Account Created Successfully',
#                 sender='sattibhargavreddy1@gmail.com',
#                 recipients=[email]
#             )
#             msg.body = f"""Dear {role.capitalize()},

# Congratulations and welcome to Hexaware! We are excited to have you onboard.

# Your account has been successfully created. Please find your login credentials below:

# - *Username*: {username}
# - *Password*: {password}

# To get started, please log in using the credentials provided above. For your security, we recommend changing your password upon first login.

# Best regards,  
# Hexaware Team
# """
#             mail.send(msg)
#             flash('Account details sent to user’s email.', 'success')

#         except Exception as e:
#             flash(f"Error: {e}", 'danger')
#         finally:
#             cursor.close()
#             connection.close()

#         return redirect(url_for('create_user'))

#     return render_template('createuser.html')

@app.route('/trainer_dashboard')
def trainer_dashboard():
    if 'trainer' not in session:
        return redirect(url_for('login'))  # Ensure trainer is logged in
    return render_template('trainer.html')  # Render the trainer dashboard

@app.route('/manage_users', methods=['GET'])
def manage_users():
    # Connect to the database and fetch all users (employees and trainers)
    connection = create_connection()
    cursor = connection.cursor()

    # Fetch employees
    cursor.execute("SELECT id, username, phone_number, email FROM employee")  
    employees = cursor.fetchall()

    # Fetch trainers
    cursor.execute("SELECT id, username, phone_number, email FROM trainer")  
    trainers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('manage_users.html', employees=employees, trainers=trainers)
@app.route('/download_question_bank')
def download_question_bank():
    # Create a connection to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Fetch all questions and correct answers from the question_banke table
    cursor.execute("SELECT question_text, correct_answer FROM question_banke")
    question_bank = cursor.fetchall()

    cursor.close()
    connection.close()

    # Render the data in a new template
    return render_template('download_question_bank.html', question_bank=question_bank)

@app.route('/download_question_banks')
def download_question_banks():
    # Create a connection to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Fetch all questions and correct answers from the question_banke table
    cursor.execute("SELECT question_text, correct_answer FROM question_banke")
    question_bank = cursor.fetchall()

    cursor.close()
    connection.close()

    # Render the data in a new template
    return render_template('questiondownload.html', question_bank=question_bank)

@app.route('/submit_subjective_question', methods=['POST'])
def submit_subjective_question():
    question = request.form['question']
    answer = request.form['answer']

    # Insert the question into the subjective_question_bank table
    connection = create_connection()
    cursor = connection.cursor()
    query = "INSERT INTO subjective_question_bank (question, answer) VALUES (%s, %s)"
    cursor.execute(query, (question, answer))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('trainer_dashboard'))  # Redirect to the dashboard after submission

@app.route('/submit_objective_question', methods=['POST'])
def submit_objective_question():
    question = request.form['question']
    option_a = request.form['option_a']
    option_b = request.form['option_b']
    option_c = request.form['option_c']
    option_d = request.form['option_d']
    correct_option = request.form['correct_option']

    # Insert the question into the objective_question_bank table
    connection = create_connection()
    cursor = connection.cursor()
    query = """
        INSERT INTO objective_question_bank (question, option_a, option_b, option_c, option_d, correct_option)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (question, option_a, option_b, option_c, option_d, correct_option))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('trainer_dashboard'))  # Redirect to the dashboard after submission

def fetch_questions_from_db():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT question, option_a, option_b, option_c, option_d, correct_answer FROM question_bank")
    questions = cursor.fetchall()
    connection.close()
    return questions

@app.route('/upload_subjective_form')
def upload_subjective_form():
    return render_template('upload_subjective_question.html')

@app.route('/upload_objective_form')
def upload_objective_form():
    return render_template('upload_objective_question.html')


@app.route('/edit_user/<int:user_id>/<role>', methods=['GET', 'POST'])
def edit_user(user_id, role):
    connection = create_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        # Get updated user details from the form
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']

        # Update user in the appropriate table based on the role
        if role == 'trainer':
            cursor.execute("UPDATE trainer SET username=%s, email=%s, phone_number=%s WHERE id=%s", (username, email, phone_number, user_id))
        elif role == 'employee':
            cursor.execute("UPDATE employee SET username=%s, email=%s, phone_number=%s WHERE id=%s", (username, email, phone_number, user_id))

        connection.commit()
        cursor.close()
        connection.close()
        
        flash('User successfully updated!', 'success')
        return redirect(url_for('manage_users'))

    # Fetch the current user details
    if role == 'trainer':
        cursor.execute("SELECT * FROM trainer WHERE id=%s", (user_id,))
    elif role == 'employee':
        cursor.execute("SELECT * FROM employee WHERE id=%s", (user_id,))

    user = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_user.html', user=user, role=role)  # Render edit user template

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Logic to delete user from the database
    connection = create_connection()
    cursor = connection.cursor()

    role = request.form.get('role')  # Get the role from the form (employee or trainer)

    if role == 'employee':
        cursor.execute("DELETE FROM employee WHERE id = %s", (user_id,))
    elif role == 'trainer':
        cursor.execute("DELETE FROM trainer WHERE id = %s", (user_id,))
    
    connection.commit()  # Commit the changes to the database
    cursor.close()
    connection.close()

    flash('User successfully deleted!', 'danger')
    return redirect(url_for('manage_users'))

@app.route('/test_generate_form')
def test_generate_form():
    if 'trainer' not in session:
        return redirect(url_for('login'))  # Ensure admin is logged in
    return render_template('auto_question.html')  # Assuming your test generation form is in index.html

@app.route('/test_generate1', methods=["POST"])
def test_generate1():
    
    if request.method == "POST":
        inputText = request.form["itext"]
        testType = request.form["test_type"]
        noOfQues = request.form["noq"]

        # Generate objective test (fill-in-the-blank)
        if testType == "objective":
            objective_generator = ObjectiveTest(inputText, noOfQues)
            question_list, answer_list, options_list = objective_generator.generate_test()
            testgenerate = zip(question_list, answer_list)
            question_type = "fillintheblank"

        # Generate subjective test
        elif testType == "subjective":
            subjective_generator = SubjectiveTest(inputText, noOfQues)
            question_list, answer_list = subjective_generator.generate_test()
            testgenerate = zip(question_list, answer_list)
            question_type = "subjective"

        else:
            flash('Error Occurred!')
            return redirect(url_for('index1'))

        # Save generated test to the database
        connection = create_connection()
        cursor = connection.cursor()
        
        # Process each question and answer
        for question, answer in testgenerate:
            # Check if answer length exceeds 255 characters
            if len(answer) > 255:
                print(f"Answer too long: {answer} (Length: {len(answer)})")
                truncated_answer = answer[:255]  # Truncate to fit column limit
            else:
                truncated_answer = answer
            
            # Insert question, answer, and type into the database
            cursor.execute(
                "INSERT INTO question_bank (question_text, correct_answer, type) VALUES (%s, %s, %s)",
                (question, truncated_answer, question_type)
            )

        connection.commit()  # Commit the transaction
        cursor.close()
        connection.close()

        flash('Question Bank generated successfully!', 'success')  # Flash success message
        return redirect(url_for('test_generate_form1'))





@app.route('/test_generate_form1')
def test_generate_form1():
    return render_template('index1.html')  # The HTML file you provided

def generate_related_options(inputText, correct_answer, num_options):
    # Split the input text into words and use them as potential distractors
    words = inputText.split()
    related_options = set()  # Use a set to avoid duplicates

    # Generate dummy distractors based on the inputText and correct_answer
    while len(related_options) < num_options:
        # Create a random option from the words
        option = random.choice(words) if words else f"Option{len(related_options) + 1}"
        
        # Ensure the option is not the correct answer
        if option != correct_answer:
            related_options.add(option)
    
    return list(related_options)

@app.route('/test_generate', methods=["POST"])
def test_generate():
    if request.method == "POST":
        inputText = request.form["itext"]
        noOfQues = int(request.form["noq"])

        # Generate the questions and answers
        objective_generator = ObjectiveTest(inputText, noOfQues)
        question_list, answer_list, options_list = objective_generator.generate_test()

        # Save generated test to the 'question_bank' table
        connection = create_connection()
        cursor = connection.cursor()

        for question, options, correct_answer in zip(question_list, options_list, answer_list):
            # Check if fewer than 4 options are provided
            if len(options) < 4:
                # Generate distractors based on the inputText
                filler_options = generate_related_options(inputText, correct_answer, 4 - len(options))
                random.shuffle(filler_options)  # Shuffle the fillers
                options = options + filler_options[:(4 - len(options))]  # Add the missing fillers

            # Ensure exactly four options by padding or slicing
            options = (options + [''] * 4)[:4]

            # Debugging lines
            print(f"Inserting Question: {question}")
            print(f"Options: {options}")
            print(f"Correct Answer: {correct_answer}")

            cursor.execute(
                """
                INSERT INTO question_banke (question_text, option1, option2, option3, option4, correct_answer) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    question,        # question_text
                    options[0],      # option1
                    options[1],      # option2
                    options[2],      # option3
                    options[3],      # option4
                    correct_answer   # correct_answer
                )
            )

        connection.commit()  # Commit the transaction
        cursor.close()
        connection.close()

        flash('Question Bank generated successfully!', 'success')
        
        # Redirect to the correct endpoint
        return redirect(url_for('trainer_dashboard'))

    
@app.route('/self_assessment')
def self_assessment():
    return render_template('self_assessment.html')
@app.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'POST':
        report_type = request.form['report_type']
        report_format = request.form['report_format']

        # Based on the selected report type, generate appropriate content
        if report_type == 'usage_statistics':
            report_data = generate_usage_statistics()
        elif report_type == 'question_bank_summary':
            report_data = generate_question_bank_summary()
        elif report_type == 'system_health':
            report_data = generate_system_health_report()
        else:
            report_data = "Invalid Report Type"

        # Generate report in PDF format
        if report_format == 'pdf':
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            pdf.drawString(100, 750, f"Report: {report_type.replace('_', ' ').title()}")
            pdf.drawString(100, 730, report_data)
            pdf.showPage()
            pdf.save()
            buffer.seek(0)
            return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype='application/pdf')

        # Generate report in Excel format
        elif report_format == 'excel':
            buffer = BytesIO()
            df = pd.DataFrame([{'Report Data': report_data}])
            writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name=report_type.title())
            
            return send_file(buffer, as_attachment=True, download_name="report.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # If it's a GET request, just render the report selection form
    return render_template('generate_report.html')


def generate_usage_statistics():
    # Placeholder function - replace with actual logic
    return "Usage statistics data..."

def generate_question_bank_summary():
    # Placeholder function - replace with actual logic
    return "Question bank generation summary data..."

def generate_system_health_report():
    # Placeholder function - replace with actual logic
    return "System health report data..."

@app.route('/admin_dashboard')
def admin_dashboard():
    # Your logic here
    return render_template('trainer.html')


@app.route('/questions', methods=['GET'])
def get_questions():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT question_text, option_a, option_b, option_c, option_d, correct_answer FROM questions")
    questions = cursor.fetchall()
    cursor.close()
    connection.close()

    # Convert to JSON format
    question_list = []
    for question in questions:
        question_list.append({
            'question_text': question[0],
            'option_a': question[1],
            'option_b': question[2],
            'option_c': question[3],
            'option_d': question[4],
            'correct_answer': question[5]
        })

    return jsonify(question_list)
new_feedback_count = 0
notifications_enabled = True
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    global new_feedback_count  # Use the global variable to track feedback count
    username = request.form['username']
    role = request.form['role']
    feedback_text = request.form['feedback']

    # Store feedback in the database
    connection = create_connection()
    cursor = connection.cursor()
    
    sql = "INSERT INTO feedback (username, role, feedback) VALUES (%s, %s, %s)"
    values = (username, role, feedback_text)
    
    cursor.execute(sql, values)
    connection.commit()
    cursor.close()
    connection.close()

    new_feedback_count += 1  # Increment the feedback count

    # Flash a success message
    flash('Feedback submitted successfully!', 'success')

    # Render the employee dashboard
    return render_template('employee.html', username=username)

@app.route('/view_feedback')
def view_feedback():
    # Connect to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Fetch all feedback from the feedback table
    cursor.execute("SELECT id, feedback, feedback_date, username, role FROM feedback")
    feedback_data = cursor.fetchall()
    
    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Render the feedback review template
    return render_template('view_feedback.html', feedback_data=feedback_data)

@app.route('/check_feedback', methods=['GET'])
def check_feedback():
    global new_feedback_count
    has_new_feedback = new_feedback_count > 0
    if has_new_feedback:
        new_feedback_count = 0  # Reset the count after checking
    return jsonify({"new_feedback": has_new_feedback})

@app.route('/feedback', methods=['GET'])
def feedback():
    return render_template('feedback.html')


    # Insert feedback into the feedback table
    insert_query = """
        INSERT INTO feedback (username, role, feedback, feedback_date) 
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_query, (username, role, feedback_text, feedback_date))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('feedback_success'))  # Redirect after successful submission

@app.route('/feedback_success')
def feedback_success():
    return "Feedback submitted successfully!"

@app.route('/learning-plan', methods=['GET'])
def learning_plan():
    return render_template('plan.html')
@app.route('/generate-learning-plan', methods=['POST'])
def generate_learning_plan():
    data = request.get_json()

    subject = data.get('subject')
    duration = data.get('duration')
    goals = data.get('goals')
    learning_style = data.get('learningStyle')

    # Basic validation
    if not subject or not duration or not goals or not learning_style:
        return jsonify({"error": "All fields are required."}), 400

    # Logic to generate the learning plan
    learning_plan = {
        "subject": subject,
        "duration": duration,
        "goals": goals,
        "learning_style": learning_style,
        "weekly_schedule": []
    }

    # Generate a basic weekly schedule
    for week in range(1, duration + 1):
        week_plan = {
            "week": week,
            "activities": []
        }

        if learning_style == "visual":
            week_plan["activities"].append(f"Watch educational videos on {subject}.")
            week_plan["activities"].append(f"Create mind maps related to {subject}.")
        elif learning_style == "auditory":
            week_plan["activities"].append(f"Listen to podcasts about {subject}.")
            week_plan["activities"].append(f"Participate in study groups for discussions on {subject}.")
        elif learning_style == "kinesthetic":
            week_plan["activities"].append(f"Engage in hands-on projects related to {subject}.")
            week_plan["activities"].append(f"Visit places (like labs or workshops) that relate to {subject}.")
        elif learning_style == "reading_writing":
            week_plan["activities"].append(f"Read textbooks and articles about {subject}.")
            week_plan["activities"].append(f"Write summaries of what you learn in each session.")

        learning_plan["weekly_schedule"].append(week_plan)

    return jsonify({"plan": learning_plan})
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('login'))  # Redirect to the login page


@app.route('/generate_quiz', methods=['GET'])
def generate_quiz():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch random questions from the database
    cursor.execute("SELECT question_text, option1, option2, option3, option4, correct_answer FROM question_banke ORDER BY RAND() LIMIT 5")
    questions = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(questions)

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    data = request.get_json()
    answers = data['answers']  # User-submitted answers

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch correct answers for the questions that the user answered
    question_texts = tuple(answers.keys())
    format_strings = ','.join(['%s'] * len(question_texts))
    query = f"SELECT question_text, correct_answer FROM question_banke WHERE question_text IN ({format_strings})"
    
    cursor.execute(query, question_texts)
    correct_answers_data = cursor.fetchall()

    correct_answers = {item['question_text']: item['correct_answer'] for item in correct_answers_data}

    cursor.close()
    connection.close()

    # Calculate score
    score = 0
    for question_text, user_answer in answers.items():
        # Normalize both user answer and correct answer
        normalized_user_answer = user_answer.strip().lower()
        correct_answer = correct_answers.get(question_text, "").strip().lower()

        if normalized_user_answer == correct_answer:
            score += 1

    total_questions = len(answers)  # This assumes that you are always getting the correct number of questions.
    percentage = (score / total_questions) * 100  # Calculate percentage score

    # Determine if tasks are completed based on the score
    task_completed = percentage >= 50

    # Update task status in session (or database)
    session['task_status'] = 'Completed' if task_completed else 'Incomplete'

    # Return score and task completion message to the user
    return jsonify({
        'score': score,
        'total_questions': total_questions,
        'task_completed': task_completed  # Add this flag to check task completion on the client-side
    })

@app.route('/submit_results')
def show_results():
    score = int(request.args.get('score'))
    total_questions = int(request.args.get('total_questions'))
    percentage = (score / total_questions) * 100

    # Determine the completion message based on the score percentage
    completion_message = (
        "You have completed today's tasks!"
        if percentage >= 50
        else "You did not complete today's tasks. Keep trying!"
    )
    
    return render_template('show_results.html', score=score, total_questions=total_questions, completion_message=completion_message, task_status=session.get('task_status', 'Not Started'))

@app.route('/auto_questions')
def auto_questions():
    return render_template('auto_question.html')

@app.route('/index1')
def index1():
    return render_template('index1.html')

@app.route('/quiz')
def quiz():
    user = {
        'task_status': session.get('task_status', 'Not Started')  # Default to 'Not Started' if not set
    }
    return render_template('quiz.html', user=user)

@app.route('/quiza')
def quiza():
    return render_template('quiza.html')

# @app.route('/self_assessment')
# def self_assessment():
#     multiple_choice_questions = fetch_mcq_questions()
#     fill_in_the_blanks_questions = fetch_fib_questions()
#     subjective_questions = fetch_subjective_questions()
    
    return render_template(
        'self_assessment.html',
        multiple_choice_questions=multiple_choice_questions,
        fill_in_the_blanks_questions=fill_in_the_blanks_questions,
        subjective_questions=subjective_questions
    )

@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    mcq_answers = {key: value for key, value in request.form.items() if key.startswith("mcq")}
    fib_answers = {key: value for key, value in request.form.items() if key.startswith("fib")}
    subjective_answers = {key: value for key, value in request.form.items() if key.startswith("subjective")}

    mcq_score = score_mcq(mcq_answers)
    fib_score = score_fib(fib_answers)
    subjective_score = score_subjective(subjective_answers)

    total_score = mcq_score + fib_score + subjective_score
    flash(f'Your total score is {total_score}', 'success')
    
    return redirect(url_for('self_assessment'))

def fetch_mcq_questions():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM question_banke WHERE question_type = 'objective' LIMIT 10")
    questions = cursor.fetchall()
    cursor.close()
    connection.close()
    return questions

def fetch_fib_questions():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM question_bank WHERE question_type = 'fill_in_the_blank' LIMIT 5")
    questions = cursor.fetchall()
    cursor.close()
    connection.close()
    return questions

def fetch_subjective_questions():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM question_bank WHERE question_type = 'subjective' LIMIT 2")
    questions = cursor.fetchall()
    cursor.close()
    connection.close()
    return questions

def score_mcq(mcq_answers):
    correct_answers = 0
    for key, user_answers in mcq_answers.items():
        question_id = key.split('_')[1]
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT correct_answer FROM question_banke WHERE id = %s", (question_id,))
        correct_answer = cursor.fetchone()
        cursor.close()
        connection.close()
        if correct_answer and set(user_answers) == set(correct_answer['correct_answer'].split(',')):
            correct_answers += 1
    return correct_answers

def score_fib(fib_answers):
    correct_answers = 0
    for key, user_answer in fib_answers.items():
        question_id = key.split('_')[1]
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT answer FROM question_bank WHERE id = %s", (question_id,))
        correct_answer = cursor.fetchone()
        cursor.close()
        connection.close()
        if correct_answer and user_answer.strip().lower() == correct_answer['correct_answer'].strip().lower():
            correct_answers += 1
    return correct_answers

def score_subjective(subjective_answers):
    total_score = 0
    for key, user_answer in subjective_answers.items():
        question_id = key.split('_')[1]
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT answer FROM question_bank WHERE id = %s", (question_id,))
        correct_answer = cursor.fetchone()
        cursor.close()
        connection.close()
        if correct_answer and any(keyword in user_answer.lower() for keyword in correct_answer['correct_answer'].lower().split(',')):
            total_score += 1
    return total_score
@app.route('/selfa')
def selfa():
    return render_template('selfa.html')  # Render your self-assessment questions page

@app.route('/nextself')
def next_self():
    return render_template('nextself.html')
user_data = {}

@app.route('/download_certificate')
def download_certificate():
    username = request.args.get('username')
    if username:
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(0, 10, 'Certificate of Completion', 0, 1, 'C')
        pdf.set_font("Arial", '', 16)
        pdf.cell(0, 10, f'Congratulations, {username}!', 0, 1, 'C')
        pdf.cell(0, 10, 'You have successfully completed the assessment.', 0, 1, 'C')
        pdf.cell(0, 10, 'From HexaWare', 0, 1, 'C')

        # Save the PDF to a temporary file
        pdf_output_path = f'certificates/{username}_certificate.pdf'
        pdf.output(pdf_output_path)

        # Send the file to the user
        return send_file(pdf_output_path, as_attachment=True)

    return "Username not provided", 400
@app.route('/certificate')
def certificate():
    return render_template('certificate.html')

@app.route('/generate_certificate/<username>')
def generate_certificate(username):
    # Fetch employee details (this is a placeholder; replace with your database logic)
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT username, date FROM employee_data WHERE username = %s", (username,))
    result = cursor.fetchone()
    
    if result:
        employee_name = result[0]
        award_date = result[1].strftime("%B %d, %Y")
    else:
        employee_name = "Unknown Employee"
        award_date = datetime.now().strftime("%B %d, %Y")

    cursor.close()
    connection.close()
    
    # Render HTML template with employee name and award date
    rendered = render_template("certificate.html", employee_name=employee_name, award_date=award_date)
    
    # Generate PDF from HTML
    pdf = pdfkit.from_string(rendered, False)

    # Create a response with PDF headers for download
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{employee_name}_Certificate.pdf"'

    return response

@app.route('/example', methods=['GET'])
def example():
    data = {"message": "Hello, World!"}
    
    # Create a response object
    response = make_response(jsonify(data), 200)
    
    # Set custom headers if needed
    response.headers['Custom-Header'] = 'Custom Value'
    
    return response
@app.route('/user_activity')
def user_activity():
    # Connect to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Fetch all user activity from the user_activity table
    cursor.execute("SELECT username, activity, timestamp FROM user_activity")
    user_activity_data = cursor.fetchall()
    
    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Render the user activity report
    return render_template('user_activity.html', user_activity_data=user_activity_data)


if __name__ == '__main__':
     
        app.run( port=5001, debug=True)
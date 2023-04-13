from flask import Flask, render_template, request, redirect
import json
import datetime
from calendar import monthrange
import random

app = Flask(
  __name__,
  template_folder='templates',
  static_folder='static'
  )

#######################################################
####################### Routing #######################
#######################################################

# Intro screen
@app.route('/')
def intro():
  return render_template('intro.html')

# Admin Login Screen
@app.route('/admin-login', methods=['POST', 'GET'])
def admin_login():
  if (request.method == 'POST'):
    email = request.form['email']
    password = request.form['password']
    name = check_json(email, password)
    if (len(name) != 0):
      global user_email
      user_email = email
      global user_password
      user_password = password
      global user_name
      user_name = name
      return redirect('/admin-home')
    else:
      return render_template('admin-login.html', incorrect=True)
  else:
    return render_template('admin-login.html')

# Admin Signup Screen
@app.route('/admin-signup', methods=['POST', 'GET'])
def admin_signup():
  if (request.method == 'POST'):
    data = {'email': request.form['email'], 
            'password': request.form['password'],
            'name': request.form['name']}
    
    if (len(check_json(data['email'], data['password'])) != 0):
      return render_template('admin-signup.html', repeat=True)
    else:
      write_json(data)
      return redirect('/admin-login')
  else:
    return render_template('admin-signup.html')

# Admin Home Screen
@app.route('/admin-home')
def admin_home():
  return render_template('admin-home.html', name=user_name)

# Student Login Screen
@app.route('/student-login', methods=['POST', 'GET'])
def student_login():
  if (request.method == 'POST'):
    email = request.form['email']
    password = request.form['password']
    name = check_json(email, password, filename='students.json')
    if (len(name) != 0):
      global student_email
      student_email = email
      global student_password
      student_password = password
      global student_name
      student_name = name
      global student_grade
      student_grade = get_student_info(student_email, student_password)[1]
      return redirect('/student-home')
    else:
      return render_template('student-login.html', incorrect=True)
  else:
    return render_template('student-login.html')

# Student Signup Screen
@app.route('/student-signup', methods=['POST', 'GET'])
def student_signUp():
  if (request.method == 'POST'):
    data = {'email': request.form['email'], 
            'password': request.form['password'],
            'name': request.form['name'],
            'grade': request.form['grade'],
            'points': 0}
    
    if (len(check_json(data['email'], data['password'], filename='students.json')) != 0):
      return render_template('student-signup.html', repeat=True)
    else:
      write_json(data, filename='students.json')
      return redirect('/student-login')
  else:
    return render_template('student-signup.html')
  
# Student Home Screen
@app.route('/student-home')
def student_home():
  points = get_student_info(student_email, student_password)[0]
  return render_template('student-home.html', 
                         name=student_name, 
                         points=points,
                         grade=student_grade)
  
# Grade Leaderboard
@app.route('/grade-leaderboard', methods=['POST', 'GET'])
def grade_leaderboard():
  if (request.method == 'POST'):
    grade = request.form['grade-selection']
    leaderboard = get_grade_leaderboard(grade)[0:10]
    return leaderboard
  else:
    return render_template('grade-leaderboard.html')
  
# Student Leaderboard
@app.route('/student-leaderboard')
def student_leaderboard():
  student_leaderboard = get_student_leaderboard()[0:10]
  return render_template('student-leaderboard.html', leaderboard=student_leaderboard)

# Add Event for Admin
@app.route('/add-event', methods=['POST', 'GET'])
def add_event():
  if (request.method == 'POST'):
    event_data = {'name': request.form['event-name'],
                  'description': request.form['event-description'],
                  'date': request.form['event-date']}
    write_json(event_data, filename='events.json', start='events')
  return render_template('add-event.html')

# Past Events Screen
@app.route('/past-events', methods=['POST', 'GET'])
def past_events():
  if (request.method == 'POST'):
    event_number = len(get_events()[0])
    points_increase = 0
    for i in range(event_number):
      if (request.form['events' + str(i)] == 'yes'):
        points_increase += 20
    add_points(student_email, student_password, points_increase)
    return redirect('/student-home')
  else:
    past_events = get_events()[0]
    return render_template('past-events.html', events=past_events)

# Upcoming Events Screen
@app.route('/upcoming-events')
def upcoming_events():
  upcoming_events = get_events()[1]
  return render_template('upcoming-events.html', events=upcoming_events)

# Quarter Winner Screen
@app.route('/quarter-winner')
def quarter_winner():
  today = datetime.date.today()
  quarter_start = datetime.date(today.year, 3 * get_quarter(today.month) - 2, 1)
  quarter_end = datetime.date(today.year, 3 * get_quarter(today.month), monthrange(today.year, 3 * get_quarter(today.month))[1])
  days_left = 0
  if (today == quarter_start):
    new_winners = choose_winners()
    with open('winners.json', 'r+') as file:
      file_data = json.load(file)
      file_data['winners'] = new_winners
    with open('winners.json', 'w') as file:
      json.dump(file_data, file)
  else:
    days_left = (quarter_end - today).days
  with open('winners.json', 'r+') as file:
    file_data = json.load(file)
    winners = file_data['winners']
  return render_template('quarter-winner.html', winners=winners, days_left=days_left)

# Resetting Grade Leaderboard
@app.route('/reset-grade-leaderboard', methods=['POST'])
def reset_grade_leaderboard():
  grade = request.form['grade']
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    students_data = file_data['users']
    for student in students_data:
      if (student['grade'] == grade):
        student['points'] = 0
    with open('students.json', 'w') as file:
      json.dump(file_data, file)
  return redirect('/admin-home')

# Resetting Student Leaderboard
@app.route('/reset-student-leaderboard', methods=['GET'])
def reset_student_leaderboard():
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    students_data = file_data['users']
    for student in students_data:
      student['points'] = 0
    with open('students.json', 'w') as file:
      json.dump(file_data, file)
  return redirect('/admin-home')

# All Events Screen for Admin
@app.route('/all-events')
def all_events():
  past_events = get_events()[0]
  upcoming_events = get_events()[1]
  events = past_events + upcoming_events
  return render_template('all-events.html', events=events)

##############################################################
####################### Helper Methods #######################
##############################################################
  
def write_json(new_data, filename='admin.json', start='users'):
  with open(filename, 'r+') as file:
    file_data = json.load(file)
    file_data[start].append(new_data)
    file.seek(0)
    json.dump(file_data, file, indent=4)
    
def check_json(email, password, filename='admin.json'):
  with open(filename, 'r+') as file:
    file_data = json.load(file)
    user_data = file_data['users']
    for user in user_data:
      if (user['email'] == email and user['password'] == password):
        return user['name']
    return ''
  
def get_student_info(email, password):
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    student_data = file_data['users']
    for student in student_data:
      if (student['email'] == email and student['password'] == password):
        return [student['points'], student['grade']]
    return [-1, -1]
  
def get_grade_leaderboard(grade):
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    student_data = file_data['users']
    grade_students = []
    for student in student_data:
      if (student['grade'] == grade):
        grade_students.append([student['name'], student['points']])
    grade_students.sort(key=sort_second, reverse=True)
    return grade_students
  
def get_student_leaderboard():
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    student_data = file_data['users']
    student_leaderboard = []
    for student in student_data:
      student_leaderboard.append([student['name'], student['points']])
    student_leaderboard.sort(key=sort_second, reverse=True)
    return student_leaderboard
  
def get_events():
  with open('events.json', 'r+') as file:
    file_data = json.load(file)
    event_data = file_data['events']
    past_events = []
    upcoming_events = []
    for event in event_data:
      event_date = datetime.datetime.strptime(event['date'], '%Y-%m-%d')
      today = datetime.datetime.today()
      if (event_date > today):
        upcoming_events.append(event)
      elif (event_date > today - datetime.timedelta(days=10)):
        past_events.append(event)
    return [past_events, upcoming_events]
  
def add_points(email, password, points_increase):
  with open('students.json') as file:
    file_data = json.load(file)
    students_data = file_data['users']
    for student in students_data:
      if (student['email'] == email and student['password'] == password):
        student['points'] += points_increase
    with open('students.json', 'w') as file:
      json.dump(file_data, file)
      
def choose_winners():
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    student_data = file_data['users']
    freshman = []
    sophomores = []
    juniors = []
    seniors = []
    for student in student_data:
      if (student['grade'] == '9'):
        freshman.append(student)
      elif (student['grade'] == '10'):
        sophomores.append(student)
      elif (student['grade'] == '11'):
        juniors.append(student)
      elif (student['grade'] == '12'):
        seniors.append(student)
    return [random.choice(freshman), random.choice(sophomores), random.choice(juniors), random.choice(seniors)]

def get_quarter(month):
  return (month - 1) // 3 + 1

def sort_second(val):
  return val[1]
    
    
    
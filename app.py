# Imports
from flask import Flask, render_template, request, redirect
import json
import datetime
from calendar import monthrange
import random

# Starting App
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
  # POST request for Login information
  if (request.method == 'POST'):
    email = request.form['email']
    password = request.form['password']
    name = check_json(email, password)
    
    # If the login credentials are correct, then go to admin home
    if (len(name) != 0):
      global user_name
      user_name = name
      return redirect('/admin-home')
    
    # If the login credentials are incorrect, show user that they have entered incorrectly
    else:
      return render_template('admin-login.html', incorrect=True)
  # GET request for getting page
  else:
    return render_template('admin-login.html')

# Admin Signup Screen
@app.route('/admin-signup', methods=['POST', 'GET'])
def admin_signup():
  # Post request for Sign Up information
  if (request.method == 'POST'):
    data = {'email': request.form['email'], 
            'password': request.form['password'],
            'name': request.form['name']}
    
    # If the email has already been used, tell the user to use another email
    if (len(check_json(data['email'], data['password'])) != 0):
      return render_template('admin-signup.html', repeat=True)
    
    # If the email has not been used, add credentials to JSON file 
    else:
      write_json(data)
      return redirect('/admin-login')
    
  # GET request for Sign Up Screen
  else:
    return render_template('admin-signup.html')

# Admin Home Screen
@app.route('/admin-home')
def admin_home():
  # Simply returns the admin-home.html template with the user's name
  return render_template('admin-home.html', name=user_name)

# Student Login Screen
@app.route('/student-login', methods=['POST', 'GET'])
def student_login():
  # POST request for getting student login information
  if (request.method == 'POST'):
    email = request.form['email']
    password = request.form['password']
    name = check_json(email, password, filename='students.json')
    
    # If the login information is correct, take student to their home page
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
    
    # If the login information is incorrect, inform user
    else:
      return render_template('student-login.html', incorrect=True)
    
  # GET request for showing student login screen
  else:
    return render_template('student-login.html')

# Student Signup Screen
@app.route('/student-signup', methods=['POST', 'GET'])
def student_signUp():
  # POST request for getting student sign up data
  if (request.method == 'POST'):
    data = {'email': request.form['email'], 
            'password': request.form['password'],
            'name': request.form['name'],
            'grade': request.form['grade'],
            'points': 0}
    
    # If the student already has an account, inform the user
    if (len(check_json(data['email'], data['password'], filename='students.json')) != 0):
      return render_template('student-signup.html', repeat=True)
    
    # If the student does not have an account, add student data to JSON file
    else:
      write_json(data, filename='students.json')
      return redirect('/student-login')
  
  # GET request to render student signup screen
  else:
    return render_template('student-signup.html')
  
# Student Home Screen
@app.route('/student-home')
def student_home():
  # Rendering student home screen
  points = get_student_info(student_email, student_password)[0]
  return render_template('student-home.html', 
                         name=student_name, 
                         points=points,
                         grade=student_grade)
  
# Grade Leaderboard
@app.route('/grade-leaderboard', methods=['POST', 'GET'])
def grade_leaderboard():
  # POST request for getting grade selection given by user
  if (request.method == 'POST'):
    grade = request.form['grade-selection']
    
    # Getting the top 10 students for each grade
    leaderboard = get_grade_leaderboard(grade)[0:10]
    return leaderboard
  
  # GET request for grade leaderboard page
  else:
    return render_template('grade-leaderboard.html')
  
# Student Leaderboard
@app.route('/student-leaderboard')
def student_leaderboard():
  # Rendering grade leaderboard page by displaying top 10 students in school
  student_leaderboard = get_student_leaderboard()[0:10]
  return render_template('student-leaderboard.html', leaderboard=student_leaderboard)

# Add Event for Admin
@app.route('/add-event', methods=['POST', 'GET'])
def add_event():
  # POST request for getting new event information
  if (request.method == 'POST'):
    event_data = {'name': request.form['event-name'],
                  'description': request.form['event-description'],
                  'date': request.form['event-date']}
    
    # Adding new event to events.json file
    write_json(event_data, filename='events.json', start='events')
  
  # GET request for rendering add-event page
  else:
    return render_template('add-event.html')

# Past Events Screen
@app.route('/past-events', methods=['POST', 'GET'])
def past_events():
  # POST request for giving points to students for attending events
  if (request.method == 'POST'):
    event_number = len(get_events()[0])
    points_increase = 0
    
    # Adding 20 points for each event that the student attended
    for i in range(event_number):
      if (request.form['events' + str(i)] == 'yes'):
        points_increase += 20
    add_points(student_email, student_password, points_increase)
    return redirect('/student-home')
  
  # GET request displaying events that already happened (past events)
  else:
    past_events = get_events()[0]
    return render_template('past-events.html', events=past_events)

# Upcoming Events Screen
@app.route('/upcoming-events')
def upcoming_events():
  # GET request displaying upcoming events (in the future)
  upcoming_events = get_events()[1]
  return render_template('upcoming-events.html', events=upcoming_events)

# All Events Screen for Admin
@app.route('/all-events')
def all_events():
  # Admin can see all the events and that's what this page renders
  past_events = get_events()[0]
  upcoming_events = get_events()[1]
  events = past_events + upcoming_events
  return render_template('all-events.html', events=events)

# Quarter Winner Screen
@app.route('/quarter-winner')
def quarter_winner():
  # Getting quarter start and end dates based on today's date
  today = datetime.date.today()
  quarter_start = datetime.date(today.year, 3 * get_quarter(today.month) - 2, 1)
  quarter_end = datetime.date(today.year, 3 * get_quarter(today.month), monthrange(today.year, 3 * get_quarter(today.month))[1])
  days_left = 0
  
  # If today is the quarter's start, choose a random winner and update the page
  if (today == quarter_start):
    new_winners = choose_winners()
    with open('winners.json', 'r+') as file:
      file_data = json.load(file)
      file_data['winners'] = new_winners
    with open('winners.json', 'w') as file:
      json.dump(file_data, file)
  
  # If today is not the quarter's start, don't choose another winner
  # Additionally display how many days until the quarter ends
  else:
    days_left = (quarter_end - today).days
  with open('winners.json', 'r+') as file:
    file_data = json.load(file)
    winners = file_data['winners']
  return render_template('quarter-winner.html', winners=winners, days_left=days_left)

# Resetting Grade Leaderboard
@app.route('/reset-grade-leaderboard', methods=['POST'])
def reset_grade_leaderboard():
  # Get grade specified by user
  grade = request.form['grade']
  
  # Get all students in that grade and make their points = 0
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
  # Make all the students in the students.json file have points = 0
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    students_data = file_data['users']
    for student in students_data:
      student['points'] = 0
    with open('students.json', 'w') as file:
      json.dump(file_data, file)
  return redirect('/admin-home')

# End of Quarter Report
@app.route('/report')
def report():
  # Get the quarter start and end date
  today = datetime.date.today()
  quarter_start = datetime.date(today.year, 3 * get_quarter(today.month) - 2, 1)
  quarter_end = datetime.date(today.year, 3 * get_quarter(today.month), monthrange(today.year, 3 * get_quarter(today.month))[1])
  days_left = 0
  
  # If today is the start of the quarter, generate a new report of points/student in each grade
  if (today == quarter_start):
    data = [points_per_student('9'), points_per_student('10'), points_per_student('11'), points_per_student('12')]
    return render_template('report.html', days_left=days_left, data=data)
  
  # Else display the number of days until the end of the quarter
  else:
    days_left = (quarter_end - today).days
    return render_template('report.html', days_left=days_left, data=[])

# Prizes Screen
@app.route('/prizes')
def prizes():
  # Show prizes by getting them from the prizes.json file
  with open('prizes.json', 'r+') as file:
    file_data = json.load(file)
    prizes_data = file_data['prizes']
    return render_template('prizes.html', prizes=prizes_data)
  
# Changing Prizes Screen
@app.route('/change-prizes')
def change_prizes():
  # Rendering the change prizes screen
  return render_template('change-prizes.html')

# Add a Prize
@app.route('/add-prize', methods=['POST'])
def add_prize():
  # Simply getting data from user about the prize and adding that data to prizes.json
  data = {
    'prize': request.form['prize'],
    'points': request.form['points'],
    'category': request.form['category']
  }
  
  write_json(data, filename='prizes.json', start='prizes')
  return redirect('/admin-home')

# Replace an existing prize
@app.route('/replace-prize', methods=['POST'])
def replace_prize():
  # Getting original prize name
  original_prize = request.form['original-prize']
  new_data = {
    'prize': request.form['new-prize'],
    'points': request.form['points'],
    'category': request.form['category']
  }
  
  # Replacing original prize with new prize in prizes.json file
  with open('prizes.json', 'r+') as file:
    file_data = json.load(file)
    prizes_data = file_data['prizes']
    for prize in prizes_data:
      if (prize['prize'] == original_prize):
        prize['prize'] = request.form['new-prize']
        prize['points'] = request.form['points']
        prize['category'] = request.form['category']
    with open('prizes.json', 'w') as file:
      json.dump(file_data, file)
  
  return redirect('/admin-home')

##############################################################
####################### Helper Methods #######################
##############################################################
  
def write_json(new_data, filename='admin.json', start='users'):
  '''
  Opens a JSON file and adds a new value to it
  '''
  with open(filename, 'r+') as file:
    file_data = json.load(file)
    file_data[start].append(new_data)
    file.seek(0)
    json.dump(file_data, file, indent=4)

def check_json(email, password, filename='admin.json'):
  '''
  Checks a JSON file for a specfic user through their email and password
  Returns the name of that user
  If the user is not found, the method will return an empty string
  '''
  with open(filename, 'r+') as file:
    file_data = json.load(file)
    user_data = file_data['users']
    for user in user_data:
      if (user['email'] == email and user['password'] == password):
        return user['name']
    return ''

def get_student_info(email, password):
  '''
  Returns the points and grade of a student based on their email and password
  '''
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    student_data = file_data['users']
    for student in student_data:
      if (student['email'] == email and student['password'] == password):
        return [student['points'], student['grade']]
    return [-1, -1]
  
def get_grade_leaderboard(grade):
  '''
  Returns the leaderboard (based on points) for a grade in decreasing order
  '''
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
  '''
  Returns the leaderboard (based on points) for whole school in decreasing order
  '''
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    student_data = file_data['users']
    student_leaderboard = []
    for student in student_data:
      student_leaderboard.append([student['name'], student['points']])
    student_leaderboard.sort(key=sort_second, reverse=True)
    return student_leaderboard

def get_events():
  '''
  Separates all events into past events and upcoming events based on today's date
  Note that if any event happened more than 2 weeks before today, it will not be returned
  Returns the past events and upcoming events
  '''
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
      elif (event_date > today - datetime.timedelta(days=14)):
        past_events.append(event)
    return [past_events, upcoming_events]
  
def add_points(email, password, points_increase):
  '''
  Adds points to a student's account in the students.json file using their email and password
  '''
  with open('students.json') as file:
    file_data = json.load(file)
    students_data = file_data['users']
    for student in students_data:
      if (student['email'] == email and student['password'] == password):
        student['points'] += points_increase
    with open('students.json', 'w') as file:
      json.dump(file_data, file)

def choose_winners():
  '''
  Chooses and returns random winners from each grade no matter their point accumulation
  '''
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

def points_per_student(grade):
  '''
  Returns the points per student value for a specific grade
  '''
  with open('students.json', 'r+') as file:
    file_data = json.load(file)
    student_data = file_data['users']
    total_points = 0
    total_students = 0
    for student in student_data:
      if (student['grade'] == grade):
        total_students += 1
        total_points += student['points']
    return total_points / total_students

def get_quarter(month):
  '''
  Determining which quarter of the year today's month is in
  '''
  return (month - 1) // 3 + 1

def sort_second(val):
  '''
  Helps for sorting array of nested arrays based on second item of nested array
  '''
  return val[1]
    
    
    
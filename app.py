from flask import Flask, render_template, request, redirect
import json

app = Flask(
  __name__,
  template_folder='templates',
  static_folder='static'
  )

####################### Routing #######################

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
            'points': 0}
    
    if (len(check_json(data['email'], data['password'], filename='students.json')) != 0):
      return render_template('student-signup.html', repeat=True)
    else:
      write_json(data, filename='students.json')
      return redirect('/student-login')
  else:
    return render_template('student-signup.html')

####################### Helper Methods #######################
  
def write_json(new_data, filename='admin.json'):
  with open(filename, 'r+') as file:
    file_data = json.load(file)
    file_data['users'].append(new_data)
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
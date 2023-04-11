from flask import Flask, render_template, request, redirect
import json

app = Flask(
  __name__,
  template_folder='templates',
  static_folder='static'
  )

####################### Routing #######################

@app.route('/', methods=['POST', 'GET'])
def signup():
  if (request.method == 'POST'):
    data = {'email': request.form['email'], 
            'password': request.form['password'],
            'name': request.form['name']}
    
    if (len(check_json(data['email'], data['password'])) != 0):
      return render_template('signup.html', repeat=True)
    else:
      write_json(data)
      return redirect('/login')
  else:
    return render_template('signup.html')
  
@app.route('/login', methods=['POST', 'GET'])
def login():
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
      return redirect('/home')
    else:
      return render_template('login.html', incorrect=True)
  else:
    return render_template('login.html')
  
@app.route('/home')
def home():
  return render_template('home.html', name=user_name)

####################### Helper Methods #######################
  
def write_json(new_data, filename='data.json'):
  with open(filename, 'r+') as file:
    file_data = json.load(file)
    file_data['users'].append(new_data)
    file.seek(0)
    json.dump(file_data, file, indent=4)
    
def check_json(email, password, filename='data.json'):
  with open(filename, 'r+') as file:
    file_data = json.load(file)
    user_data = file_data['users']
    for user in user_data:
      if (user['email'] == email and user['password'] == password):
        return user['name']
    return ''
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
    
    if (check_json(request.form['email'], request.form['password'])):
      return render_template('signup.html', repeat=True)
    else:
      write_json(data)
      return redirect('/login')
  else:
    return render_template('signup.html')
  
@app.route('/login', methods=['POST', 'GET'])
def login():
  if (request.method == 'POST'):
    if (check_json(request.form['email'], request.form['password'])):
      return 'Logged In!'
    else:
      return 'Incorrect credentials!'
  else:
    return render_template('login.html')
  

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
        return True
    return False
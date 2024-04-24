import os
from flask import Flask, request, render_template, jsonify, abort, make_response
import json
import sqlite3
import pandas as pd

app = Flask(__name__, static_folder='public', template_folder='views')

@app.after_request 
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    # Other headers can be added here if needed
    return response
  

adm_pass = os.environ.get('ADMIN_SECRET')

@app.route('/v1/admin/getSocialDB')
def get_social_db():
    if request.args['secret']!=adm_pass:
      abort(401)
    conn = sqlite3.connect('database_social') 
    c = conn.cursor()
    c.execute('''
          SELECT
          id,
          name,
          text
          FROM comments
          ''')
    df = pd.DataFrame(c.fetchall(), columns=['id','name','text'])
    conn.commit()
    return df.to_string(index=False).replace('\n', '<br>')
  
@app.route('/v1/admin/createSocialDB')
def create_social_db():
    if request.args['secret']!=adm_pass:
      abort(401)
    conn = sqlite3.connect('database_social') 
    c = conn.cursor()
    c.execute('''
          CREATE TABLE comments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          text TEXT NOT NULL
          );
          ''')
    conn.commit()
    return "ok"
        
@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')
  
@app.route('/v1/social/saveComment', methods=['POST'])
def saveComment():
    data = json.loads(request.data)
    conn = sqlite3.connect('database_social') 
    c = conn.cursor()
    c.execute('''
          INSERT INTO comments (name, text)
                VALUES
                ("''' + data['name'] + '''","''' + data['text'] + '''")
          ''')
    conn.commit()
    return "ok"
  
@app.route('/v1/social/getComments', methods=['GET'])
def getComments():
    conn = sqlite3.connect('database_social') 
    c = conn.cursor()
    c.execute('''
          SELECT * FROM comments ORDER BY id DESC LIMIT 20;
          ''')
    dict = {}
    data = c.fetchall()
    i = 0
    for entity in data:
      dict[i] = {"name":entity[1],"text":entity[2]}
      i += 1
    return jsonify(dict)
    

if __name__ == '__main__':
    app.run()
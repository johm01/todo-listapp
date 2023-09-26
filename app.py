from flask import (render_template,request,logging,session,redirect,url_for)
from flask import Flask 
from flask_bcrypt import Bcrypt
import sqlite3 

app = Flask(__name__,template_folder='../todo-list/templates')
bcrypt = Bcrypt(app)
app.secret_key = "yo"

def used_username(name):
    db = sqlite3.connect("todo.db")
    cur = db.cursor()
    cur.execute("SELECT username FROM users")
    names = cur.fetchall()
    val = None
    for n in names:
        if n[0] == name:
            val = True 
        else:
            val = False
    return val 
# Check if username is already in use
def create_user(username,passw):
    db = sqlite3.connect("todo.db")
    cur = db.cursor()
    cur.execute("INSERT INTO users(username,password) VALUES(?,?)",(username,bcrypt.generate_password_hash(passw).decode('utf-8')))
    db.commit()

def login_user(username,passw:str):
    db = sqlite3.connect("todo.db")
    cur = db.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE username=?",(username,))
    user = cur.fetchone()
    if bcrypt.check_password_hash(user[2],passw):
        return user 
    else:
        return None

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register',methods=['POST','GET'])
def register():
    error = None
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']        
        
        if used_username(user):
            error = 'Username already in use'
        else:
            create_user(user,password)
            return redirect(url_for('login'))

    return render_template('index.html',error=error)

@app.route('/login',methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':    
        username = request.form['user']
        password = request.form['password']
        
        try:
            user = login_user(username,password)
            session["user_id"] = user[0]
            return redirect(url_for('page'))
        except:
            error = 'Incorrect Username or Password'
            return render_template('login.html',error=error)
     
    return render_template('login.html')

@app.route('/user/remove/<todo_id>',methods=['POST','GET'])
def remove(todo_id):
    if 'user_id' in session:
        db = sqlite3.connect('todo.db')
        cur = db.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?",(todo_id,))
        db.commit()
        db.close()
        return redirect(url_for('page'))

@app.route('/user/add',methods=['POST'])
def add():
    if 'user_id' in session:
        user_id = session['user_id']
        item = request.form['todo-item']
        db = sqlite3.connect('todo.db')
        cur = db.cursor()
        cur.execute("INSERT INTO tasks(task,user_id) VALUES (?,?)",(item,user_id))
        db.commit()
        db.close()
        return redirect(url_for('page'))

@app.route('/user',methods=['POST','GET'])
def page():
    if "user_id" in session:
        error = None
        user = session["user_id"]
        db = sqlite3.connect('todo.db')
        cur = db.cursor()
        cur.execute("SELECT task,id FROM tasks WHERE user_id=?",(user,))
        todo_list = cur.fetchall()
        return render_template('user_page.html',error=error,todo=todo_list)
    else:
        return redirect(url_for('login'))

#TODO Use htmx to be able to logout 
@app.route('/user/logout',methods=['POST'])
def logout():
    session.pop('user_id',None)
    return redirect(url_for('login'))


from crypt import methods
from distutils.log import debug
from socket import socket
from flask import Flask, render_template, request, redirect, url_for, session, flash
from numpy import broadcast
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, send
from flask import send_from_directory
from datetime import datetime
import os 


app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'red_social'
app.config['SECRET_KEY'] = 'secret'
app.secret_key = 'key_secret'
socketio = SocketIO(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA
mysql = MySQL(app)

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user!=None:
            if password == user[4]:
                session['id'] = user[0]
                session['name'] = user[1]
                session['lastname'] = user[2]
                session['email'] = user[3]
                return redirect(url_for('home'))
            else:
                flash("Error, contraseña no valida")
                return render_template('login.html')

        else:
            flash("Error, usuario no encontrado")
            return render_template('login.html')
    else:    
        return render_template('login.html')


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (name, lastname, email, password) VALUES (%s, %s, %s, %s)', 
        (name, lastname, email, password))
        mysql.connection.commit()
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')

@app.route('/home', methods = ['GET', 'POST'])
def home():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM post')
    data = cur.fetchall()
    return render_template('home.html',user=data)

@app.route('/cerrar', methods = ['GET', 'POST'])
def cerrar():
    if request.method == 'GET':
        session.clear()
        return redirect(url_for('login'))

@app.route('/profile/<id>', methods = ['POST'])
def profile(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s', (id))
    data = cur.fetchall()
    return render_template('profile.html', user = data)

@app.route('/subir/<id>', methods=['GET', 'POST'])
def subir(id):
    if request.method == 'POST':
        foto = request.files['foto']
        comentario = request.form['comentario']
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        if foto.filename!='':
                nuevoNombreFoto=tiempo + foto.filename
                foto.save("uploads/"+ nuevoNombreFoto)
                
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO post (foto, comentario, id_user) VALUES (%s,%s, %s)', 
        (nuevoNombreFoto, comentario, id))
        mysql.connection.commit()
        flash('publicacion exitosa')
        return redirect(url_for('home'))

@app.route('/deleted/<string:id>')
def deleted_post(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM post WHERE id = {0}'.format(id))
    mysql.connection.commit()
    return redirect(url_for('home'))


@socketio.on('message')
def handleMessage(msg):
    print("Message: " + msg)
    send(msg, broadcast = True)

@app.route('/chat', methods = ['POST'])
def chat():
    return render_template('chat.html')


    
        



if __name__ == '__main__':
    socketio.run(app, debug = True)

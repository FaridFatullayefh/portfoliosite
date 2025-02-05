import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = 'ITfAFXPUmZoPzcE'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

ADMIN_USER = "admin"
ADMIN_PASS = "admin"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Message {self.name}>"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
from flask import send_from_directory

@app.route('/download_resume')
def download_pdf():
    filename = 'document.pdf'  
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['user'] = username  
            return redirect(url_for('admin'))
        else:
            return render_template('login.html')

    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' in session and session['user'] == ADMIN_USER:
        messages = Message.query.all()  
        
        if request.method == 'POST':
            file = request.files['pdf']
            if file and allowed_file(file.filename):
                filename = 'document.pdf' 
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('admin'))  

        return render_template('admin.html', messages=messages)

    return redirect(url_for('login'))  

@app.route('/logout')
def logout():
    session.pop('user', None) 
    return redirect(url_for('login'))

@app.route('/submit_message', methods=['POST'])
def submit_message():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        new_message = Message(name=name, email=email, message=message)
        db.session.add(new_message)
        db.session.commit()

        return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.app_context():
        db.create_all() 

    app.run(debug=True)

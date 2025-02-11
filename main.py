# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SECRET_KEY'] = '7897654564321321852'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    ## we need to create a relation ship between the models so that we can cross refrence them
    days = relationship('day', backref='user', lazy=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Day Model
class day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_name = db.Column(db.String(50), nullable=False)
    split_name = db.Column(db.String(50), nullable=False)
    # exercises = db.Column(db.JSON, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if request.method == "POST":
            day_name = request.form.get("day_name")
            split_name = request.form.get("split_name")
            new_day = day(day_name=day_name,split_name=split_name,user_id=user.id)
            db.session.add(new_day)
            db.session.commit()
            flash('Workout added successfully!', 'success')
            return redirect(url_for('home'))

        return render_template('home.html', username=user.username )

    return render_template('home.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Username already exists')
            return redirect(url_for('signup'))

        if email_exists:
            flash('Email already registered')
            return redirect(url_for('signup'))

        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred. Please try again.')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!')
    return redirect(url_for('home'))

#home page routes
@app.route("/weight_lifting", methods=['GET', 'POST'])
def weight_lifting():
    if 'user_id' not in session:
        return render_template('weight_lifting.html')
    user = User.query.get(session['user_id'])
    days = user.days
    return render_template('weight_lifting.html', username=user.username , days=days)
@app.route("/cardio")
def cardio():
    print("hello")
@app.route("/meditation")
def meditation():
    print("hello")



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
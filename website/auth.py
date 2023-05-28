from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import datetime
from io import BytesIO
import base64

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email=request.form.get('email')
        first_name=request.form.get('firstName')
        password1=request.form.get('password1')
        password2=request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif password1!=password2:
            flash('Passwords don\'t match', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

def calculate_bmi(height, weight):
    bmi = weight / (height * height)
    return round(bmi, 2)

@auth.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if request.method == 'POST':
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        bmi = calculate_bmi(height, weight)
        return render_template("result.html", bmi=bmi, user=current_user)
    return render_template("bmi.html", user=current_user)

import io
import base64

def get_base64_encoded_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    encoded_image = base64.b64encode(buf.getvalue()).decode('utf-8')

    return encoded_image

@auth.route('/measurements', methods=['GET', 'POST'])
def measurements():
    if request.method == 'POST':
        user = current_user
        # Retrieve the measurements from the form
        bust = float(request.form['bust'])
        waist = float(request.form['waist'])
        hips = float(request.form['hips'])

        if current_user:
            # Update the existing user's measurements
            user.bust = bust
            user.waist = waist
            user.hips = hips
        else:
            # Create a new user with the measurements
            user = User(user=current_user, bust=bust, waist=waist, hips=hips)
            db.session.add(user)

        db.session.commit()

        # Plot the graph with previous and new measurements
        measurements = User.query.filter_by(user=current_user).all()
        bust_values = [m.bust for m in measurements]
        waist_values = [m.waist for m in measurements]
        hips_values = [m.hips for m in measurements]

        plt.plot(range(len(measurements)), bust_values, label='Bust')
        plt.plot(range(len(measurements)), waist_values, label='Waist')
        plt.plot(range(len(measurements)), hips_values, label='Hips')

        plt.xlabel('Days')
        plt.ylabel('Measurements')
        plt.title('User Measurement Progress')
        plt.legend()
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.clf()

        return 'Measurement graph plotted successfully!'
        return render_template('measurements.html', user=current_user, image_base64=image_base64)
    return render_template("measurements.html", user=current_user)


workout_data = {
    '2023-05-01': True,
    '2023-05-02': False,
    '2023-05-03': True,
    # Add more workout data as needed
}

@auth.route('/workout', methods=['POST', 'GET'])
def workout():
    if request.method == 'POST':
        today = datetime.date.today()
        day_of_week = today.strftime("%A")
        workout_option = request.form.get('workout_option')
        workout_class = 'worked-out' if workout_option == 'Yes' else 'not-worked-out'
        return render_template("calendar.html", user=current_user, workout_class=workout_class, day_of_week=day_of_week)
    return render_template("workout.html", user=current_user)
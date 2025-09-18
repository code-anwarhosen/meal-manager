from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import User
from app.utils import Auth

bp = Blueprint('user', __name__)


@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if Auth.is_authenticated():
        flash('You\'re already logged in!')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        if not phone or not password:
            flash('Phone and password are required!', 'error')
            return redirect(url_for('user.login'))
        
        user = User.get(username=phone)

        if user and User.check_password(password, user.password_hash):
            Auth.login_user(user.username, remember=remember)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))

        else:
            flash('Invalid phone number or password.', 'error')

    return render_template('login.html')


@bp.route('/logout/', methods=['GET'])
def logout():
    if not Auth.is_authenticated():
        flash('You\'re not logged in!')
        return redirect(url_for('user.login'))

    Auth.logout_user()
    flash('You\'re logged out!')
    return redirect(url_for('user.login'))


@bp.route('/register/', methods=['GET', 'POST'])
def register():
    if Auth.is_authenticated():
        flash('You\'re already logged in!')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        name = request.form.get('fullname')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if not name or not phone or not password:
            flash('Name, phone and password are required!', 'error')
            return redirect(url_for('user.register'))

        if password != confirm_password:
            flash("Passwords didn't match!", 'error')
            return redirect(url_for('user.register'))

        if len(password) < 6:
            flash("Password can't be less than 6 characters!", 'error')
            return redirect(url_for('user.register'))

        if User.exists(username=phone):
            flash(f"User already exists with this username!")
            return redirect(url_for('user.register'))

        pw_hash = User.make_password(password)  # Or generate_password_hash

        try:
            user_id = User.create(
                username=phone,
                name=name,
                password_hash=pw_hash
            )
        except Exception as e:
            flash(f'Error: {e}')
            return redirect(url_for('user.register'))

        print('User added:', user_id)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('user.login'))

    return render_template('register.html')


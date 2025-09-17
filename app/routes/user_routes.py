from flask import Blueprint, render_template, request

bp = Blueprint('user', __name__)

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        print(request.form)
        
    return render_template('login.html')

@bp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('fullname')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        
        print(request.form)
        
    return render_template('register.html')

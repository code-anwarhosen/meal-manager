from flask import Blueprint, render_template
from app.utils import login_required

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def home():
    return render_template('dashboard.html')


@bp.route('/group/<id>/')
@login_required
def group(id):
    return render_template('group.html')

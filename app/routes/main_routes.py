from flask import Blueprint, render_template, flash, request, redirect, url_for
from app.utils import login_required, current_user
from app.models import Group


bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def home():
    user = current_user()
    
    groups = Group.objects.filter(admin_user_id=user.id).all() # type: ignore
    return render_template('dashboard.html', groups=groups)


@bp.route('/group/<id>/')
@login_required
def group(id):
    return render_template('group.html')


@bp.route('/create/group/', methods=['POST'])
@login_required
def create_group():

    if request.method == 'POST':
        group_name = request.form.get('group_name')
        group_description = request.form.get('group_description')

        if not group_name:
            flash("Group Name is required!")
            return redirect(url_for('main.home'))

        user = current_user()

        try:
            Group.create(
                title=group_name,
                description=group_description,
                admin_user_id=user.id # type: ignore
            )
            flash(f"{group_name} create successful!", "success")

        except Exception as e:
            flash(f"Error: {e}", "error")

    return redirect(url_for('main.home'))


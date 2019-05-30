from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from spreadsheetcompiler.extensions import login_manager, db
from .. import models
import re

blueprint = Blueprint('users', __name__, url_prefix='/', static_folder='../static')


def role_required(required_roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in required_roles:
                flash("You do not have sufficient permissions to access that page.", "danger")
                if request.referrer != None:
                    return redirect(request.referrer)
                return redirect(url_for("users.login"))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


@blueprint.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == "uploader":
            return redirect(url_for("uploader.uploader"))
        elif current_user.role == "compiler":
            return redirect(url_for("compiler.compiler"))
        elif current_user.role == "manager":
            return redirect(url_for("compiler.compiler"))
    return render_template('home.html',
        current_user=current_user)


@blueprint.route('/login/', methods=['GET', 'POST'])
def login_post():
    if request.method == "GET": redirect(url_for('users.login'))
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = models.User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('users.login'))
    if user.active == False:
        flash('Sorry, but that user has been deactivated and cannot log in.')
        return redirect(url_for('users.login'))

    login_user(user, remember=remember)
    user_log = models.UserLog(user_id=user.id,
        action="Log in")
    db.session.add(user_log)
    db.session.commit()
    if user.role == "manager":
        return redirect(url_for('manager.manager'))
    elif user.role == "compiler":
        return redirect(url_for('compiler.compiler'))
    return redirect(url_for('uploader.uploader'))


@blueprint.route("/users/")
@login_required
@role_required(["compiler"])
def users():
    users = models.User.query.filter_by(active=True).all()
    usergroups = models.UserGroup.query.all()
    return render_template("users.html",
        users=users,
        usergroups=usergroups,
        current_user=current_user)


@blueprint.route("/users/usergroup/new/", methods=['GET', 'POST'])
@blueprint.route("/users/usergroup/edit/<usergroup_id>/", methods=['GET', 'POST'])
@login_required
@role_required(["compiler"])
def create_edit_usergroup(usergroup_id=None):
    if request.method == "GET":
        if usergroup_id is not None:
            usergroup = models.UserGroup.query.get(usergroup_id)
            return render_template("create_edit_usergroup.html",
                usergroup=usergroup,
                current_user=current_user)
        else:
            return render_template("create_edit_usergroup.html",
                current_user=current_user)

    name = request.form.get('name')
    if usergroup_id is not None:
        usergroup = models.UserGroup.query.get(usergroup_id)
        usergroup.name=name
        db.session.add(usergroup)
        db.session.commit()
        flash("Successfully edited user group!", "success")
        return redirect(url_for("users.users"))
    usergroup = models.UserGroup.query.filter_by(name=name).first()

    if usergroup:
        flash('This name already exists! User group names must be unique.')
        return redirect(url_for('users.create_edit_usergroup'))

    new_user_group = models.UserGroup(name=name)
    db.session.add(new_user_group)
    db.session.commit()
    flash("Successfully created user group!", "success")

    return redirect(url_for('users.users'))


@blueprint.route("/users/user/new/", methods=['GET', 'POST'])
@blueprint.route("/users/user/edit/<user_id>/", methods=['GET', 'POST'])
@login_required
@role_required(["compiler"])
def create_edit_user(user_id=None):
    if request.method == "GET":
        usergroups = models.UserGroup.query.all()
        if user_id is not None:
            user = models.User.query.get(user_id)
            return render_template("create_edit_user.html",
                usergroups=usergroups,
                user=user,
                current_user=current_user)
        else:
            return render_template("create_edit_user.html",
                usergroups=usergroups,
                current_user=current_user)

    usergroup_id = request.form.get('usergroup_id')
    if usergroup_id == "":
        usergroup_id = None
    else:
        usergroup_id = int(usergroup_id)

    user_form = {
        "email": request.form.get('email'),
        "username": request.form.get('username'),
        "usergroup_id": usergroup_id,
        "role": request.form.get('role')
    }
    password = request.form.get('password')
    valid_form = True
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_pattern, user_form.get("email")):
        flash('Please enter a valid email address')
        valid_form = False

    if (user_form.get("username") == ""):
        flash('Please enter a username.')
        valid_form = False

    if (user_form.get("role") == ""):
        flash('Please select a role.')
        valid_form = False

    if ((user_id == None) and (password == "")):
        flash('Please enter a password for this user.')
        valid_form = False

    if (user_form.get("role")=="uploader"):
        if (usergroup_id == None):
            flash("""User groups are required for uploaders. Please
                specify an existing user group, or create a new
                user group and try again.""")
            valid_form = False
        else:
            usergroup = models.UserGroup.query.get(usergroup_id)
            if not usergroup:
                flash("""Could not find that user group. User groups are
                required for uploaders. Please specify an existing user
                group, or create a new user group and try again.""")
                valid_form = False
            usergroup_id = usergroup.id
    else:
        usergroup_id = None

    user = models.User.query.filter_by(username=user_form.get("username")).first()
    if user:
        flash('This username already exists! Usernames must be unique.')
        valid_form = False

    user = models.User.query.filter_by(email=user_form.get("email")).first()
    if user:
        flash('This email address is already being used by another user! Email addresses must be unique.')
        valid_form = False

    if valid_form == False:
        usergroups = models.UserGroup.query.all()
        return render_template("create_edit_user.html",
                usergroups=usergroups,
                user=user_form,
                current_user=current_user)

    if user_id is not None: # edit
        user = models.User.query.get("user_id")
        user.email = user_form.get("email")
        user.username = user_form.get("username")
        user.usergroup_id = usergroup_id
        user.role = user_form.get("role")
        if password != "":
            user.password = generate_password_hash(password, method='sha256')
        db.session.add(user)
        db.session.commit()
        flash("Successfully edited user!", "success")
        return redirect(url_for("users.users"))

    new_user = models.User(email=user_form.get("email"),
        username=user_form.get("username"), role=user_form.get("role"),
        usergroup_id=user_form.get("usergroup_id"),
        password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    flash("Successfully created user!", "success")
    return redirect(url_for('users.users'))


@blueprint.route("/users/user/delete/<user_id>/", methods=['GET'])
@login_required
@role_required(["compiler"])
def delete_user(user_id):
    user = models.User.query.get(user_id)
    if not user:
        flash("Sorry, could not find that user. Perhaps they have already been deleted?")
        return(redirect(url_for('users.users')))
    elif user.id == current_user.id:
        flash("Sorry, you cannot delete your own user. Please ask another compiler to delete you.")
        return(redirect(url_for('users.users')))
    user.active = False
    db.session.add(user)
    db.session.commit()
    flash("Deleted that user.", "success")
    return redirect(url_for("users.users"))


@blueprint.route('/logout/')
@login_required
def logout():
    user_log = models.UserLog(user_id=current_user.id,
        action="Log out")
    db.session.add(user_log)
    db.session.commit()
    logout_user()
    flash(u'Logged out', 'success')
    redir_url = url_for("users.login")
    return redirect(redir_url)

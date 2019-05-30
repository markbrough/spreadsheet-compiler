from flask import abort, Blueprint, render_template, send_from_directory, \
jsonify, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import openpyxl
from io import BytesIO
import datetime

from spreadsheetcompiler.extensions import login_manager, db
from .. import models
from . import compiler
from .users import role_required

blueprint = Blueprint('uploader', __name__,
    url_prefix='/uploader/', static_folder='../static')


ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])
def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route("/")
@login_required
@role_required(["uploader"])
def uploader():
    return render_template("uploader.html",
        current_user=current_user,
        compilation=compiler.active_compilation())


def handle_upload(file, submission_name, type):
    if file.filename == '':
        flash('Please select a file.', "warning")
        return redirect(url_for('uploader.uploader'))
    if file and allowed_file(file.filename):
        uid = uuid.uuid4()
        filename = "{}-{}".format(uid.hex, secure_filename(file.filename))
        current_compilation = compiler.active_compilation()
        wb = openpyxl.load_workbook(BytesIO(file.stream.read()))
        if (type=="submission") and (not current_user.usergroup.name in wb.sheetnames):
            flash("""Your submission file does not contain the sheet name {}, which is
                required. Did you upload the correct file? If you want to submit this
                file as a supplementary file, use the form at the bottom of
                that page ("Upload supplementary file").""".format(current_user.usergroup.name))
            return redirect(url_for('uploader.uploader'))
        fileobj = models.UploadedFile(
            user_id=current_user.id,
            filename=filename,
            type=type,
            name=submission_name,
            compilation_id=current_compilation.id,
            created_date=datetime.datetime.now()
            )
        db.session.add(fileobj)
        db.session.commit()
        wb.save(os.path.join(current_app.config['UPLOAD_FOLDER'], "source", filename))

        user_log = models.UserLog(user_id=current_user.id,
            action="Upload a new {} file: {}".format(type, submission_name))
        db.session.add(user_log)
        db.session.commit()
        flash("Uploaded!", "success")
        return redirect(url_for('uploader.uploader'))

    flash("Please upload an Excel file in the template format.")
    return redirect(url_for('uploader.uploader'))


@blueprint.route("/delete_file/<file_id>/", methods=['GET'])
@login_required
@role_required(["uploader"])
def delete_file(file_id):
    file = models.UploadedFile.query.get(file_id)
    if file and file.user_id == current_user.id:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], "source", file.filename))
        except FileNotFoundError:
            pass # If we don't find in the file system, we delete silently from the DB anyway.
        user_log = models.UserLog(user_id=current_user.id,
            action="Deleted a {} file: {}".format(file.type, file.name))
        db.session.add(user_log)
        db.session.delete(file)
        db.session.commit()
        flash("File deleted.", "success")
        return(redirect(url_for('uploader.uploader')))
    else:
        flash("Could not delete that file - are you sure it belongs to you?")
        return(redirect(url_for('uploader.uploader')))


@blueprint.route("/submission_post/", methods=['GET', 'POST'])
@login_required
@role_required(["uploader"])
def submission_post():
    if (request.method == "GET") or ('file' not in request.files):
        flash("You must upload a file!")
        return redirect(url_for('uploader.uploader'))

    file = request.files['file']
    name = request.form.get('name', 'Submission')
    type = "submission"
    return handle_upload(file, name, type)


@blueprint.route("/supplementary_post/", methods=['GET', 'POST'])
@login_required
@role_required(["uploader"])
def supplementary_post():
    if (request.method == "GET") or ('file' not in request.files):
        flash("You must upload a file!")
        return redirect(url_for('uploader.uploader'))

    file = request.files['file']
    name = request.form.get('name')
    type = "supplementary"
    return handle_upload(file, name, type)

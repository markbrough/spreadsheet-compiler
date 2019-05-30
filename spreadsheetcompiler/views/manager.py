from flask import abort, Blueprint, render_template, send_from_directory, \
jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user

from .. import models
from . import compiler
from .users import role_required
import datetime


blueprint = Blueprint('manager', __name__,
    url_prefix='/manager/', 
    static_folder='../static')


@blueprint.route("/")
@login_required
@role_required(["manager", "compiler"])
def manager():
    if request.args.get('compilation_id'):
        compilation = models.Compilation.query.get(request.args.get('compilation_id'))
    else:
        compilation = compiler.most_recent_finalised_compilation()
    compilations = models.Compilation.query.filter(
            datetime.datetime.now() > models.Compilation.final_deadline
        ).order_by(
        models.Compilation.id.desc()).all()
    return render_template("manager.html",
        compilations=compilations,
        compilation = compilation,
        current_user=current_user)

from flask import current_app, render_template
from flask_login import UserMixin
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from .extensions import db
import datetime
from collections import defaultdict


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.UnicodeText, unique=True,
        nullable=False)
    usergroup_id = db.Column(db.Integer,
        db.ForeignKey('usergroups.id'),
        nullable=True) # does not have to have a user group
    usergroup = sa.orm.relationship("UserGroup")
    email = db.Column(db.UnicodeText, unique=True,
        nullable=False)
    password = db.Column(db.UnicodeText,
        nullable=False)
    role = db.Column(db.Enum('uploader', 'compiler', 'manager'),
        nullable=False)
    active = db.Column(db.Boolean,
        nullable=False,
        default=True)
    uploadedfiles = sa.orm.relationship("UploadedFile")


class UserLog(db.Model):
    __tablename__ = 'userlog'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('users.id'),
        nullable=True)
    user = sa.orm.relationship("User")
    log_date_time = db.Column(db.DateTime,
        nullable=False,
        default=datetime.datetime.now())
    action = db.Column(db.UnicodeText, 
        nullable=False)


class UserGroup(db.Model):
    __tablename__ = 'usergroups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, unique=True,
        nullable=False)
    users_uploadedfiles = sa.orm.relationship("UploadedFile",
        secondary="users",
        secondaryjoin="User.id==UploadedFile.user_id") 


def onDay(day, start_end="end", before=None):
    # Monday = 0
    if start_end == "end":
        date = datetime.datetime.now()
        the_date = date + datetime.timedelta(days=(day-date.weekday()+7)%7)
        the_date = the_date.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1,microseconds=-1)
        if before and the_date > before:
            onDay(day, "start")
    elif start_end=="start":
        date = datetime.datetime.now()
        the_date = date + datetime.timedelta(days=(day-date.weekday()))
        the_date = the_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return the_date


class FileOnTime(object):
    def __init__(self, type):
        self.type = type

    def t_satisfies_type(self, t, compilation):
        if self.type == "draft":
            return t.submission_by_draft
        if self.type == "final":
            return t.submission_by_final
        return False

    def __get__(self, obj, type=None):
        return [t for t in obj.files if self.t_satisfies_type(t, obj)]


class TypeOfFile(object):
    def __init__(self, type):
        self.type = type

    def __get__(self, obj, type=None):
        return [t for t in obj.files if t.type==self.type]


class Compilation(db.Model):
    __tablename__ = 'compilations'
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, 
        nullable=False,
        default=onDay(0, start_end="start"))
    draft_deadline = db.Column(db.DateTime, 
        nullable=False,
        default=onDay(3, start_end="end", before=onDay(6)))
    @property
    def draft_deadline_text(self):
        return self.draft_deadline.date().isoformat()
    final_deadline = db.Column(db.DateTime, 
        nullable=False,
        default=onDay(6, start_end="end"))
    @property
    def final_deadline_text(self):
        return self.final_deadline.date().isoformat()
    templatefile_id = db.Column(db.Integer,
        db.ForeignKey('templatefiles.id'),
        default = db.select([db.func.max(None,
            db.func.max("models.TemplateFile.id"))]),
        )
    templatefile = sa.orm.relationship("TemplateFile")
    files = sa.orm.relationship("UploadedFile")
    before_draft = FileOnTime("draft")
    before_final = FileOnTime("final")
    supplementary_files = TypeOfFile("supplementary")

    @hybrid_property
    def status(self):
        if datetime.datetime.now() > self.draft_deadline:
            return "final"
        return "draft"

    @hybrid_property
    def sheets(self):
        list_draft = list(map(lambda d: d.user.usergroup.name, self.before_draft))
        list_final = list(map(lambda d: d.user.usergroup.name, self.before_final))
        files_by_usergroup = defaultdict(dict)
        for file in self.before_final:
            files_by_usergroup[file.user.usergroup.name][file.id] = file

        sheets = [sheet for sheet in self.templatefile.sheets if sheet.usergroup]
        
        for sheet in sheets:
            sheet.draft = False
            sheet.final = False
            if sheet.name in list_draft:
                sheet.draft = True
            if sheet.name in list_final:
                sheet.final = True
            if sheet.name in files_by_usergroup:
                sheet.file = files_by_usergroup[sheet.name][max(files_by_usergroup[sheet.name])]
        return sheets

    """
    files = sa.orm.relationship("UploadedFile",
        primaryjoin="and_(Compilation.created_date < UploadedFile.created_date, "
            "Compilation.final_deadline > UploadedFile.created_date)",
        foreign_keys=[created_date, final_deadline],
        backref="compilation",
        uselist=True,
        viewonly=True)
    """


class TemplateFile(db.Model):
    __tablename__ = 'templatefiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('users.id'),
        nullable=False)
    created_date = db.Column(db.DateTime, 
        nullable=False,
        default=datetime.datetime.utcnow())
    active = db.Column(db.Boolean,
        nullable=False,
        default=True)
    sheets = sa.orm.relationship("TemplateFileSheet")


class TemplateFileSheet(db.Model):
    __tablename__ = 'templatefilesheets'
    id = db.Column(db.Integer, primary_key=True)
    templatefile_id = db.Column(db.Integer,
        db.ForeignKey('templatefiles.id'),
        nullable=False)
    name = db.Column(db.UnicodeText,
        nullable=False)
    sheet_number = db.Column(db.Integer,
        nullable=False)
    usergroup = sa.orm.relationship("UserGroup",
        primaryjoin="TemplateFileSheet.name==UserGroup.name",
        foreign_keys=name)


class UploadedFile(db.Model):
    __tablename__ = 'uploadedfiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('users.id'),
        nullable=False)
    user = sa.orm.relationship("User")
    compilation_id = db.Column(db.Integer,
        db.ForeignKey('compilations.id'),
        nullable=False)
    compilation = sa.orm.relationship("Compilation")
    created_date = db.Column(db.DateTime, 
        nullable=False,
        default=datetime.datetime.utcnow())
    @property
    def created_date_formatted(self): 
        _the_d = self.created_date.isoformat()
        return "{} {}".format(_the_d[0:10], _the_d[11:16])
    filename = db.Column(db.UnicodeText,
        nullable=False)
    name = db.Column(db.UnicodeText,
        nullable=False)
    type = db.Column(db.Enum('submission', 'supplementary'),
        nullable=False)

    @hybrid_property
    def submission_by_draft(self):
        if ((self.type == "submission") and (self.compilation.created_date < self.created_date) and 
            (self.compilation.draft_deadline > self.created_date)):
            return True
        return False

    @hybrid_property
    def submission_by_final(self):
        if ((self.type == "submission") and (self.compilation.created_date < self.created_date) and 
            (self.compilation.final_deadline > self.created_date)):
            return True
        return False

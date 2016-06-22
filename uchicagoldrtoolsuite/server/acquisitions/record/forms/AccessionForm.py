from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.fields.simple import TextAreaField
from wtforms.fields.core import SelectField, BooleanField


class AccessionForm(Form):
    materialtype = StringField("Type", validators=[DataRequired])
    rights = StringField("Rights", validators=[DataRequired])
    prc = StringField("PRC", validators=[DataRequired])
    filesStaged = StringField("Date Files Were Staged")
    filesReceived = StringField(
        "Date Files Were Received")
    access = BooleanField(
        "Should The Public Have Access to These Files?")
    discover = BooleanField(
        "Should the Public Be Able to Discover these Files?")
from flask_wtf import Form
from wtforms import Form as WTForm, StringField
from wtforms.validators import DataRequired
from wtforms.fields.simple import TextAreaField
from wtforms.fields.core import SelectField, BooleanField

class AccessionForm(Form):
    collection = SelectField(
        "Formal Collection To Which This Accession Belongs",
        validators=[DataRequired],
        choices=[('A','A'),
                 ('B','B')])
    span_date = StringField("Year Range")
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


from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class AcquisitionForm(Form):
    accessionID = StringField("accession ID", validators=[DataRequired])
    
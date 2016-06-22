
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.fields.simple import TextAreaField
from wtforms.fields.core import SelectField, BooleanField

class AcquisitionForm(Form):
    accessionID = StringField("Accession Identifier", 
                              validators=[DataRequired])
    donorfirstname = StringField("Donor's first name", 
                                 validators=[DataRequired])
    donorlastname = StringField("Donor's last name", 
                                validators=[DataRequired])
    donoremail = StringField("Donor's email address", 
                             validators=[DataRequired])
    donorphonenumber = StringField("Donor's phone number", 
                                   validators=[DataRequired])
    sourcefirstname = StringField("Source's first name", 
                                  validators=[DataRequired])
    sourcelastname = StringField("Source's last name", 
                                 validators=[DataRequired])
    sourceemail = StringField("Source's email address", 
                              validators=[DataRequired])
    sourcephonenumber = StringField("Source's phone number", 
                                    validators=[DataRequired])
    summary = TextAreaField("Description", validators=[DataRequired])
    restriction = SelectField("Restriction", validators=[DataRequired], 
                              choices=[('R-X', 'R-X'), 
                                       ('R-30', 'R-30'),
                                       ('OU', 'OU'),
                                       ('O','O')])
    restrictionComment = TextAreaField("Comment about Restriction", 
                                       validators=[DataRequired])
    adminComment = TextAreaField(
        "Administrative Comment")
    physicalMediaNote = TextAreaField(
        "Note about the physical Media")
    physicalLocationNote = TextAreaField(
        "Note about the physical location")
    receiptLetterSent = BooleanField(
        "Was a letter of receipt sent?")
    invLetterSent = BooleanField(
        "Is an inventory letter required?")
    giftAcknowledgementRequired = BooleanField(
        "Is a gift acknowledgement required?")
    giftAcknowledgementReceived = BooleanField(
        "Was a gift acknowledgement received?")
    

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.fields.simple import TextAreaField
from wtforms.fields.core import SelectField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

def possible_restrictions():
    from ..models.Restriction import db, Restriction
    output = db.session.query(Restriction)    
    return [(x.restrictionCode, x.restrictionCode) for x in output]

class PersonForm(Form):
    firstname = StringField("First name", 
                                 validators=[DataRequired])
    lastname = StringField("Last name", 
                                validators=[DataRequired])
    email = StringField("Email address", 
                             validators=[DataRequired])
    phonenumber = StringField("Phone number", 
                              validators=[DataRequired])    

class AcquisitionForm(Form):
    accessionID = StringField("Accession Identifier", 
                              validators=[DataRequired])
    collection = StringField("Collection that this belongs in", validators=[DataRequired])
    donor = PersonForm("Donor")
    source = PersonForm("Source")
    sourcephonenumber = StringField("Source's phone number", 
                                    validators=[DataRequired])
    summary = TextAreaField("Description", validators=[DataRequired])
    
    restriction = SelectField('Restriction Code', 
                                   choices=possible_restrictions(),
                                   validators=[DataRequired])
    
    restrictionComment = TextAreaField("Comment about Restriction", 
                                       validators=[DataRequired])
    adminComment = TextAreaField(
        "Administrative Comment")
    physicalMediaNote = TextAreaField(
        "Note about the physical Media")
    physicalLocationNote = TextAreaField(
        "Note about the physical location")
    acquisitionType = BooleanField("Is this acquisition all digital?")
    receiptLetterSent = BooleanField(
        "Was a letter of receipt sent?")
    invLetterSent = BooleanField(
        "Is an inventory letter required?")
    giftAcknowledgementRequired = BooleanField(
        "Is a gift acknowledgement required?")
    giftAcknowledgementReceived = BooleanField(
        "Was a gift acknowledgement received?")
    
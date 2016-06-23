
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.fields.simple import TextAreaField
from wtforms.fields.core import SelectField, BooleanField
from wtforms import Form as WTForm
from wtforms.fields import FormField
from wtforms.ext.sqlalchemy.fields import QuerySelectField


def possible_restrictions():
    from ..models.Restriction import db, Restriction
    output = db.session.query(Restriction)    
    return [(x.restrictionCode, x.restrictionCode) for x in output]

class PhysicalMediaFields(WTForm):
    label = StringField("Descriptive Term", validators=[DataRequired])
    number = StringField("Amount", validators=[DataRequired])

class DonorFields(WTForm):
    donor_firstname = StringField("First name", 
                                 validators=[DataRequired])
    donor_lastname = StringField("Last name", 
                                validators=[DataRequired])
    donor_email = StringField("Email address", 
                             validators=[DataRequired])
    donor_phonenumber = StringField("Phone number", 
                              validators=[DataRequired])    

class SourceFields(WTForm):
    source_firstname = StringField("First name", 
                                 validators=[DataRequired])
    source_lastname = StringField("Last name", 
                                validators=[DataRequired])
    source_email = StringField("Email address", 
                             validators=[DataRequired])
    source_phonenumber = StringField("Phone number", 
                              validators=[DataRequired])    
    
  
class OriginFields(WTForm):
    description = StringField("Description of the origin")
    
    
class RestrictionFields(WTForm):
    restriction = SelectField('Restriction Code', 
                                   choices=possible_restrictions(),
                                   validators=[DataRequired])
    
    restrictionComment = TextAreaField("Comment about Restriction", 
                                       validators=[DataRequired])
    
class AcquisitionForm(Form):
    accessionID = StringField("Accession Identifier", 
                              validators=[DataRequired])
    summary = TextAreaField("Description", validators=[DataRequired])
    adminComment = TextAreaField(
        "Administrative Comment")
    receiptLetterSent = BooleanField(
        "Was a letter of receipt sent?")
    invLetterSent = BooleanField(
        "Is an inventory letter required?")
    giftAcknowledgementRequired = BooleanField(
        "Is a gift acknowledgement required?")
    giftAcknowledgementReceived = BooleanField(
        "Was a gift acknowledgement received?")
    acquisitionType = BooleanField("Is this acquisition all digital?")

    physicalLocationNote = TextAreaField(
        "Note about the physical location")

    collection = StringField("Collection that this belongs in", validators=[DataRequired])
    donor = FormField(DonorFields)
    source = FormField(SourceFields)
    origin = FormField(OriginFields)
    
    restrictions = FormField(RestrictionFields)

    physical_media_info = FormField(PhysicalMediaFields)


    
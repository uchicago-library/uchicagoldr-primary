
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.fields.simple import TextAreaField
from wtforms.fields.core import SelectField, BooleanField, IntegerFeild
from wtforms.fields import FormField
from wtforms import Form as WTForm

class DonorSourceInfoFields(WTForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    address = StringField("Address")
    phone = StringField("Phone Number")
    email = StringField("Email")

class PhysicalMediaFields(WTForm):
    quantity = IntegerField("Quantity")
    description = StringField("Description")

class AcquisitionForm(Form):
    accessionID = StringField("Accession Identifier",
                              validators=[DataRequired])
    donor = FormField(DonorSourceInfoFields)
    source = FormField(DonorSourceInfoFields)
    summary = TextAreaField("Description", validators=[DataRequired])
    restriction = SelectField("Restriction", validators=[DataRequired],
                              choices=[('R-X', 'R-X'),
                                       ('R-30', 'R-30'),
                                       ('OU', 'OU'),
                                       ('O','O')])
    restrictionComment = TextAreaField("Comment about Restriction")
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

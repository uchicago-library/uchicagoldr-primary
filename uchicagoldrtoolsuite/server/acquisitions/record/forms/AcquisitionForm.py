
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.fields.simple import TextAreaField
from wtforms.fields.core import SelectField, BooleanField, IntegerField
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

class RestrictionFields(WTForm):
    restriction = SelectField("Restriction", validators=[DataRequired],
                              choices=[('R-X', 'R-X'),
                                       ('R-30', 'R-30'),
                                       ('OU', 'OU'),
                                       ('O','O')])
    restriction_comment = TextAreaField("Restriction Comment")

class AcquisitionForm(Form):
    accessionID = StringField("Accession Identifier",
                              validators=[DataRequired])
    summary = TextAreaField("Description", validators=[DataRequired])
    restriction_information = FormField(RestrictionFields)
    donor = FormField(DonorSourceInfoFields)
    source = FormField(DonorSourceInfoFields)
    adminComment = TextAreaField("Administrative Comment")
    physical_media_information = FormField(PhysicalMediaFields)
    acquisitionType = BooleanField("Is this acquisition all digital?")
    giftAcknowledgementRequired = BooleanField(
        "Is a gift acknowledgement required?")
    giftAcknowledgementReceived = BooleanField(
        "Was a gift acknowledgement received?")

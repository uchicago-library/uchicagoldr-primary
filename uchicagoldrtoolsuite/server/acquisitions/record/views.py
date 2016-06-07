
from flask import Blueprint

blueprint = Blueprint('records', __name__, 
                      template_folder='templates')

@blueprint.route('/')
def frontpage():
    return str("hello, this is the front page of " + 
            "the acquisitions record application")
    
    
@blueprint.route('/record/chooseType', methods=['GET'])
def chooseTypeForNewRecord():
    # select the option to start a physical accession turned digital
    # or born digital acquisition record
    return "choose the type for the new record"

@blueprint.route('/record/makeNew', methods=['GET', 'POST'])
def makeANewRecord():
    # end point for student workers to fill out an acquisition
    # record for the DAS to review and convert to an accession
    # record
    return "make a new record by filling out the form"

@blueprint.route('/records/list')
def listRecords():
    # end point for DAS to view all acquisitions records 
    # whether converted to accession records or not
    return "view all acquisitions records in the system end point"

@blueprint.route('/record/convertToAccession', methods=['GET', 'POST'])
def convertRecordToAccession():
    # end point for the DAS to modify the acqusition record 
    # submitted by a student worker and convert modified record 
    # into an accession record 
    return str("DAS form to modify and convert " + 
               "acquisition record into an accession record")
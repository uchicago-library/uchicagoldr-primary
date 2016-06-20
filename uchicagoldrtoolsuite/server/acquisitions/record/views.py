
from flask import Blueprint
from flask.templating import render_template

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


acquisition = Blueprint('records', __name__, 
                      template_folder='templates')

@acquisition.route('/')
def frontpage():
    return render_template('index.html')

@acquisition.route('/record/chooseType', methods=['GET', 'POST'])
def chooseTypeForNewRecord():
    # select the option to start a physical accession turned digital
    # or born digital acquisition record

    return render_template('choose.html')

@acquisition.route('/record/makeNew', methods=['GET', 'POST'])
def makeANewRecord():
    # end point for student workers to fill out an acquisition
    # record for the DAS to review and convert to an accession
    # record
    return "make a new record by filling out the form"

@acquisition.route('/records/list')
def listRecords():
    # end point for DAS to view all acquisitions records 
    # whether converted to accession records or not
    return "view all acquisitions records in the system end point"

@acquisition.route('/record/convertToAccession', methods=['GET', 'POST'])
def convertRecordToAccession():
    # end point for the DAS to modify the acquisition record 
    # submitted by a student worker and convert modified record 
    # into an accession record 
    return str("DAS form to modify and convert " + 
               "acquisition record into an accession record")
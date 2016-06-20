
from flask import Blueprint, request
from flask.templating import render_template
from .config import SECRET_KEY

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


acquisition = Blueprint('records', __name__, 
                      template_folder='../templates')

@acquisition.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = SECRET_KEY
    return session['_csrf_token']

@acquisition.route('/')
def frontpage():
    return render_template('front.html')

@acquisition.route('/acquisition', methods=['GET', 'POST'])
def makeANewRecord():
    from .forms.AcquisitionForm import AcquisitionForm
    # end point for student workers to fill out an acquisition
    # record for the DAS to review and convert to an accession
    # record
    form = AcquisitionForm()
    return render_template('record.html', recordform=new) 

@acquisition.route('/list')
def listRecords():
    from .controllers.acquisitionretriever import AcquisitionRetriever
    retriever = AcquisitionRetriever.run_browse()
    return render_template('list.html', result=retriever.result)
    return "view all acquisitions records in the system end point"

@acquisition.route('/record/convertToAccession', methods=['GET', 'POST'])
def convertRecordToAccession():
    # end point for the DAS to modify the acquisition record 
    # submitted by a student worker and convert modified record 
    # into an accession record 
    return str("DAS form to modify and convert " + 
               "acquisition record into an accession record")
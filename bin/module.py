
from uchicagoldr.output import Output
from uchicagoldr.batch import StagingDirectory

if __name__ == "__main__":
    final_output = Output('a_type','a_preferred_output_format')
    directory_to_stage = StagingDirectory("/a/full/path/to/files/that/need/to/be/staged",
                                          "/a/full/path/to")
    final_output = directory_to_stage.validate(final_output)
    if final_output.get_requests():
        requests_satisfied = []
        for request in final_output.get_requests():
            # get user input
        if not len(requests_satisfied) == final_output.get_requests()):
            # need to do more work
    final_output = directory_to_stage.ingest(final_output)
    if final_output.get_requests():
        requests_satisifed = []
        for request in final_output.get_requets():
            # get user input
        if not len(requests_satisfied) == final_output.get_requests()):
            # need to do more work            
    final_output = directory_to_stage.audit(final_output)
    if final_output.get_requests():
        requests_satisfied = []
        for request in final_output.get_requets():
            # get user input
        if not len(requests_satisfied) == final_output.get_requests()):
            # need to do more work            
            
    if final_output.get_status():
        final_output.display()
    else:
        stderr.write("The following errors occured")
        stderr.write(str(final_output.get_errors()))
    

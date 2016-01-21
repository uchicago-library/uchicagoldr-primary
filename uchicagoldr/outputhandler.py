from uchicagoldr.output import Outport

class OutputHandler(object)

    kind = 'Abstract base class'

    def __init__(self, output_instance):
        assert(isinstance(output_instance, Output))
        self.output_instance = output_instance

    def display_data(self):
        raise NotImplemented

    def handle_requests(self):
        raise NotImplemented

    def handle_errors(self):
        raise NotImplemented

    def _display_data_str(self):
        raise NotImplemented

    def _display_data_item(self):
        raise NotImplemented

    def _display_data_batch(self):
        raise NotImplemented

    def _display_data_family(self):
        raise NotImplemented

    def _handle_request_true_or_false(self):
        raise NotImplemented

    def _handle_request_input(self):
        raise NotImplemented

    def _handle_request_choose_between(self):
        raise NotImplemented

    def _handle_request_confirm(self):
        raise NotImplemented

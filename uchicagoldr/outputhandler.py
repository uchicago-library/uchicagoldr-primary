from uchicagoldr.output import Outport

class Displayer(object):
    def __init__(self, kind):
	self.class_being_displayed = kind

    def display():
	if self.class_being_displayed == 'family':
		return NotImplemented
	if self.class_being_displayed == 'directory':
		return NotImplemented
	if self.class_being_displayed == 'string':
		return NotImplemented
	if self.class_being_displayed == 'item':
		return NotImplemented
	if self.class_being_displayed == 'accessionitem':
		return NotImplemented
    

class OutputHandler(object)

    kind = 'Abstract base class'

    def __init__(self, output_instance):
        assert(isinstance(output_instance, Output))
        self.output_instance = output_instance
	displayer = Display(output_instance.type)

    def display_data(self):
        return displayer.display()

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

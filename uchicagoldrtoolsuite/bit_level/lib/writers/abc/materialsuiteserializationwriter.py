from abc import ABCMeta, abstractmethod
from logging import getLogger

from pypremis.nodes import Event, EventOutcomeInformation, EventOutcomeDetail

from uchicagoldrtoolsuite import log_aware
from .abc.serializationwriter import SerializationWriter
from ...structures.materialsuite import MaterialSuite


log = getLogger(__name__)


class MaterialSuiteSerializationWriter(SerializationWriter, metaclass=ABCMeta):
    @abstractmethod
    @log_aware(log)
    def __init__(self, struct, root, update_content_location=False,
                 premis_event=None, eq_detect="bytes"):
        log.debug("Entering the ABC init")
        super().__init__(struct, root, eq_detect=eq_detect)
        self._update_content_location = update_content_location
        self._premis_event = premis_event
        log.debug("Exiting the ABC init")

    @log_aware(log)
    def set_struct(self, struct):
        if not isinstance(struct, MaterialSuite):
            raise ValueError(
                "{} is a {}, not a {}".format(
                    str(struct), str(type(struct)), str(MaterialSuite)
                )
            )
        self._struct = struct

    def get_update_content_location(self):
        return self._update_content_location

    def set_update_content_location(self, x):
        self._update_content_location = bool(x)

    def get_premis_event(self):
        return self._premis_event

    def set_premis_event(self, x):
        if not (isinstance(x, Event) or isinstance(x, None)):
            raise TypeError(
                "{} is a {}, not a {} or None".format(
                    str(x), str(type(x)), str(Event)
                )
            )
        self._premis_event = x

    def content_location_update(self, premis_rec, loc):
        log.debug("Updating PREMIS contentLocation field")
        premis_rec.get_object_list()[0].\
            get_storage()[0].get_contentLocation().set_contentLocationValue(
                loc
            )

    def finalize_event(self, premis, e, eventOutcomeDetailNote=None):
        eventOutcomeInformation = EventOutcomeInformation(
            eventOutcome="SUCCESS"
        )
        if eventOutcomeDetailNote:
            eventOutcomeDetail = EventOutcomeDetail(
                eventOutcomeDetailNote=str(eventOutcomeDetailNote)
            )
            eventOutcomeInformation.add_eventOutcomeDetail(eventOutcomeDetail)
        e.add_eventOutcomeInformation(eventOutcomeInformation)
        premis.add_event(e)

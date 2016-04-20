
class MaterialSuitePackager(Packager):

    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod(self):
    def get_techmod(self):
        pass

    @abstractmethod
    def get_presform(self):
        pass

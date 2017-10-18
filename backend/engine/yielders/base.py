
class BaseYielder:
    """Base class to create yielders. The yielders are an specific type of Generator

    To call start_message() the instance must have a self.config_data attribute"""

    def has_start_message(self):
        return True

    def start_message(self):
        return "event: config\ndata: {}\n\n".format(self.config_data)

    def generate(self):
        """Abstract method."""
        raise("Abstract method BaseYielder.generate()")

class BaseProcessor:
    """Base class to make processors. The Processors are an specific type of Generators.

    To call start_message() the instance must have a self.generator attribute (which is a generator)."""

    def start_message(self):
        return self.generator.start_message()

    def generate(self):
        """Abstract method."""
        raise("Abstract method BaseProcessor.generate()")

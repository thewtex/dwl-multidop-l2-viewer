# make sure files are there
class ExtensionError(Exception):
    """Exception raised if a file does not have the expected extension."""

    def __init__(self, filename, extension):
        self.filename = filename
        self.extension = extension

    def __str__(self):
        return 'the file prefix, %s, does not exist or have the anticipated extension, %s' % (self.filename, self.extension)

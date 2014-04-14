import os

from file_generator import FileGenerator


class IdenticalFileGenerator(FileGenerator):
    """Generate files that have the same content"""

    def __init__(self, size, **kwargs):
        super(IdenticalFileGenerator, self).__init__(**kwargs)
        self.content = os.urandom(size)

    def make_file(self, **kwargs):
        kwargs['is_binary'] = True
        return super(IdenticalFileGenerator, self).make_file(**kwargs)

    def generate_file_content(self, **kwargs):
        return self.content

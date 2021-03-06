import os

from file_generator import FileGenerator


class IdenticalFileGenerator(FileGenerator):
    """Generate files that have the same content"""

    def __init__(self, size, **kwargs):
        super(IdenticalFileGenerator, self).__init__(**kwargs)
        self.content = os.urandom(size)

    def make_file(self, **kwargs):
        kwargs['is_binary'] = True
        # ignore size param because size is already fixed in __init__()
        if 'size' in kwargs:
            kwargs.pop('size')
        return super(IdenticalFileGenerator, self).make_file(size=0, **kwargs)

    def generate_file_content(self, size, **kwargs):
        # param size is omitted here
        return self.content

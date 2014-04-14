import os

from file_generator import FileGenerator


class RandomFileGenerator(FileGenerator):
    def __init__(self, **kwargs):
        super(RandomFileGenerator, self).__init__(**kwargs)

    def make_file(self, **kwargs):
        kwargs['is_binary'] = True
        return super(RandomFileGenerator, self).make_file(**kwargs)

    def generate_file_content(self, size, **kwargs):
        return os.urandom(size)


import os

from file_generator import FileGenerator


class RandomFileGenerator(FileGenerator):
    def __init__(self, directory, prefix='', suffix='', filename_length=10):
        super(RandomFileGenerator, self).__init__(directory=directory,
                                                  prefix=prefix,
                                                  suffix=suffix)

    def make_file(self, size, filename=None, filename_length=10, **kwargs):
        super(RandomFileGenerator, self).make_file(size=size,
                                                   filename=filename,
                                                   filename_length=filename_length,
                                                   is_binary=True,
                                                   **kwargs)

    def generate_file_content(self, size, **kwargs):
        return os.urandom(size)


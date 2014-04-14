import os

from file_generator import FileGenerator


class SparseFileGenerator(FileGenerator):
    def __init__(self, **kwargs):
        super(SparseFileGenerator, self).__init__(**kwargs)

    def make_file(self, repeat_str, **kwargs):
        kwargs['is_binary'] = False
        # repeat_char to be passed to generate_file_content:
        kwargs['repeat_str'] = repeat_str
        return super(SparseFileGenerator, self).make_file(**kwargs)

    def generate_file_content(self, size, **kwargs):
        repeat_string = kwargs['repeat_str']
        if len(repeat_string) > size:
            raise AttributeError(
                "The length of repeat_str({}) is bigger than size({})".format(
                    len(repeat_string), size))
        content = str(repeat_string) * (size/len(repeat_string))
        if len(content) < size:
            content += repeat_string[:(size - len(content))]
        return content

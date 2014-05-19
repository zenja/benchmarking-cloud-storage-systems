import os

from file_generator import FileGenerator


class DeltaFileGenerator(FileGenerator):
    def __init__(self, size, percent, **kwargs):
        super(DeltaFileGenerator, self).__init__(**kwargs)
        self.size = int(size)
        self.percent = float(percent)
        if self.percent < 0 or self.percent > 1:
            print percent
            raise ValueError('percent should be in [0, 1]')
        if self.size <= 0:
            raise ValueError('size should be greater than 0')
        self.fixed_content = os.urandom(int(self.size*self.percent))

    def make_file(self, **kwargs):
        kwargs['is_binary'] = True
        # ignore size param because size is already fixed in __init__()
        if 'size' in kwargs:
            kwargs.pop('size')
        return super(DeltaFileGenerator, self).make_file(size=0, **kwargs)

    def generate_file_content(self, size, **kwargs):
        return self.fixed_content + os.urandom(int(self.size*(1-self.percent)))


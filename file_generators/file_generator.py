import os
import tempfile


class FileGenerator(object):
    def __init__(self, directory=None, prefix='', suffix='', delete=False):
        """ Constructor of FileGenerator

        Args:
            directory: the directory for saving generated files
            prefix: the prefix of the filename for generated files
            suffix: the suffix of the filename for generated files
            delete: whether to delete the temp files on file close or not
        """
        if (directory is not None) and not os.path.isdir(directory):
            raise AttributeError("{} is not a valid directory.".format(directory))
        self.directory = directory
        self.prefix = prefix
        self.suffix = suffix
        self.delete = delete

    def make_file(self, size, filename=None, is_binary=True, **kwargs):
        """make a file

        Args:
            size: file size in bytes
            others omitted

        Return:
            the file object of the created file (not closed)
        """
        content = self.generate_file_content(size=size, **kwargs)
        if is_binary:
            mode = 'wb'
        else:
            mode = 'w'
        if self.directory:
            tmp_file = tempfile.NamedTemporaryFile(mode=mode,
                                                   prefix=self.prefix,
                                                   suffix=self.suffix,
                                                   dir=self.directory,
                                                   delete=self.delete)
        else:
            tmp_file = tempfile.NamedTemporaryFile(mode=mode,
                                                   prefix=self.prefix,
                                                   suffix=self.suffix,
                                                   delete=self.delete)
        tmp_file.write(content)
        tmp_file.flush()
        return tmp_file

    def generate_file_content(self, size, **kwargs):
        raise NotImplementedError()

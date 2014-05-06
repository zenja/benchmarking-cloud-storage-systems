import shutil

from driver import Driver


class LocalFSDriver(Driver):
    """Driver for local file system"""
    def __init__(self):
        super(LocalFSDriver, self).__init__()

    def connect(self, include_guest=False):
        pass

    def acquire_access_token(self, guest=False):
        pass

    def upload(self, local_filename, remote_filename):
        shutil.copyfile(src=local_filename, dst=remote_filename)

    def download(self, remote_filename, local_filename):
        shutil.copyfile(src=remote_filename, dst=local_filename)

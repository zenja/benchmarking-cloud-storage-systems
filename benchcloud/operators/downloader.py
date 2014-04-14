import os

from drivers import driver
from file_utils import file_util


class Downloader(object):
    def __init__(self, server_driver):
        """Init a Uploader object

        Args:
            server_driver: a driver already connected to cloud service
        """
        if not issubclass(driver.Driver, driver.Driver):
            raise TypeError('Driver should be a subclass of drivers.driver.Driver')
        self.driver = server_driver

    def download(self, remote_filename, local_filename=None, local_dir=None):
        if local_filename is None and local_dir is None:
            raise AttributeError('Need at least one of local_filename or local_dir.')
        if local_dir:
            local_filename = os.path.join(local_dir, file_util.path_leaf(remote_filename))
        self.driver.download(local_filename=local_filename,
                             remote_filename=remote_filename)

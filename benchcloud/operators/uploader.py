import os
import ntpath

from benchcloud.drivers import driver


class Uploader(object):
    def __init__(self, server_driver):
        """Init a Uploader object

        Args:
            server_driver: a driver already connected to cloud service
        """
        if not issubclass(driver.Driver, driver.Driver):
            raise TypeError('Driver should be a subclass of drivers.driver.Driver')
        self.driver = server_driver

    def upload(self, local_filename, remote_filename=None):
        """Upload a file to a cloud

        Args:
            filename: the filename of the local file to be uploaded
        """
        if remote_filename is None:
            remote_filename = ntpath.basename(local_filename)
        self.driver.upload(local_filename=local_filename,
                           remote_filename=remote_filename)

    def upload_dir(self, local_dir, remote_dir):
        """Upload all files from a local dir to a remote dir.

        Note it is not done recursively, so subdirectories will not
        be uploaded.
        """
        filename_list = [os.path.join(local_dir, base) for base in os.listdir(local_dir)]
        for base in os.listdir(local_dir):
            local_filename = os.path.join(local_dir, base)
            if remote_dir[-1] != '/':
                remote_dir += '/'
            remote_filename = remote_dir + base
            self.upload(local_filename=local_filename, remote_filename=remote_filename)

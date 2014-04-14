from benchcloud.drivers import driver
import ntpath


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

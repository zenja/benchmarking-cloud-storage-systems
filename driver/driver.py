import os
from ConfigParser import SafeConfigParser

class Driver(object):
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        config_filename = "drivers.conf"
        self.config_path = os.path.join(self.base_path, config_filename)
        if os.path.exists(self.config_path):
            try:
                self.parser = SafeConfigParser()
                self.parser.read(self.config_path)
            except IOError:
                print "ERROR opening config file: {}".format(config_filename)
                sys.exit(1)
        else:
            print "ERROR: config.ini not found! Exiting!"
            sys.exit(1)

    def acquire_access_token(self, guest=False):
        pass

    def connect(self, include_guest=False):
        pass

    def download(self, remote_filename, local_filename):
        pass

    def upload(self, local_filename, remote_filename):
        pass

    def share(self, host_filename, guest_filename):
        pass

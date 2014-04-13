import os
import ntpath

from mega import Mega

from driver import Driver

class MegaDriver(Driver):
    def __init__(self, verbose=True):
        super(MegaDriver, self).__init__()
        # add the verbose option for print output on some functions
        self.mega = Mega({'verbose': verbose})

    def acquire_access_token(self, guest=False):
        email = raw_input('Enter your account email: ').strip()
        password = raw_input('Enter your account password: ').strip()
        self.parser.set('mega', 'email', email)
        self.parser.set('mega', 'password', password)
        with open(self.config_path, "w") as f:
            self.parser.write(f)

    def connect(self, include_guest=False):
        email = self.parser.get("mega", "email")
        password = self.parser.get("mega", "password")
        self.mega_service = self.mega.login(email, password)

    def download(self, remote_filename, local_filename=None):
        mega_file = self.mega_service.find(remote_filename)
        if local_filename:
            local_dir = os.path.dirname(local_filename)
            local_file_basename = ntpath.basename(local_filename)
            return self.mega_service.download(mega_file, local_dir, local_file_basename)
        else:
            self.mega_service.download(mega_file)

    def upload(self, local_filename, remote_filename=None):
        """upload a local file to Mega

        Args:
            local_filename: local file name
            remote_filename: not used here because of interface
        """
        return self.mega_service.upload(local_filename)

    def share(self, host_filename, guest_filename):
        raise NotImplementedError()


if __name__ == '__main__':
    mega = MegaDriver()
    mega.connect()
    print mega.download(remote_filename='test.txt', local_filename='./test-download.txt')
    #print mega.upload(local_filename="./test.txt")
